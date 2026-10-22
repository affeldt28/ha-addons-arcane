"""Exercise the real storage blocks without Docker or a host Docker socket."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class StorageTests(unittest.TestCase):
    def test_migrate_reinstall_and_replace_settings(self):
        for package, entrypoint, legacy_subdir in [
            ('arcane_edge_agent', 'run-monitor', 'arcane'),
            ('arcane_edge_agent_full', 'run-full', ''),
        ]:
            with self.subTest(package=package), tempfile.TemporaryDirectory() as temp:
                base = Path(temp)
                data, config = base/'data', base/'config'
                old_state = data/legacy_subdir
                old_state.mkdir(parents=True)
                (old_state/'state').write_text('original')
                settings = dict(MANAGER_API_URL='https://manager.test', AGENT_TOKEN='secret', EDGE_TRANSPORT='grpc')
                options = data/'options.json'
                options.write_text(json.dumps(settings))
                source = (ROOT/package/'rootfs/usr/local/bin'/entrypoint).read_text()
                options_block = source.split('# Use saved pairing settings', 1)[1].split('\n', 1)[1].split('[ -S ', 1)[0]
                migration = source.split('# Copy old state once,', 1)[1].split('\nfi', 1)[0]
                migration = migration[migration.index('\nif '):] + '\nfi\n'
                script = 'set -eu\nfail() { echo "$*" >&2; exit 1; }\n' + options_block + migration
                script = script.replace('/config', str(config)).replace('/data', str(data))

                def run():
                    return subprocess.run(['sh', '-c', script], text=True, capture_output=True)

                result = run()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((config/'arcane/state').read_text(), 'original')
                self.assertEqual(json.loads((config/'options.json').read_text()), settings)
                self.assertEqual((config/'options.json').stat().st_mode & 0o777, 0o600)
                # Retained state wins over old private state, and blank defaults reuse pairing.
                (old_state/'state').write_text('stale')
                options.write_text(json.dumps(dict(settings, MANAGER_API_URL='', AGENT_TOKEN='', EDGE_TRANSPORT='poll')))
                result = run()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((config/'arcane/state').read_text(), 'original')
                self.assertEqual(json.loads((config/'options.json').read_text()), settings)
                # Explicit valid changes replace saved settings; partial changes fail safely.
                changed = dict(settings, AGENT_TOKEN='replacement')
                options.write_text(json.dumps(changed))
                self.assertEqual(run().returncode, 0)
                self.assertEqual(json.loads((config/'options.json').read_text()), changed)
                options.write_text(json.dumps(dict(changed, AGENT_TOKEN='')))
                self.assertNotEqual(run().returncode, 0)
                self.assertEqual(json.loads((config/'options.json').read_text()), changed)


if __name__ == '__main__':
    unittest.main()
