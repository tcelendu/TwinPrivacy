# SPDX-License-Identifier: MIT
"""Verify file-level licence metadata for public-repository source materials."""
from __future__ import annotations
import unittest
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDE = {'__pycache__', '.git', '.pytest_cache', '.venv'}
ALLOWED = {'MIT', 'CC0-1.0', 'CC-BY-4.0'}


class RepositoryLicensingTests(unittest.TestCase):
    def test_each_released_file_has_valid_spdx_identifier(self) -> None:
        checked = 0
        for path in ROOT.rglob('*'):
            if not path.is_file() or any(x in EXCLUDE for x in path.parts):
                continue
            if path.name.endswith('.license'):
                continue
            contents = path.read_text(encoding='utf-8')
            sidecar = path.with_name(path.name + '.license')
            pattern = r'^\s*(?:#\s*|<!--\s*)?SPDX-License-Identifier:\s*(MIT|CC0-1.0|CC-BY-4.0)(?:\s*-->)?\s*$'
            matches = re.findall(pattern, contents[:500], flags=re.MULTILINE)
            if not matches and sidecar.exists():
                matches = re.findall(pattern, sidecar.read_text(encoding='utf-8'), flags=re.MULTILINE)
            self.assertTrue(matches, f'Missing SPDX identifier for {path.relative_to(ROOT)}')
            self.assertIn(matches[0], ALLOWED, f'Unknown licence for {path.relative_to(ROOT)}')
            checked += 1
        self.assertGreaterEqual(checked, 40)


if __name__ == '__main__':
    unittest.main()
