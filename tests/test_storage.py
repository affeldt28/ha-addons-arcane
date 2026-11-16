"""Exercise the real storage blocks without Docker or a host Docker socket."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class StorageTests(unittest.TestCase):
    def test_migrate_reinstall_and_replace_settings(self):
        for package, entrypoint, legacy_subdir in [
            ('arcane_edge_agent', 'run-monitor', 'arcane'),
        ]:
            with self.subTest(package=package), tempfile.TemporaryDirectory() as temp:
                base = Path(temp)
                data, config = base/'data', base/'config'
                old_state = data/legacy_subdir
                old_state.mkdir(parents=True)
                (old_state/'state').write_text('original')
                settings = dict(ARCANE_MANAGER_API_URL='https://manager.test', ARCANE_AGENT_TOKEN='secret', ARCANE_AGENT_TRANSPORT='grpc')
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
                options.write_text(json.dumps(dict(settings, ARCANE_MANAGER_API_URL='', ARCANE_AGENT_TOKEN='', ARCANE_AGENT_TRANSPORT='auto')))
                result = run()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((config/'arcane/state').read_text(), 'original')
                self.assertEqual(json.loads((config/'options.json').read_text()), settings)
                # Explicit valid changes replace saved settings; partial changes fail safely.
                changed = dict(settings, ARCANE_AGENT_TOKEN='replacement')
                options.write_text(json.dumps(changed))
                self.assertEqual(run().returncode, 0)
                self.assertEqual(json.loads((config/'options.json').read_text()), changed)
                # Legacy UI options migrate even alongside the new blank defaults.
                options.write_text(json.dumps(dict(
                    MANAGER_API_URL=r'https\://manager.test', AGENT_TOKEN='old', EDGE_TRANSPORT='poll',
                    ARCANE_MANAGER_API_URL='', ARCANE_AGENT_TOKEN='', ARCANE_AGENT_TRANSPORT='auto')))
                result = run()
                self.assertEqual(result.returncode, 0, result.stderr)
                migrated = dict(ARCANE_MANAGER_API_URL='https://manager.test', ARCANE_AGENT_TOKEN='old', ARCANE_AGENT_TRANSPORT='auto')
                self.assertEqual(json.loads((config/'options.json').read_text()), migrated)
                options.write_text(json.dumps(dict(changed, MANAGER_API_URL='https://stale.test', AGENT_TOKEN='stale', EDGE_TRANSPORT='poll')))
                self.assertEqual(run().returncode, 0)
                self.assertEqual(json.loads((config/'options.json').read_text()), changed)
                # Explicit unsupported Arcane 3 transport still fails safely.
                for unsupported in [
                    dict(changed, ARCANE_AGENT_TRANSPORT='poll'),
                ]:
                    options.write_text(json.dumps(unsupported))
                    self.assertNotEqual(run().returncode, 0)
                    self.assertEqual(json.loads((config/'options.json').read_text()), changed)
                options.write_text(json.dumps(dict(changed, ARCANE_AGENT_TOKEN='')))
                self.assertNotEqual(run().returncode, 0)
                self.assertEqual(json.loads((config/'options.json').read_text()), changed)

    def test_ui_save_success_failure_and_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            data, config, tools = base/'data', base/'config', base/'tools'
            data.mkdir()
            tools.mkdir()
            original = dict(MANAGER_API_URL='https://manager.test', AGENT_TOKEN='fixture', EDGE_TRANSPORT='poll')
            (data/'options.json').write_text(json.dumps(original))
            source = (ROOT/'arcane_edge_agent/rootfs/usr/local/bin/run-monitor').read_text()
            block = source.split('# Use saved pairing settings', 1)[1].split('\n', 1)[1].split('[ -S ', 1)[0]
            script = ('set -eu\nfail() { exit 1; }\n' + block).replace('/config', str(config)).replace('/data', str(data))
            wget = tools/'wget'
            wget.write_text('''#!/bin/sh
set -eu
for arg in "$@"; do
    case "$arg" in
        --post-file=*) cp "${arg#*=}" "$CAPTURE" ;;
    esac
done
if [ "$SAVE_FAIL" = yes ]; then exit 1; fi
while [ "$#" -gt 0 ]; do
    if [ "$1" = -O ]; then shift; printf '%s' '{"result":"ok"}' > "$1"; fi
    shift
done
''')
            wget.chmod(0o755)
            capture = base/'request.json'
            env = dict(os.environ, PATH=str(tools)+os.pathsep+os.environ['PATH'],
                       SUPERVISOR_TOKEN='fixture-supervisor-token', CAPTURE=str(capture), SAVE_FAIL='yes')
            failed = subprocess.run(['sh', '-c', script], env=env, text=True, capture_output=True)
            self.assertEqual(failed.returncode, 0, failed.stderr)
            self.assertIn('WARNING', failed.stderr)
            self.assertEqual(json.loads((data/'options.json').read_text()), original)
            env['SAVE_FAIL'] = 'no'
            saved = subprocess.run(['sh', '-c', script], env=env, text=True, capture_output=True)
            self.assertEqual(saved.returncode, 0, saved.stderr)
            self.assertIn('Saved migrated', saved.stdout)
            options = json.loads(capture.read_text())['options']
            self.assertEqual(options, dict(ARCANE_MANAGER_API_URL='https://manager.test', ARCANE_AGENT_TOKEN='fixture', ARCANE_AGENT_TRANSPORT='auto'))
            self.assertNotIn('fixture-supervisor-token', saved.stdout+saved.stderr)
            (data/'options.json').write_text(json.dumps(options))
            capture.unlink()
            self.assertEqual(subprocess.run(['sh', '-c', script], env=env, capture_output=True).returncode, 0)
            self.assertFalse(capture.exists(), 'Already migrated settings must not be posted again')


if __name__ == '__main__':
    unittest.main()
