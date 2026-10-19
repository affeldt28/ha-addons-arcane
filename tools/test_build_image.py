"""Verify retry behavior without contacting registries or actually sleeping."""
import subprocess
import unittest
from unittest.mock import patch
from build_image import build_image


class BuildImageTests(unittest.TestCase):
    @patch('build_image.time.sleep')
    @patch('build_image.subprocess.check_output')
    def test_rate_limit_recovers(self, run, sleep):
        run.side_effect = [subprocess.CalledProcessError(1, [], output='429 Too Many Requests'), 'built\n']
        build_image('fixture', 'context')
        self.assertEqual(run.call_count, 2)
        sleep.assert_called_once_with(10)

    @patch('build_image.time.sleep')
    @patch('build_image.subprocess.check_output')
    def test_real_build_failure_is_not_retried(self, run, sleep):
        run.side_effect = subprocess.CalledProcessError(1, [], output='Dockerfile syntax error')
        with self.assertRaises(subprocess.CalledProcessError):
            build_image('fixture', 'context')
        self.assertEqual(run.call_count, 1)
        sleep.assert_not_called()

    @patch('build_image.time.sleep')
    @patch('build_image.subprocess.check_output')
    def test_persistent_rate_limit_still_fails(self, run, sleep):
        run.side_effect = subprocess.CalledProcessError(1, [], output='toomanyrequests')
        with self.assertRaises(subprocess.CalledProcessError):
            build_image('fixture', 'context')
        self.assertEqual(run.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [10, 30])


if __name__ == '__main__':
    unittest.main()
