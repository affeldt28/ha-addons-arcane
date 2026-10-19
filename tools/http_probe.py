"""Read a complete HTTP response from a subprocess without closing its stdin early."""
import http.client
import subprocess
import threading


class _ResponseStream:
    def __init__(self, stream):
        self.stream = stream

    def makefile(self, *_args, **_kwargs):
        return self.stream


def request_http(command, method, path, timeout=8):
    """Keep the connection's write side open until HTTP framing says it is complete."""
    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    deadline = threading.Timer(timeout, process.kill)
    deadline.start()
    try:
        request = (f'{method} {path} HTTP/1.1\r\n'
                   'Host: localhost\r\nConnection: close\r\n\r\n')
        process.stdin.write(request.encode('ascii'))
        process.stdin.flush()
        response = http.client.HTTPResponse(_ResponseStream(process.stdout), method=method)
        response.begin()
        status = response.status
        response.read()
        response.close()
    finally:
        try:
            process.stdin.close()
        except BrokenPipeError:
            pass
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        deadline.cancel()
    if process.returncode:
        raise subprocess.CalledProcessError(process.returncode, command,
                                            stderr=process.stderr.read())
    return status
