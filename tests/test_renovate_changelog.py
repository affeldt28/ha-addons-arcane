import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    'renovate_changelog',
    Path(__file__).resolve().parents[1] / '.github/scripts/renovate_changelog.py',
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ChangelogTests(unittest.TestCase):
    def test_prepend_preserves_history_and_links(self):
        original = '# Changelog\n\n[Releases](https://example.com)\n\n## 3.0.1-1\n\n- Old note.\n'
        result = module.update_changelog(original, '3.0.2-1', ['Update Arcane.'])
        self.assertIn('## 3.0.2-1\n\n- Update Arcane.\n\n## 3.0.1-1', result)
        self.assertTrue(result.endswith('## 3.0.1-1\n\n- Old note.\n'))
        self.assertEqual(module.update_changelog(result, '3.0.2-1', ['Other note.']), result)

    def test_existing_manual_release_notes_are_preserved(self):
        original = '# Changelog\n\n## 3.0.2-1\n\n- Breaking migration instructions.\n'
        self.assertEqual(module.update_changelog(original, '3.0.2-1', ['Update.']), original)

    def test_manifest_version(self):
        self.assertEqual(module.version('name: Agent\nversion: 3.0.1-2\n'), '3.0.1-2')
