# SPDX-License-Identifier: MIT
"""Run the three reference clinical disclosure analyses."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from twinprivacy import disclosure_report, verify_receipt_chain

ROOT = Path(__file__).resolve().parent
DEFAULT_CASES = ROOT / "examples" / "clinical_case_series.json"


def run_cases(path: Path = DEFAULT_CASES) -> dict:
    with path.open("r", encoding="utf-8") as f:
        cases = json.load(f)["cases"]
    analyses = []
    for case in cases:
        report = disclosure_report(case["releases"], case.get("recipient_prior", {}), case["actual_profile"])
        if not verify_receipt_chain(report):
            raise RuntimeError(f"Receipt verification failed for {case['case_id']}")
        analyses.append({"case_id": case["case_id"], **report})
    return {"series": "TwinPrivacy structured clinical case analyses", "analyses": analyses}


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproduce structured clinical disclosure analyses")
    parser.add_argument("--format", choices=("table", "json"), default="table")
    args = parser.parse_args()
    analyses = run_cases()["analyses"]
    if args.format == "json":
        print(json.dumps({"analyses": analyses}, indent=2))
        return
    print("TWINPRIVACY | CLINICAL DISCLOSURE CASE ANALYSES")
    print("=" * 78)
    for case in analyses:
        print(case["case_id"])
        for event in case["events"]:
            attr = ", ".join(event["disclosed_attributes"])
            print(f"  {event['sequence']:>2}  {event['recipient']:<24} {attr:<22} +{event['incremental_information_bits']:.1f} bits | total {event['cumulative_information_bits']:.1f}")
        print(f"  Receipt integrity: {'PASS' if verify_receipt_chain(case) else 'FAIL'}")
        print()

if __name__ == "__main__":
    main()
