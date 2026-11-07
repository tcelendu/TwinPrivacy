# SPDX-License-Identifier: MIT
"""Tests for conditional information, verification and patient report output."""
import copy
import json
import math
import unittest
from pathlib import Path

from privacy_engine import analyze_scenario, verify_analysis
from patient_report import render_patient_report

ROOT = Path(__file__).resolve().parent


def example():
    return json.loads((ROOT/'examples'/'privacy_verification_scenario.json').read_text(encoding='utf-8'))


class WeightedDisclosureTests(unittest.TestCase):
    def test_repeated_fact_yields_zero_information(self):
        report = analyze_scenario(example())
        self.assertEqual(0, report['events'][1]['incremental_information_bits'])
        self.assertEqual(report['events'][0]['cumulative_information_bits'],
                         report['events'][1]['cumulative_information_bits'])

    def test_cross_attribute_inference_detected(self):
        first = analyze_scenario(example())['events'][0]
        shift = next(x for x in first['model_implied_probability_shifts']
                     if x['attribute'] == 'chronic_kidney_disease')
        self.assertGreater(shift['probability_after'], shift['probability_before'])

    def test_recipient_specific_baseline(self):
        report = analyze_scenario(example())
        self.assertEqual(0, report['events'][-1]['incremental_information_bits'])
        self.assertGreater(report['events'][0]['incremental_information_bits'], 1.0)

    def test_preference_review_flags(self):
        report = analyze_scenario(example())
        self.assertEqual('review', report['events'][3]['preference_status'])
        self.assertIn('chronic_kidney_disease', report['events'][3]['attributes_outside_preferences'])
        self.assertEqual('review', report['events'][6]['preference_status'])

    def test_receipt_chain_and_anchor(self):
        report = analyze_scenario(example())
        self.assertTrue(verify_analysis(report))
        self.assertTrue(verify_analysis(report, report['final_receipt_sha256']))
        self.assertFalse(verify_analysis(report, 'x' * 64))

    def test_unauthorized_event_mutation_detected(self):
        report = analyze_scenario(example())
        report['events'][2]['purpose'] = 'altered'
        self.assertFalse(verify_analysis(report))

    def test_modified_model_invalidates_receipt(self):
        report = analyze_scenario(example())
        report['analysis_context']['population_model'][0]['weight'] += .002
        self.assertFalse(verify_analysis(report))

    def test_both_receipt_deletion_and_reordering_detected(self):
        report = analyze_scenario(example())
        altered = copy.deepcopy(report)
        altered['events'].pop(3)
        self.assertFalse(verify_analysis(altered))
        altered = copy.deepcopy(report)
        altered['events'][0], altered['events'][1] = altered['events'][1], altered['events'][0]
        self.assertFalse(verify_analysis(altered))

    def test_unrecognized_field_rejected(self):
        scenario = example()
        scenario['releases'][0]['facts']['patient_name'] = 'Person X'
        with self.assertRaises(ValueError):
            analyze_scenario(scenario)

    def test_contradictory_input_rejected(self):
        scenario = example()
        scenario['releases'][0]['facts']['diabetes'] = False
        with self.assertRaises(ValueError):
            analyze_scenario(scenario)

    def test_duplicate_state_rejected(self):
        scenario = example()
        scenario['population_model'].append(copy.deepcopy(scenario['population_model'][0]))
        with self.assertRaises(ValueError):
            analyze_scenario(scenario)

    def test_entropy_is_finite(self):
        report = analyze_scenario(example())
        for event in report['events']:
            self.assertTrue(math.isfinite(event['posterior_entropy_after_bits']))
            self.assertGreaterEqual(event['incremental_information_bits'], 0)

    def test_patient_statement_contains_necessary_sections(self):
        report = analyze_scenario(example())
        html = render_patient_report(report, report['final_receipt_sha256'])
        self.assertIn('Your health-information disclosure record', html)
        self.assertIn('Potential inference', html)
        self.assertIn('Outside recorded sharing preferences', html)
        self.assertIn('PASS', html)

    def test_patient_statement_escapes_external_strings(self):
        scenario = example()
        scenario['releases'][0]['purpose'] = '<script>doBadThings()</script>'
        html = render_patient_report(analyze_scenario(scenario))
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_invalid_preferences_rejected(self):
        scenario = example()
        scenario['recipient_preferences']['research_analytics'].append('unknown')
        with self.assertRaises(ValueError):
            analyze_scenario(scenario)

if __name__ == '__main__':
    unittest.main()
