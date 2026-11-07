# SPDX-License-Identifier: MIT
"""Single-command quality-assured reproduction of TwinPrivacy analyses.

Usage: python reproduce.py
Runs the automated suite, rebuilds analysis outputs, checks all receipts,
and writes both patient-facing HTML and machine-readable records.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from evidence_validation import run_validation
from case_series import run_cases
from privacy_engine import analyze_scenario, verify_analysis
from patient_report import render_patient_report
from twinprivacy import disclosure_report, verify_receipt_chain

ROOT = Path(__file__).resolve().parent


def to_json(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n'


def build_outputs(output: Path, validate: bool = True) -> dict[str, object]:
    if validate:
        print('Step 1/4 · Running automated tests ...', flush=True)
        command = [sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT), '-p', 'test_*.py', '-v']
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode:
            raise RuntimeError('Tests failed; report generation halted')

    print('Step 2/4 · Reproducing analytical results ...', flush=True)
    with (ROOT / 'examples' / 'privacy_verification_scenario.json').open(encoding='utf-8') as f:
        scenario = json.load(f)
    analysis = analyze_scenario(scenario)
    if not verify_analysis(analysis):
        raise RuntimeError('Enhanced disclosure receipts failed verification')
    with (ROOT / 'examples' / 'clinical_disclosure_scenario.json').open(encoding='utf-8') as f:
        base = json.load(f)
    legacy_report = disclosure_report(base['releases'], base.get('recipient_prior', {}), base['actual_profile'])
    if not verify_receipt_chain(legacy_report):
        raise RuntimeError('Reference disclosure receipts failed verification')
    clinical = run_cases()
    if any(not verify_receipt_chain(case) for case in clinical['analyses']):
        raise RuntimeError('A clinical workbook receipt failed verification')

    print('Step 3/4 · Generating patient-facing and machine-readable outputs ...', flush=True)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'enhanced_analysis.json').write_text(to_json(analysis), encoding='utf-8')
    (output / 'patient_disclosure_statement.html').write_text(
        render_patient_report(analysis, analysis['final_receipt_sha256']), encoding='utf-8')
    (output / 'trusted_receipt_anchor.txt').write_text(analysis['final_receipt_sha256'] + '\n', encoding='utf-8')
    (output / 'reference_disclosure_report.json').write_text(to_json(legacy_report), encoding='utf-8')
    (output / 'clinical_case_results.json').write_text(to_json(clinical), encoding='utf-8')
    manifest = {
        'project': 'TwinPrivacy', 'engine_version': analysis['version'],
        'disclosure_events': len(analysis['events']),
        'receiving_organizations': len(analysis['recipient_summary']),
        'events_flagged_for_preference_review': sum(e['preference_status'] == 'review' for e in analysis['events']),
        'receipt_chain_verification': 'PASS',
        'clinical_case_analyses': len(clinical['analyses']),
        'patient_statement': 'patient_disclosure_statement.html',
        'machine_readable_analysis': 'enhanced_analysis.json',
        'receipt_anchor': 'trusted_receipt_anchor.txt',
    }
    (output / 'reproduction_manifest.json').write_text(to_json(manifest), encoding='utf-8')
    print(f'PASS · {manifest["disclosure_events"]} disclosure events; '
          f'{manifest["receiving_organizations"]} recipients; '
          f'{manifest["events_flagged_for_preference_review"]} events for review')
    print(f'Patient statement: {output / "patient_disclosure_statement.html"}')
    print(f'Complete results: {output / "enhanced_analysis.json"}')
    print('Step 4/4 · Generating synthetic evidence and independent validation ...', flush=True)
    research = run_validation(ROOT / 'evidence' / 'results')
    print(f"PASS · {research['synthetic_profile_count']} synthetic profiles; "
          f"{research['event_count']} events; "
          f"{research['independent_oracle']['comparison_values']} independent oracle comparisons")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description='Reproduce and verify all TwinPrivacy outputs')
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs',
                        help='Destination for reproducible results')
    args = parser.parse_args()
    build_outputs(args.output)


if __name__ == '__main__':
    main()
