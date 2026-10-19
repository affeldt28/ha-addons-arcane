"""Configure stable Home Assistant DNS names from the actual public Git URL."""
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlparse
root = Path(__file__).resolve().parents[1]
if len(sys.argv) != 2 or urlparse(sys.argv[1]).scheme != 'https':
    raise SystemExit('Usage: python3 tools/configure_repository.py https://github.com/OWNER/REPO')
url = sys.argv[1]
prefix = hashlib.sha1(url.lower().encode()).hexdigest()[:8]
def update(path, change):
    file = root / path
    data = json.loads(file.read_text())
    change(data)
    file.write_text(json.dumps(data, indent=2) + '\n')
update('repository.json', lambda d: d.update(url=url))
update('arcane_edge_agent/config.json', lambda d: d['options'].update(DOCKER_HOST=f'tcp://{prefix}-arcane-docker-proxy:2375'))
update('arcane_docker_proxy/config.json', lambda d: d['options'].update(SP_ALLOWFROM=f'{prefix}-arcane-edge-agent'))
print('Configured repository metadata and internal agent/proxy hostnames.')
