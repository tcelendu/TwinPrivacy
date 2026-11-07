# SPDX-License-Identifier: MIT
"""Automated functional and integrity tests for TwinPrivacy."""

import copy
import unittest

from twinprivacy import (
    candidate_profiles, disclosure_report, matching_profiles,
    verify_receipt_chain,
)

PROFILE = {"diabetes": False, "asthma": True, "drug_allergy": True}


class TwinPrivacyTests(unittest.TestCase):
    def test_complete_candidate_enumeration(self):
        profiles = candidate_profiles()
        self.assertEqual(len(profiles), 8)
        self.assertEqual(len({tuple(p.items()) for p in profiles}), 8)

    def test_conditional_information_gain(self):
        releases = [
            {"recipient": "researcher", "facts": {"asthma": True}},
            {"recipient": "researcher", "facts": {"asthma": True}},
            {"recipient": "researcher", "facts": {"drug_allergy": True}},
        ]
        events = disclosure_report(releases, {}, PROFILE)["events"]
        self.assertEqual([1.0, 0.0, 1.0], [e["incremental_information_bits"] for e in events])
        self.assertEqual(2.0, events[-1]["cumulative_information_bits"])

    def test_prior_knowledge_is_accounted_for(self):
        event = disclosure_report(
            [{"recipient": "clinician", "facts": {"asthma": True}}],
            {"clinician": {"asthma": True}}, PROFILE,
        )["events"][0]
        self.assertEqual(0.0, event["incremental_information_bits"])

    def test_recipient_isolation(self):
        report = disclosure_report([
            {"recipient": "a", "facts": {"asthma": True}},
            {"recipient": "b", "facts": {"asthma": True}},
        ], {}, PROFILE)
        self.assertEqual([1.0, 1.0], [e["incremental_information_bits"] for e in report["events"]])

    def test_contradictory_disclosure_rejected(self):
        with self.assertRaises(ValueError):
            disclosure_report([{"recipient": "r", "facts": {"asthma": False}}], {}, PROFILE)

    def test_upper_bound_under_uniform_model(self):
        event = disclosure_report([{"recipient": "r", "facts": PROFILE}], {}, PROFILE)["events"][0]
        self.assertEqual(3.0, event["cumulative_information_bits"])
        self.assertEqual(1, event["remaining_candidate_profiles"])

    def test_receipt_chain_verifies(self):
        report = disclosure_report([
            {"recipient": "r", "facts": {"asthma": True}},
            {"recipient": "r", "facts": {"diabetes": False}},
        ], {}, PROFILE)
        self.assertTrue(verify_receipt_chain(report))

    def test_receipt_change_is_detected(self):
        report = disclosure_report([{"recipient": "r", "facts": {"asthma": True}}], {}, PROFILE)
        altered = copy.deepcopy(report)
        altered["events"][0]["incremental_information_bits"] = 0.0
        self.assertFalse(verify_receipt_chain(altered))

    def test_hash_chain_reordering_is_detected(self):
        report = disclosure_report([
            {"recipient": "r", "facts": {"asthma": True}},
            {"recipient": "r", "facts": {"drug_allergy": True}},
        ], {}, PROFILE)
        changed = copy.deepcopy(report)
        changed["events"].reverse()
        self.assertFalse(verify_receipt_chain(changed))

    def test_unknown_field_is_rejected(self):
        with self.assertRaises(ValueError):
            matching_profiles(candidate_profiles(), {"unknown": True})

    def test_invalid_type_is_rejected(self):
        with self.assertRaises(ValueError):
            disclosure_report([{"recipient": "r", "facts": {"asthma": 1}}], {}, PROFILE)


if __name__ == "__main__":
    unittest.main()
