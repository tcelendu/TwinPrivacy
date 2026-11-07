# SPDX-License-Identifier: MIT
"""Reproducibility and integrity checks for case-based analyses."""
import json
import unittest
from pathlib import Path
from case_series import run_cases
from twinprivacy import verify_receipt_chain

ROOT = Path(__file__).resolve().parent

class ClinicalCaseAnalysesTests(unittest.TestCase):
    def test_case_series_matches_preserved_results(self):
        observed = run_cases()
        stored = json.loads((ROOT / "examples" / "clinical_case_results.json").read_text())
        self.assertEqual(observed, stored)
        self.assertEqual(len(observed["analyses"]), 3)

    def test_all_case_receipts_verify(self):
        for case in run_cases()["analyses"]:
            with self.subTest(case=case["case_id"]):
                self.assertTrue(verify_receipt_chain(case))

    def test_repeated_disclosures_yield_zero_additional_bits(self):
        analyses = run_cases()["analyses"]
        by_id = {case["case_id"]: case for case in analyses}
        self.assertEqual(0.0, by_id["TP-CL-01"]["events"][1]["incremental_information_bits"])
        self.assertEqual(0.0, by_id["TP-CL-02"]["events"][5]["incremental_information_bits"])
        self.assertEqual(0.0, by_id["TP-CL-03"]["events"][5]["incremental_information_bits"])

if __name__ == "__main__":
    unittest.main()
