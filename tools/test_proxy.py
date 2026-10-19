"""Exercise the packaged monitor proxy with a fake socket, never the host socket."""
import http.server
import http.client
import json
import os
import socketserver
import subprocess
import tempfile
import sys
import threading
import time
import uuid
from pathlib import Path
from check_policy import CASES, root, policy
from http_probe import request_http

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
            # Keep stdin open while reading: piping printf into BusyBox nc can
            # close the connection before the proxy/fake Docker server responds.
            return request_http(['docker','exec','-i',container,'su-exec','65532:65532',
                                 'nc','-w','5','127.0.0.1','2375'], method, path)
        for attempt in range(30):
            try:
                if request('GET','/_ping') == 200:
                    break
            except (subprocess.CalledProcessError,http.client.HTTPException,OSError):
                pass
            time.sleep(.1)
        else:
            raise AssertionError(f'Proxy did not become ready: {docker("logs",container)}')
        for method,path,allowed in CASES + [('GET','/containers/json?all=1',True),('GET','/containers/abc/archive?path=/etc',False)]:
            before = len(forwarded)
            status = request(method,path)
            # Unsupported HTTP methods are 405; blocked paths on allowed methods are 403.
            expected = 200 if allowed else (403 if method in policy else 405)
            assert status == expected, (method,path,status,expected)
            assert len(forwarded) == before + int(allowed), (method,path,'unexpected forwarding')
        print('Actual loopback proxy enforced the monitoring policy; agent user cannot open real socket.')
    finally:
        docker('rm','-f',container)
    # Exercise the actual entrypoint, not only the proxy: catches clean-PATH launch failures.
    data = Path(temp)/'data'
    data.mkdir()
    (data/'options.json').write_text(json.dumps({'MANAGER_API_URL':'http://invalid.test','AGENT_TOKEN':'fixture','EDGE_TRANSPORT':'poll'}))
    fake_agent = Path(temp)/'fake-agent'
    fake_agent.write_text("""#!/bin/sh
set -eu
[ "$(id -u)" = 65532 ]
[ "$(id -G)" = 65532 ]
[ "$DOCKER_HOST" = tcp://127.0.0.1:2375 ]
[ "${SUPERVISOR_TOKEN-unset}" = unset ]
test ! -w /var/run/docker.sock
printf 'ENTRYPOINT_TEST_AGENT_STARTED\\n'
exec sleep 300
""")
    os.chmod(fake_agent,0o755)
    started = docker('run','-d','--init',
        '-e','SUPERVISOR_TOKEN=must-not-reach-agent',
        '-v',f'{fake_socket}:/var/run/docker.sock:ro',
        '-v',f'{data}:/data', '-v',f'{fake_agent}:/app/arcane-agent:ro', image)
    try:
        for attempt in range(60):
            logs = docker('logs',started)
            if 'ENTRYPOINT_TEST_AGENT_STARTED' in logs:
                break
            if docker('inspect','--format','{{.State.Running}}',started) != 'true':
                raise AssertionError(f'Monitor entrypoint exited before agent startup: {logs}')
            time.sleep(.1)
        else:
            raise AssertionError(f'Monitor entrypoint never launched agent: {docker("logs",started)}')
        assert 'Connection refused' not in logs, logs
        docker('stop','-t','15',started)
        assert docker('inspect','--format','{{.State.ExitCode}}',started) == '0'
        print('Actual monitor entrypoint launches the agent unprivileged and stops cleanly.')
    finally:
        docker('rm','-f',started)
        # The entrypoint owns its state as UID 65532; remove only this fake test state.
        docker('run','--rm','--entrypoint','/bin/sh','-v',f'{data}:/fixture',
               image,'-c','rm -rf /fixture/arcane')
    # Create the insecure socket on a native Linux volume: Docker Desktop can
    # virtualize permissions on host-mounted Unix sockets, hiding chmod changes.
    volume = 'arcane-guard-test-' + uuid.uuid4().hex
    docker('volume','create',volume)
    fixture = None
    guarded = None
    try:
        fixture = docker('run','-d','--entrypoint','/usr/local/bin/socket-proxy',
            '-v',f'{fake_socket}:/var/run/docker.sock:ro', '-v',f'{volume}:/fixture', image,
            '-proxysocketendpoint=/fixture/docker.sock',
            '-proxysocketendpointfilemode=0666')
        for attempt in range(30):
            probe = subprocess.run(['docker','exec',fixture,'test','-S','/fixture/docker.sock'])
            if probe.returncode == 0:
                break
            time.sleep(.1)
        else:
            raise AssertionError(f'Guard fixture not ready: {docker("logs",fixture)}')
        guarded = docker('create','-v',f'{volume}:/var/run:ro','-v',f'{data}:/data',image)
        docker('start',guarded)
        for attempt in range(50):
            if docker('inspect','--format','{{.State.Running}}',guarded) == 'false':
                break
            time.sleep(.1)
        else:
            raise AssertionError(f'Guard did not reject accessible socket: {docker("logs",guarded)}')
        logs = docker('logs',guarded)
        assert docker('inspect','--format','{{.State.ExitCode}}',guarded) != '0'
        assert 'socket is accessible to the agent user' in logs, logs
        print('Startup guard refuses a Docker socket accessible to the agent user.')
    finally:
        if guarded:
            docker('rm','-f',guarded)
        if fixture:
            docker('rm','-f',fixture)
        docker('volume','rm',volume)
    server.shutdown()
    server.server_close()
