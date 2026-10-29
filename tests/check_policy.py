"""Validate the two access modes and the monitoring endpoint boundary."""
import json
import re
import yaml
from pathlib import Path
root = Path(__file__).resolve().parents[1]
monitor = yaml.safe_load((root/'arcane_edge_agent/config.yaml').read_text())
full = yaml.safe_load((root/'arcane_edge_agent_full/config.yaml').read_text())
policy = json.loads((root/'arcane_edge_agent/rootfs/etc/arcane-monitor/policy.json').read_text())
assert set(p.parent.name for p in root.glob('*/config.yaml')) == {'arcane_edge_agent','arcane_edge_agent_full'}
assert monitor['docker_api'] and full['docker_api']
assert set(policy) == {'GET','HEAD'}
assert 'image' not in monitor and 'DOCKER_HOST' not in monitor['options']
assert 'image' not in full
full_dockerfile = (root/'arcane_edge_agent_full/Dockerfile').read_text()
assert 'ARG BUILD_FROM=ghcr.io/getarcaneapp/agent:v2.17.1' in full_dockerfile
assert 'FROM ${BUILD_FROM}' in full_dockerfile
assert full['legacy'] is True
assert full['environment']['DOCKER_HOST'] == 'unix:///run/docker.sock'
assert 'Full Access' in full['name'] and 'WARNING' in full['description']
for cfg in [monitor,full]:
    expected_map = {'type': 'addon_config', 'read_only': False}
    if cfg is full:
        expected_map['path'] = '/app/data'
    assert cfg['map'] == [expected_map]
    assert not cfg.get('ports') and not cfg.get('host_network')
    assert not cfg.get('hassio_api') and not cfg.get('full_access')
    assert cfg['boot'] == 'manual'
    assert set(cfg['options']) == set(cfg['schema']) == {'MANAGER_API_URL','AGENT_TOKEN','EDGE_TRANSPORT'}
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
 ('POST','/v1.51/containers/abc/stop',False), ('PATCH','/containers/abc',False),
 ('GET','/v1.51/images/abc/get',False), ('HEAD','/containers/abc/json',False),
]
for method,path,expected in CASES:
    actual = bool(re.fullmatch(policy.get(method, r'(?!)'),path))
    assert actual == expected, (method,path,actual,expected)
if __name__ == '__main__':
    print(f'Two add-on definitions and {len(CASES)} monitoring access-policy cases passed.')
