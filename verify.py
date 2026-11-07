# SPDX-License-Identifier: MIT
"""Independently verify retained TwinPrivacy receipt data and an optional anchor.

Usage: python verify.py outputs/enhanced_analysis.json outputs/trusted_receipt_anchor.txt
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from privacy_engine import verify_analysis


def main() -> None:
    parser = argparse.ArgumentParser(description='Verify a saved TwinPrivacy disclosure record')
    parser.add_argument('report', type=Path, help='Path to the saved enhanced analysis JSON')
    parser.add_argument('anchor', type=Path, nargs='?', help='External retained terminal digest file')
    args = parser.parse_args()
    with args.report.open(encoding='utf-8') as stream:
        report = json.load(stream)
    trusted_anchor = args.anchor.read_text(encoding='utf-8').strip() if args.anchor else None
    passed = verify_analysis(report, trusted_anchor)
    print('PASS: receipt history, analytical context, and saved report are consistent.' if passed
          else 'FAIL: the report or receipt anchor did not pass verification.')
    if not passed:
        raise SystemExit(1)
    if args.anchor is None:
        print('Note: without an independently retained anchor, complete replacement cannot be detected.')


if __name__ == '__main__':
    main()
