"""Optionally set the public repository homepage; no hostname wiring is needed."""
import json
import sys
from pathlib import Path
from urllib.parse import urlparse
root = Path(__file__).resolve().parents[1]
if len(sys.argv) != 2 or urlparse(sys.argv[1]).scheme != 'https' or not urlparse(sys.argv[1]).netloc:
    raise SystemExit('Usage: python3 tools/configure_repository.py https://github.com/OWNER/REPO')
file = root / 'repository.json'
data = json.loads(file.read_text())
data['url'] = sys.argv[1]
file.write_text(json.dumps(data, indent=2) + '\n')
for config in root.glob('*/config.json'):
    addon = json.loads(config.read_text())
    addon['url'] = sys.argv[1]
    config.write_text(json.dumps(addon, indent=2) + '\n')
print('Configured repository and add-on homepages. No hostname wiring is needed.')
