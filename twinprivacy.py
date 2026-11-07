# SPDX-License-Identifier: MIT
"""TwinPrivacy: recipient-specific health-information disclosure analysis.

Combines a discrete information-gain model with hash-linked disclosure receipts
for a reproducible, specified clinical-attribute assessment.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any

ATTRIBUTES = ("diabetes", "asthma", "drug_allergy")
VERSION = "0.4.0"
ROOT = Path(__file__).resolve().parent
DEFAULT_SCENARIO = ROOT / "examples" / "clinical_disclosure_scenario.json"


def candidate_profiles() -> list[dict[str, bool]]:
    """Enumerate the eight profiles in the reference three-attribute model."""
    return [
        dict(zip(ATTRIBUTES, values))
        for values in itertools.product((False, True), repeat=len(ATTRIBUTES))
    ]


def _validate_facts(facts: dict[str, bool]) -> None:
    if not isinstance(facts, dict):
        raise ValueError("Disclosure facts must be an object")
    unknown = set(facts) - set(ATTRIBUTES)
    if unknown:
        raise ValueError(f"Unrecognized clinical attributes: {sorted(unknown)}")
    if any(type(value) is not bool for value in facts.values()):
        raise ValueError("Clinical attributes must have Boolean values")


def matching_profiles(
    profiles: list[dict[str, bool]], facts: dict[str, bool]
) -> list[dict[str, bool]]:
    """Return the candidate profiles consistent with the supplied information."""
    _validate_facts(facts)
    return [
        profile for profile in profiles
        if all(profile[field] == value for field, value in facts.items())
    ]


def _digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def disclosure_report(
    releases: list[dict[str, Any]],
    recipient_prior: dict[str, dict[str, bool]],
    actual_profile: dict[str, bool],
) -> dict[str, Any]:
    """Quantify incremental and cumulative information disclosed per recipient.

    The information-gain model uses eight equiprobable candidate profiles.
    Recipients are evaluated independently, accounting for their declared prior
    knowledge. Each recorded disclosure generates a hash-linked receipt.
    """
    if not isinstance(actual_profile, dict) or set(actual_profile) != set(ATTRIBUTES):
        raise ValueError("A complete reference profile is required")
    _validate_facts(actual_profile)
    if not isinstance(recipient_prior, dict):
        raise ValueError("Recipient prior knowledge must be an object")
    if not isinstance(releases, list):
        raise ValueError("Disclosures must be an array")

    profiles = candidate_profiles()
    known: dict[str, dict[str, bool]] = {}
    baseline_counts: dict[str, int] = {}

    for recipient, prior in recipient_prior.items():
        if not isinstance(recipient, str) or not recipient.strip():
            raise ValueError("A recipient identifier must be nonempty")
        _validate_facts(prior)
        if any(actual_profile[field] != value for field, value in prior.items()):
            raise ValueError(f"Prior knowledge conflicts with the reference profile: {recipient}")
        known[recipient] = dict(prior)
        baseline_counts[recipient] = len(matching_profiles(profiles, prior))

    events: list[dict[str, Any]] = []
    prior_receipt_hash = "0" * 64

    for sequence, release in enumerate(releases, 1):
        if not isinstance(release, dict) or set(release) != {"recipient", "facts"}:
            raise ValueError(f"Disclosure {sequence} must specify recipient and facts")
        recipient = release["recipient"]
        facts = release["facts"]
        if not isinstance(recipient, str) or not recipient.strip():
            raise ValueError("A recipient identifier must be nonempty")
        _validate_facts(facts)
        if any(actual_profile[field] != value for field, value in facts.items()):
            raise ValueError(f"Disclosure {sequence} conflicts with the reference profile")

        if recipient not in known:
            known[recipient] = {}
            baseline_counts[recipient] = len(profiles)

        before = len(matching_profiles(profiles, known[recipient]))
        updated = {**known[recipient], **facts}
        after = len(matching_profiles(profiles, updated))
        incremental = math.log2(before / after)
        cumulative = math.log2(baseline_counts[recipient] / after)

        event = {
            "sequence": sequence,
            "recipient": recipient,
            "disclosed_attributes": dict(sorted(facts.items())),
            "incremental_information_bits": round(incremental, 4),
            "cumulative_information_bits": round(cumulative, 4),
            "remaining_candidate_profiles": after,
            "previous_receipt_sha256": prior_receipt_hash,
        }
        event["receipt_sha256"] = _digest(event)
        events.append(event)
        prior_receipt_hash = event["receipt_sha256"]
        known[recipient] = updated

    return {
        "project": "TwinPrivacy",
        "version": VERSION,
        "measurement": "recipient-specific information gain (bits)",
        "candidate_profile_count": len(profiles),
        "events": events,
        "final_receipt_sha256": prior_receipt_hash,
    }


def verify_receipt_chain(report: dict[str, Any]) -> bool:
    """Check internal linkage and integrity of recorded disclosure receipts.

    The check does not authenticate the reporter or establish completeness of
    the disclosure history; independent retention of the final digest is needed
    to detect replacement of an entire chain.
    """
    if not isinstance(report, dict) or not isinstance(report.get("events"), list):
        return False
    expected_previous = "0" * 64
    for sequence, event in enumerate(report["events"], 1):
        if not isinstance(event, dict):
            return False
        if event.get("sequence") != sequence or event.get("previous_receipt_sha256") != expected_previous:
            return False
        claimed = event.get("receipt_sha256")
        without_digest = {key: value for key, value in event.items() if key != "receipt_sha256"}
        if not isinstance(claimed, str) or claimed != _digest(without_digest):
            return False
        expected_previous = claimed
    return report.get("final_receipt_sha256") == expected_previous


def render_table(report: dict[str, Any]) -> str:
    headers = ("Event", "Recipient", "New (bits)", "Cumulative (bits)", "Candidates")
    rows = [
        (
            str(event["sequence"]),
            event["recipient"],
            f'{event["incremental_information_bits"]:.1f}',
            f'{event["cumulative_information_bits"]:.1f}',
            str(event["remaining_candidate_profiles"]),
        )
        for event in report["events"]
    ]
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) if rows else len(headers[i]) for i in range(len(headers))]
    line = "  ".join(headers[i].ljust(widths[i]) for i in range(len(headers)))
    body = ["  ".join(row[i].ljust(widths[i]) for i in range(len(headers))) for row in rows]
    return "\n".join([
        "TWINPRIVACY | DISCLOSURE ANALYSIS",
        "=" * len(line), line, "-" * len(line), *body,
        "=" * len(line),
        f"Receipt-chain verification: {'PASS' if verify_receipt_chain(report) else 'FAIL'}",
        "Analysis basis: specified clinical-attribute record",
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description="TwinPrivacy | Health-data disclosure accounting")
    parser.add_argument("--scenario", type=Path, default=DEFAULT_SCENARIO,
                        help="Path to a structured disclosure scenario (JSON)")
    parser.add_argument("--format", choices=("table", "json"), default="table")
    args = parser.parse_args()

    with args.scenario.open("r", encoding="utf-8") as handle:
        scenario = json.load(handle)
    if "population_model" in scenario:
        from privacy_engine import analyze_scenario
        result = analyze_scenario(scenario)
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            header = ("Sequence", "Recipient", "New bits", "Cumulative bits", "Preference")
            print("TWINPRIVACY | WEIGHTED DISCLOSURE ANALYSIS")
            print(" | ".join(header))
            for event in result["events"]:
                print(f'{event["sequence"]:>8} | {event["recipient"]:<24} | '
                      f'{event["incremental_information_bits"]:>8.3f} | '
                      f'{event["cumulative_information_bits"]:>15.3f} | '
                      f'{event["preference_status"]}')
            print(f'Receipt SHA-256: {result["final_receipt_sha256"]}')
        return
    result = disclosure_report(
        scenario["releases"], scenario.get("recipient_prior", {}), scenario["actual_profile"]
    )
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(render_table(result))


if __name__ == "__main__":
    main()
