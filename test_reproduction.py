# SPDX-License-Identifier: MIT
"""End-to-end tests for deterministic report generation."""
import json
import tempfile
import unittest
from pathlib import Path
from reproduce import build_outputs
from privacy_engine import verify_analysis


class ReproductionTests(unittest.TestCase):
    def test_rebuild_writes_expected_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            manifest = build_outputs(output, validate=False)
            self.assertEqual(8, manifest['disclosure_events'])
            for name in ['enhanced_analysis.json', 'patient_disclosure_statement.html',
                         'trusted_receipt_anchor.txt', 'reproduction_manifest.json',
                         'reference_disclosure_report.json', 'clinical_case_results.json']:
                self.assertTrue((output / name).is_file(), name)
            report = json.loads((output / 'enhanced_analysis.json').read_text(encoding='utf-8'))
            anchor = (output / 'trusted_receipt_anchor.txt').read_text(encoding='utf-8').strip()
            self.assertTrue(verify_analysis(report, anchor))

    def test_reproducing_twice_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as temp:
            a, b = Path(temp) / 'run_a', Path(temp) / 'run_b'
            build_outputs(a, validate=False)
            build_outputs(b, validate=False)
            for item in a.iterdir():
                self.assertEqual(item.read_bytes(), (b / item.name).read_bytes(), item.name)


if __name__ == '__main__':
    unittest.main()
