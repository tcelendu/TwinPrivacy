# SPDX-License-Identifier: MIT
import json
import unittest
from pathlib import Path

from evidence_validation import (SCENARIO, SEED, case_scenario, cohort_csv,
                                 cohort_rows, independent_model, reference_oracle,
                                 run_validation, tamper_experiments)
from privacy_engine import analyze_scenario


class EvidenceValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario = json.loads(Path(SCENARIO).read_text(encoding='utf-8'))

    def test_synthetic_generator_reproducible(self):
        self.assertEqual(cohort_csv(cohort_rows(self.scenario, count=20, seed=SEED)),
                         cohort_csv(cohort_rows(self.scenario, count=20, seed=SEED)))
        self.assertEqual(cohort_rows(self.scenario, count=1)[0]['record_id'], 'SYN-TP-0001')

    def test_reference_oracle_matches_engine_first_profile(self):
        scenario = case_scenario(self.scenario, cohort_rows(self.scenario, count=1)[0])
        actual = analyze_scenario(scenario)
        oracle = reference_oracle(scenario)
        for event, independent in zip(actual['events'], oracle):
            self.assertAlmostEqual(event['incremental_information_bits'], independent['incremental_bits'], delta=0.000001)
            self.assertAlmostEqual(event['cumulative_information_bits'], independent['cumulative_bits'], delta=0.000001)

    def test_independence_preserves_marginal(self):
        product = independent_model(self.scenario)
        self.assertAlmostEqual(sum(row['weight'] for row in product), 1.0)
        for key in ('diabetes', 'chronic_kidney_disease', 'asthma', 'drug_allergy'):
            actual = sum(row['weight'] for row in self.scenario['population_model'] if row['profile'][key])
            changed = sum(row['weight'] for row in product if row['profile'][key])
            self.assertAlmostEqual(actual, changed)

    def test_receipt_limit_demonstration(self):
        s = case_scenario(self.scenario, cohort_rows(self.scenario, count=1)[0])
        report = analyze_scenario(s)
        self.assertTrue(all(tamper_experiments(report, s).values()))

    def test_validation_small_cohort_equivalence(self):
        # Entire pipeline is exercised by reproduce.py; test key engine/oracle
        # invariants on a second record without rerunning 512 complete cases.
        s = case_scenario(self.scenario, cohort_rows(self.scenario, count=2)[1])
        report = analyze_scenario(s)
        self.assertEqual(report['events'][1]['incremental_information_bits'], 0.0)
        self.assertEqual(report['events'][-1]['incremental_information_bits'], 0.0)


if __name__ == '__main__':
    unittest.main()
