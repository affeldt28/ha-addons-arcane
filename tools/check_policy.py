"""Check access boundaries and the endpoint policy, including bypass cases."""
import json
import re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
proxy = json.loads((root/'arcane_docker_proxy/config.json').read_text())
agent = json.loads((root/'arcane_edge_agent/config.json').read_text())
env = proxy['environment']
assert proxy['docker_api'] is True
assert not agent.get('docker_api') and not agent.get('hassio_api')
assert not agent.get('host_network') and not proxy.get('host_network')
assert not proxy.get('ports') and not agent.get('ports')
assert all(m['type'] == 'data' for m in agent['map'])
assert {k for k in env if k.startswith('SP_ALLOW_')} == {'SP_ALLOW_GET', 'SP_ALLOW_HEAD'}
assert set(proxy['options']) == {'SP_ALLOWFROM'}
CASES = [
 ('GET','/_ping',True), ('HEAD','/v1.51/_ping',True),
 ('GET','/containers/json',True), ('GET','/v1.51/containers/abc/stats',True),
 ('GET','/containers/abc/logs',True), ('GET','/images/sha256:abc/json',True),
 ('GET','/events',True), ('GET','/networks',True), ('GET','/volumes',True),
 ('POST','/containers/create',False), ('POST','/containers/abc/restart',False),
 ('DELETE','/containers/abc',False), ('POST','/containers/abc/exec',False),
 ('GET','/containers/abc/archive',False), ('GET','/containers/abc/export',False),
 ('GET','/images/get',False), ('GET','/containers/abc/attach/ws',False),
 ('PUT','/containers/abc/archive',False), ('GET','/secrets',False),
 ('GET','/containers/../archive',False), ('GET','//containers/json',False),
 ('GET','/containers%2fabc%2farchive',False), ('CONNECT','/containers/json',False),
 ('POST','/volumes/prune',False), ('GET','/containers/json/extra',False),
]
for method,path,expected in CASES:
    actual = bool(re.fullmatch(env.get('SP_ALLOW_'+method, r'(?!)'), path))
    assert actual == expected, (method,path,actual,expected)
if __name__ == '__main__':
    print(f'Configuration boundaries and {len(CASES)} access-policy cases passed.')
