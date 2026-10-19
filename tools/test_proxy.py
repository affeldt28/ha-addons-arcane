"""Exercise the packaged monitor proxy with a fake socket, never the host socket."""
import http.server
import os
import socketserver
import subprocess
import tempfile
import sys
import threading
import time
from pathlib import Path
from check_policy import CASES, root

def docker(*args):
    try:
        return subprocess.check_output(['docker',*args],text=True,stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as error:
        print(error.output, file=sys.stderr)
        raise

forwarded = []
class FakeDocker(http.server.BaseHTTPRequestHandler):
    def answer(self):
        forwarded.append((self.command,self.path))
        self.send_response(200)
        self.send_header('Content-Length','2')
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(b'{}')
    do_GET = do_HEAD = do_POST = do_PUT = do_PATCH = do_DELETE = do_CONNECT = answer
    def log_message(self,*_):
        pass
class UnixHTTP(socketserver.ThreadingMixIn,socketserver.UnixStreamServer):
    daemon_threads = True

image = 'arcane-monitor-test:local'
docker('build','-t',image,str(root/'arcane_edge_agent'))
with tempfile.TemporaryDirectory() as temp:
    fake_socket = Path(temp)/'docker.sock'
    server = UnixHTTP(str(fake_socket),FakeDocker)
    os.chmod(fake_socket,0o600)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    container = docker('run','-d','--entrypoint','/bin/sh',
        '-v',f'{fake_socket}:/var/run/docker.sock:ro',image,'-c',
        'exec env -i PATH=/usr/local/bin:/usr/bin:/bin /usr/local/bin/socket-proxy '
        '-listenip=127.0.0.1 -allowfrom=127.0.0.1/32 '
        '"-allowGET=$(jq -r .GET /etc/arcane-monitor/policy.json)" '
        '"-allowHEAD=$(jq -r .HEAD /etc/arcane-monitor/policy.json)"')
    try:
        # Run clients under exactly the same user/group as the actual monitor agent.
        docker('exec',container,'su-exec','65532:65532','sh','-c',
               'test ! -w /var/run/docker.sock && test "$(id -G)" = 65532 && '
               'test "$(awk \'/^CapEff:/ {print $2}\' /proc/self/status)" = 0000000000000000')
        def request(method,path):
            raw = docker('exec',container,'su-exec','65532:65532','sh','-c',
                'printf "%s %s HTTP/1.0\\r\\nHost: localhost\\r\\nConnection: close\\r\\n\\r\\n" '
                '"$1" "$2" | nc -w 2 127.0.0.1 2375','client',method,path)
            return int(raw.splitlines()[0].split()[1])
        for attempt in range(30):
            try:
                if request('GET','/_ping') == 200:
                    break
            except (subprocess.CalledProcessError,IndexError,ValueError):
                pass
            time.sleep(.1)
        else:
            raise AssertionError('Proxy did not become ready')
        for method,path,allowed in CASES + [('GET','/containers/json?all=1',True),('GET','/containers/abc/archive?path=/etc',False)]:
            before = len(forwarded)
            status = request(method,path)
            assert status == (200 if allowed else 403), (method,path,status)
            assert len(forwarded) == before + int(allowed), (method,path,'unexpected forwarding')
        print('Actual loopback proxy enforced the monitoring policy; agent user cannot open real socket.')
    finally:
        docker('rm','-f',container)
    # Verify the real startup guard rejects a socket the unprivileged agent could access.
    import json
    data = Path(temp)/'data'
    data.mkdir()
    (data/'options.json').write_text(json.dumps({'MANAGER_API_URL':'http://invalid.test','AGENT_TOKEN':'fixture','EDGE_TRANSPORT':'poll'}))
    os.chmod(fake_socket,0o666)
    result = subprocess.run(['docker','run','--rm','-v',f'{fake_socket}:/var/run/docker.sock:ro',
        '-v',f'{data}:/data',image],capture_output=True,text=True,timeout=15)
    assert result.returncode != 0 and 'socket is accessible to the agent user' in result.stderr, result
    print('Startup guard refuses a Docker socket accessible to the agent user.')
    server.shutdown()
    server.server_close()
