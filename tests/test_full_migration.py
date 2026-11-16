"""Exercise Full Access option migration without Docker or exposing credentials."""
import os
from pathlib import Path
import subprocess
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'arcane_edge_agent_full/rootfs/usr/local/bin/run-full'


class FullMigrationTests(unittest.TestCase):
    def run_wrapper(self, **options):
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(('ARCANE_', 'EDGE_')) and key not in ('MANAGER_API_URL', 'AGENT_TOKEN')}
        env.pop('SUPERVISOR_TOKEN', None)
        env.pop('HASSIO_TOKEN', None)
        env.update(options)
        return subprocess.run(['sh', str(SCRIPT), 'sh', '-c', '''
            printf '%s\\n' "$ARCANE_MANAGER_API_URL" "$ARCANE_AGENT_TOKEN" "$ARCANE_AGENT_TRANSPORT"
            test "${MANAGER_API_URL-unset}" = unset
            test "${AGENT_TOKEN-unset}" = unset
            test "${EDGE_TRANSPORT-unset}" = unset
            test "${SUPERVISOR_TOKEN-unset}" = unset
            test "${HASSIO_TOKEN-unset}" = unset
        '''], env=env, text=True, capture_output=True)

    def test_legacy_ui_options_and_blank_defaults(self):
        result = self.run_wrapper(MANAGER_API_URL=r'https\://manager.test', AGENT_TOKEN='fixture', EDGE_TRANSPORT='poll',
                                  ARCANE_MANAGER_API_URL='', ARCANE_AGENT_TOKEN='', ARCANE_AGENT_TRANSPORT='auto')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ['https://manager.test', 'fixture', 'auto'])

    def test_explicit_new_settings_win(self):
        result = self.run_wrapper(MANAGER_API_URL='https://old.test', AGENT_TOKEN='old', EDGE_TRANSPORT='poll',
                                  ARCANE_MANAGER_API_URL='https://new.test', ARCANE_AGENT_TOKEN='new', ARCANE_AGENT_TRANSPORT='grpc')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ['https://new.test', 'new', 'grpc'])
