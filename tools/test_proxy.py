"""Exercise the packaged proxy against a fake Unix Docker socket, never the host socket."""
import http.client
import http.server
import json
import socketserver
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from check_policy import CASES, root, proxy

def docker(*args):
    return subprocess.check_output(['docker', *args], text=True).strip()

class FakeDocker(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Length', '2')
        self.end_headers()
        self.wfile.write(b'{}')
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, *_):
        pass

class UnixHTTP(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True

image = 'arcane-readonly-proxy-test:local'
docker('build', '-t', image, str(root/'arcane_docker_proxy'))
with tempfile.TemporaryDirectory() as temp:
    server = UnixHTTP(str(Path(temp)/'docker.sock'), FakeDocker)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    args = ['run', '-d', '-p', '127.0.0.1::2375', '-v', f'{temp}:/fixture:ro',
            '-e', 'SP_SOCKETPATH=/fixture/docker.sock', '-e', 'SP_ALLOWFROM=0.0.0.0/0']
    for key,value in proxy['environment'].items():
        args += ['-e', f'{key}={value}']
    container = docker(*args, image)
    try:
        port = int(docker('port', container, '2375/tcp').rsplit(':',1)[1])
        def request(method,path):
            conn = http.client.HTTPConnection('127.0.0.1',port,timeout=3)
            try:
                conn.request(method,path)
                response = conn.getresponse()
                status = response.status
                response.read()
                return status
            finally:
                conn.close()
        for attempt in range(50):
            try:
                if request('GET','/_ping') == 200:
                    break
            except (OSError, http.client.HTTPException):
                pass
            time.sleep(.1)
        else:
            raise AssertionError('Proxy did not become ready')
        for method,path,allowed in CASES + [('GET','/containers/json?all=1',True),('GET','/containers/abc/archive?path=/etc',False)]:
            status = request(method,path)
            assert status == (200 if allowed else 403), (method,path,status)
        print('Actual proxy allowed monitoring requests and denied all mutation/bypass cases.')
    finally:
        docker('rm','-f',container)
        server.shutdown()
        server.server_close()
