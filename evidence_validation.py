# SPDX-License-Identifier: MIT
"""Deterministic evidence generation and independent finite-state reference checks.

Validation is computational / model-based, not a clinical effectiveness trial.
No third-party packages, external services, or patient data are used.
"""
from __future__ import annotations

import csv
import io
import itertools
import json
import math
import random
import statistics
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

from privacy_engine import analyze_scenario, verify_analysis

ROOT = Path(__file__).resolve().parent
SCENARIO = ROOT / 'examples' / 'privacy_verification_scenario.json'
SEED = 20261107
COHORT_SIZE = 512
FIELDS = ('diabetes', 'chronic_kidney_disease', 'asthma', 'drug_allergy')


def _json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n'


def cohort_rows(scenario: dict[str, Any], count: int = COHORT_SIZE, seed: int = SEED) -> list[dict[str, Any]]:
    """Generate a fully synthetic cohort from the specified joint probability model.

    Conditional values are design choices for a software test, not clinical
    prevalence, treatment recommendations, diagnosis criteria, or observed data.
    """
    rng = random.Random(seed)
    choices = [r['profile'] for r in scenario['population_model']]
    weights = [r['weight'] for r in scenario['population_model']]
    rows = []
    for i in range(count):
        p = dict(rng.choices(choices, weights=weights, k=1)[0])
        age = rng.randint(30, 79)
        # The numerical clinical fields supply context only; the four Boolean
        # attributes are the actual disclosure-engine analysis inputs.
        hba1c = round(rng.uniform(6.3, 10.1) if p['diabetes'] else rng.uniform(4.7, 5.9), 1)
        egfr = rng.randint(24, 58) if p['chronic_kidney_disease'] else rng.randint(65, 112)
        fev1_fvc = round(rng.uniform(0.54, 0.73) if p['asthma'] else rng.uniform(0.77, 0.9), 2)
        rows.append({
            'record_id': f'SYN-TP-{i+1:04d}',
            'age_years': age,
            'diabetes': int(p['diabetes']),
            'chronic_kidney_disease': int(p['chronic_kidney_disease']),
            'asthma': int(p['asthma']),
            'drug_allergy': int(p['drug_allergy']),
            'hba1c_percent': f'{hba1c:.1f}',
            'egfr_mL_min_1_73m2': egfr,
            'fev1_fvc_ratio': f'{fev1_fvc:.2f}',
            'medication_allergy_label': 'penicillin' if p['drug_allergy'] else 'none_recorded',
        })
    return rows


def cohort_csv(rows: list[dict[str, Any]]) -> str:
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def profile_of(row: dict[str, Any]) -> dict[str, bool]:
    return {field: bool(int(row[field])) for field in FIELDS}


def case_scenario(base: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    """Preserve the event order and recipient knowledge of the reference study."""
    scenario = deepcopy(base)
    scenario['scenario_id'] = f'VAL-{row["record_id"]}'
    scenario['patient_reference'] = row['record_id']
    actual = profile_of(row)
    scenario['actual_profile'] = actual
    for recipient, facts in scenario['recipient_prior'].items():
        scenario['recipient_prior'][recipient] = {field: actual[field] for field in facts}
    for release in scenario['releases']:
        release['facts'] = {field: actual[field] for field in release['facts']}
    return scenario


def _prob_mass(states: list[dict[str, Any]], known: dict[str, Any]) -> float:
    """Independent reference oracle: direct enumeration, no engine helpers."""
    return math.fsum(
        state['weight'] for state in states
        if all(state['profile'][key] == value for key, value in known.items())
    )


def reference_oracle(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    """Separate probability enumeration implementation for the finite joint model."""
    states = scenario['population_model']
    total = math.fsum(state['weight'] for state in states)
    known = {recipient: dict(prior) for recipient, prior in scenario['recipient_prior'].items()}
    initial_mass = {recipient: _prob_mass(states, prior) / total for recipient, prior in known.items()}
    seen = []
    for release in scenario['releases']:
        recipient = release['recipient']
        if recipient not in known:
            known[recipient] = {}
            initial_mass[recipient] = 1.0
        before = _prob_mass(states, known[recipient]) / total
        updated = {**known[recipient], **release['facts']}
        after = _prob_mass(states, updated) / total
        if not 0 < after <= before + 1e-12:
            raise AssertionError('Unexpected probability model behavior')
        inc = math.log2(before / after)
        cumul = math.log2(initial_mass[recipient] / after)
        # Count review flags from stated preferences, independent of engine.
        policy = scenario['recipient_preferences'].get(recipient)
        flag = bool(policy is not None and (set(release['facts']) - set(policy)))
        seen.append({'incremental_bits': inc, 'cumulative_bits': cumul, 'flag': flag})
        known[recipient] = updated
    return seen


def independent_model(base: dict[str, Any]) -> list[dict[str, Any]]:
    """Construct a comparator joint model using products of the original marginals."""
    states = base['population_model']
    total = math.fsum(s['weight'] for s in states)
    marginal = {
        f: math.fsum(s['weight'] for s in states if s['profile'][f]) / total
        for f in FIELDS
    }
    result = []
    for values in itertools.product((False, True), repeat=len(FIELDS)):
        p = dict(zip(FIELDS, values))
        weight = math.prod(marginal[f] if p[f] else (1 - marginal[f]) for f in FIELDS)
        result.append({'profile': p, 'weight': weight})
    return result


def _indirect_probability(scenario: dict[str, Any], known: dict[str, Any], field: str, value: bool) -> float:
    states = scenario['population_model']
    mass = _prob_mass(states, known)
    return _prob_mass(states, {**known, field: value}) / mass


def tamper_experiments(report: dict[str, Any], original: dict[str, Any]) -> dict[str, Any]:
    anchor = report['final_receipt_sha256']
    attack_results = {}
    for label, changer in (
        ('alter_event_attribute', lambda r: r['events'][0]['disclosed_attributes'].update({'diabetes': not r['events'][0]['disclosed_attributes']['diabetes']})),
        ('remove_recorded_event', lambda r: r['events'].pop(1)),
        ('reorder_events', lambda r: r['events'].__setitem__(slice(0, 2), r['events'][0:2][::-1])),
        ('alter_analysis_model', lambda r: r['analysis_context']['population_model'][0].update({'weight': 0.8})),
    ):
        changed = deepcopy(report)
        changer(changed)
        attack_results[label] = not verify_analysis(changed, anchor)
    # Demonstrates the trusted-anchor security boundary. A person capable of
    # regenerating both data and chain can create a self-consistent replacement.
    edited = deepcopy(original)
    edited['releases'][0]['purpose'] = 'Changed by log custodian'
    forged_report = analyze_scenario(edited)
    attack_results['recomputed_history_against_original_anchor'] = (
        not verify_analysis(forged_report, anchor)
    )
    attack_results['rewritten_history_without_external_anchor_passes'] = verify_analysis(forged_report)
    return attack_results


def run_validation(output_dir: Path | None = None) -> dict[str, Any]:
    base = json.loads(SCENARIO.read_text(encoding='utf-8'))
    rows = cohort_rows(base)
    independence = independent_model(base)
    all_states = [tuple(p[field] for field in FIELDS) for p in (profile_of(r) for r in rows)]
    counts = Counter(all_states)
    errors: list[float] = []
    repeat_zero = 0
    prior_known_zero = 0
    correlated_shift = []
    independent_shift = []
    model_sensitive_abs_delta = []
    review_flags = 0
    reference_flags = 0
    preference_exact_matches = 0
    inferred_ckd_shift_checks = 0
    repeated_events_baseline_miscount = 0
    event_total = 0
    prior_knowledge_events_baseline_miscount = 0
    tamper = None

    for index, patient in enumerate(rows):
        scenario = case_scenario(base, patient)
        result = analyze_scenario(scenario)
        oracle = reference_oracle(scenario)
        assert len(oracle) == len(result['events'])
        assert verify_analysis(result, result['final_receipt_sha256'])
        independent_case = deepcopy(scenario)
        independent_case['population_model'] = independence
        alt = analyze_scenario(independent_case)
        for e, ref, indep in zip(result['events'], oracle, alt['events']):
            event_total += 1
            errors.extend((abs(e['incremental_information_bits'] - ref['incremental_bits']),
                           abs(e['cumulative_information_bits'] - ref['cumulative_bits'])))
            review_flags += int(e['preference_status'] == 'review')
            reference_flags += int(ref['flag'])
            preference_exact_matches += int((e['preference_status'] == 'review') == ref['flag'])
            if e['event_id'] == 'TP-E002':
                if abs(e['incremental_information_bits']) < 1e-9:
                    repeat_zero += 1
                repeated_events_baseline_miscount += 1  # naive event count counts one disclosure
            if e['event_id'] == 'TP-E008':
                if abs(e['incremental_information_bits']) < 1e-9:
                    prior_known_zero += 1
                prior_knowledge_events_baseline_miscount += 1
            model_sensitive_abs_delta.append(abs(e['incremental_information_bits'] - indep['incremental_information_bits']))
        # Independent corroboration of the inferred kidney-disease shift from
        # revealing diabetes status to the research recipient (E001).
        diabetes = profile_of(patient)['diabetes']
        kidney = profile_of(patient)['chronic_kidney_disease']
        before = _indirect_probability(scenario, {}, 'chronic_kidney_disease', kidney)
        after = _indirect_probability(scenario, {'diabetes': diabetes}, 'chronic_kidney_disease', kidney)
        correlated_shift.append(abs(after - before))
        inferred = [item for item in result['events'][0]['model_implied_probability_shifts']
                    if item['attribute'] == 'chronic_kidney_disease']
        if abs(after-before) >= 0.01:
            if len(inferred) != 1:
                raise AssertionError('Expected a reported CKD probability shift')
            if abs(inferred[0]['probability_before'] - before) >= 0.000001 or \
               abs(inferred[0]['probability_after'] - after) >= 0.000001:
                raise AssertionError('CKD inference does not match independently calculated probabilities')
            inferred_ckd_shift_checks += 1
        alt_before = _indirect_probability(independent_case, {}, 'chronic_kidney_disease', kidney)
        alt_after = _indirect_probability(independent_case, {'diabetes': diabetes}, 'chronic_kidney_disease', kidney)
        independent_shift.append(abs(alt_after - alt_before))
        if index == 0:
            tamper = tamper_experiments(result, scenario)

    assert tamper is not None
    result = {
        'study': 'TwinPrivacy deterministic synthetic-profile validation',
        'cohort_provenance': 'Generated from an author-specified 16-state joint distribution; not derived from patients or observational data',
        'model_provenance': 'Repository-specified weighted joint profile distribution; not epidemiological prevalence estimates',
        'synthetic_generator_seed': SEED,
        'synthetic_profile_count': len(rows),
        'distinct_profile_states_represented': len(counts),
        'possible_profile_states': len(base['population_model']),
        'event_count': event_total,
        'independent_oracle': {
            'comparison_values': len(errors),
            'maximum_absolute_difference_bits': round(max(errors), 9),
            'mean_absolute_difference_bits': round(statistics.mean(errors), 9),
            'tolerance_bits': 0.000001,
            'all_within_tolerance': max(errors) < 0.000001,
        },
        'repeated_disclosure': {
            'duplicate_events_evaluated': len(rows),
            'incremental_zero_bits': repeat_zero,
            'naive_event_count_would_count': repeated_events_baseline_miscount,
        },
        'recipient_prior_knowledge': {
            'already_known_events_evaluated': len(rows),
            'incremental_zero_bits': prior_known_zero,
            'naive_event_count_would_count': prior_knowledge_events_baseline_miscount,
        },
        'preference_flag_validation': {
            'flagged_by_engine': review_flags,
            'flagged_by_independent_rule': reference_flags,
            'agreement': preference_exact_matches == event_total,
            'exact_match_events': preference_exact_matches,
            'total_events': event_total,
        },
        'correlation_sensitivity': {
            'absolute_ckd_probability_shift_after_diabetes_mean_joint_pp': round(100 * statistics.mean(correlated_shift), 6),
            'absolute_ckd_probability_shift_after_diabetes_mean_independent_pp': round(100 * statistics.mean(independent_shift), 6),
            'max_absolute_event_bit_difference_joint_vs_independent': round(max(model_sensitive_abs_delta), 6),
            'mean_absolute_event_bit_difference_joint_vs_independent': round(statistics.mean(model_sensitive_abs_delta), 6),
            'ckd_probability_shifts_independently_checked': inferred_ckd_shift_checks,
            'interpretation': 'Sensitivity to modeling assumptions, not empirical superiority or a validated inference attack.',
        },
        'receipt_integrity_challenges': tamper,
        'scope': {
            'analysis_units': 'Recorded structured attribute disclosure events',
            'validation_type': 'In-model computational validation with independent finite-state enumeration',
            'not_covered': ['clinical generalizability', 'real EHR integration', 'free-text extraction',
                            'complete event capture', 'real adversarial inference', 'ground-truth population probabilities',
                            'regulatory compliance'],
        },
    }
    failures = []
    if not result['independent_oracle']['all_within_tolerance']:
        failures.append('finite-state oracle disagreement')
    if repeat_zero != len(rows) or prior_known_zero != len(rows):
        failures.append('repeat or prior-knowledge invariance')
    if preference_exact_matches != event_total or review_flags != reference_flags:
        failures.append('preference flag disagreement')
    if not all(tamper.values()):
        failures.append('integrity attack demonstration')
    if max(independent_shift) > 1e-10:
        failures.append('independence model contradiction')
    if failures:
        raise AssertionError('; '.join(failures))

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        data_dir = ROOT / 'data'
        data_dir.mkdir(exist_ok=True)
        (data_dir / 'synthetic_clinical_profiles.csv').write_text(cohort_csv(rows), encoding='utf-8', newline='')
        (data_dir / 'DATA_PROVENANCE.json').write_text(_json({
            'dataset': 'TwinPrivacy synthetic clinical profiles', 'number_of_records': len(rows),
            'generation_method': 'Seeded weighted sampling of the declared 16-state joint model; age and illustrative clinical measurements generated from explicit conditional ranges',
            'seed': SEED, 'provenance': 'Entirely synthetic; no actual patients or patient-derived records',
            'model_source': 'examples/privacy_verification_scenario.json',
            'modeled_attributes': list(FIELDS),
            'context_only_columns': ['age_years', 'hba1c_percent', 'egfr_mL_min_1_73m2', 'fev1_fvc_ratio', 'medication_allergy_label'],
            'limitations': 'Clinical context variables are rule-generated and not clinically validated; association structure is specified rather than estimated.',
        }), encoding='utf-8')
        (output_dir / 'validation_results.json').write_text(_json(result), encoding='utf-8')
        headers = ('diabetes', 'chronic_kidney_disease', 'asthma', 'drug_allergy', 'count', 'frequency')
        buffer = io.StringIO(newline='')
        writer = csv.writer(buffer)
        writer.writerow(headers)
        for state in sorted(counts):
            writer.writerow([*[int(v) for v in state], counts[state], f'{counts[state]/len(rows):.6f}'])
        (output_dir / 'profile_state_counts.csv').write_text(buffer.getvalue(), encoding='utf-8')
        (output_dir / 'VALIDATION_SUMMARY.md').write_text(render_summary(result), encoding='utf-8')
        (output_dir / 'VALIDATION_REPORT.html').write_text(render_html(result), encoding='utf-8')
    return result


def render_summary(r: dict[str, Any]) -> str:
    e = r['independent_oracle']
    cor = r['correlation_sensitivity']
    t = r['receipt_integrity_challenges']
    attacks = '\n'.join(f'| {name.replace("_", " ").capitalize()} | {"Observed" if value else "Not observed"} |'
                        for name, value in t.items())
    return f'''# TwinPrivacy | Reproducible validation findings

**Evaluation design.** Deterministic, in-model computational validation using {r['synthetic_profile_count']} generated clinical profiles, {r['event_count']} structured disclosure events and a specified {r['possible_profile_states']}-state joint probability distribution. The clinical records and model parameters are synthetic and are not empirical clinical evidence.

## Primary computational results

| Evaluation | Reproducible finding |
| --- | ---: |
| Patient profiles | {r['synthetic_profile_count']} |
| Profile states represented | {r['distinct_profile_states_represented']} / {r['possible_profile_states']} |
| Disclosure events processed | {r['event_count']} |
| Independent reference comparisons | {e['comparison_values']} |
| Maximum absolute deviation from independent enumerator | {e['maximum_absolute_difference_bits']:.9f} bits |
| Reference calculations within prespecified 0.000001-bit tolerance | {'Yes' if e['all_within_tolerance'] else 'No'} |
| Repeated disclosures correctly assigned zero incremental bits | {r['repeated_disclosure']['incremental_zero_bits']} / {r['synthetic_profile_count']} |
| Attributes already known to recipient assigned zero incremental bits | {r['recipient_prior_knowledge']['incremental_zero_bits']} / {r['synthetic_profile_count']} |
| Preference flag decisions matching independently implemented rules | {r['preference_flag_validation']['exact_match_events']} / {r['preference_flag_validation']['total_events']} |
| CKD probability-shift outputs independently checked | {cor['ckd_probability_shifts_independently_checked']} |

## Comparator analyses

**Event-count baseline.** A naïve count of release events registers each of the {r['synthetic_profile_count']} duplicate disclosures and {r['synthetic_profile_count']} prior-known disclosures as another event. TwinPrivacy instead reports zero additional conditional surprisal for these identical facts. Event count and information bits are distinct quantities and should not be interpreted as comparable measurements.

**Independence ablation.** When the same profile marginals are retained but all four clinical attributes are treated as independent, the mean absolute modeled chronic-kidney-disease probability shift after diabetes disclosure is {cor['absolute_ckd_probability_shift_after_diabetes_mean_independent_pp']:.6f} percentage points, compared with {cor['absolute_ckd_probability_shift_after_diabetes_mean_joint_pp']:.6f} percentage points under the specified correlated model. Across all events, the maximum absolute difference in incremental information between the two assumptions is {cor['max_absolute_event_bit_difference_joint_vs_independent']:.6f} bits. **These findings demonstrate model sensitivity, not greater real-world predictive accuracy.**

## Integrity challenge results

| Challenge | Observed outcome |
| --- | --- |
{attacks}

The final row demonstrates a deliberate limitation: when the trusted external receipt anchor is absent, a replacement history with newly calculated internal hashes can verify as internally consistent. Hash-linked receipts **do not authenticate the origin or completeness of logged events**.

## Interpretation

Under the supplied assumptions, the implementation accurately reproduces conditional pointwise information values using an independently written finite-state enumeration, preserves recipient-specific knowledge, and detects basic tampering against a retained hash anchor. This is computational validation **within a specified analytical model**. It does not establish clinical sensitivity or specificity, a universal privacy bound, completeness of access auditing, or validation against real-life data.

Run `python reproduce.py` from the repository root. See `docs/VALIDATION_PROTOCOL.md`, `docs/RESEARCH_NOVELTY.md`, and `data/DATA_PROVENANCE.json` for full methods and boundaries.
'''


def render_html(r: dict[str, Any]) -> str:
    """Portable, dependency-free review copy of the reproducible findings."""
    e = r['independent_oracle']
    co = r['correlation_sensitivity']
    joint = co['absolute_ckd_probability_shift_after_diabetes_mean_joint_pp']
    independent = co['absolute_ckd_probability_shift_after_diabetes_mean_independent_pp']
    challenges = ''.join(
        '<tr><td>' + label.replace('_', ' ').capitalize() + '</td>'
        '<td>' + ('Observed' if passed else 'Not observed') + '</td></tr>'
        for label, passed in r['receipt_integrity_challenges'].items()
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TwinPrivacy | Reproducible Research Evidence</title>
<style>
:root {{ color-scheme:light; }} * {{box-sizing:border-box}} body {{margin:0;background:#f0f3f6;color:#16253c;font:15px/1.65 system-ui,-apple-system,Segoe UI,Arial,sans-serif}} main {{max-width:1000px;margin:42px auto;background:white;box-shadow:0 18px 56px #1b355019;border-radius:14px;padding:50px 56px}} .overline {{font-size:12px;letter-spacing:.18em;color:#64758d;font-weight:700;text-transform:uppercase}} h1 {{font:600 39px/1.1 Georgia,serif;letter-spacing:-.02em;margin:13px 0 14px;color:#13304d}} .deck {{font-size:17px;color:#54657b;max-width:720px}} .rule {{height:1px;background:#dbe2ea;margin:30px 0}} h2 {{font:600 23px Georgia,serif;margin:32px 0 12px}} p {{margin:10px 0 15px}} .cards {{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:26px 0}} .card {{background:#eef3f7;padding:19px;border-radius:10px}} .num {{font-weight:700;font-size:29px;letter-spacing:-.025em;font-variant-numeric:tabular-nums;color:#13304d}} .lbl {{font-size:12px;color:#576d83;margin-top:2px}} table {{border-collapse:collapse;width:100%;font-size:14px;margin:16px 0 25px}} th,td {{padding:11px 10px;border-bottom:1px solid #dfe5ed;text-align:left;vertical-align:top}} th {{background:#f1f5f8;color:#44566b}} .barblock {{padding:18px;background:#f4f7fa;border-radius:10px;margin:16px 0}} .track {{height:18px;border-radius:30px;background:#dce4ec;overflow:hidden;margin:6px 0 11px}} .fill {{height:100%;background:#416f89;border-radius:30px}} .muted {{color:#687b91;font-size:13px}} .note {{border-left:3px solid #57778b;padding:11px 17px;background:#f4f7f9}} footer {{margin-top:36px;border-top:1px solid #dbe2ea;padding-top:19px;color:#67788d;font-size:12px}} @media(max-width:700px) {{main {{padding:26px 18px;margin:0;border-radius:0}}.cards {{grid-template-columns:1fr 1fr}}h1 {{font-size:32px}}}}
</style></head><body><main>
<div class="overline">TwinPrivacy / Research Evidence / Version 0.6.0</div>
<h1>Verifying disclosures.<br>Measuring what was revealed.</h1>
<p class="deck">Reproducible computational evaluation of a recipient-conditioned information-accounting system for recorded structured health-data disclosures.</p>
<div class="rule"></div>
<div class="cards"><div class="card"><div class="num">{r['synthetic_profile_count']:,}</div><div class="lbl">Synthetic clinical profiles</div></div><div class="card"><div class="num">{r['event_count']:,}</div><div class="lbl">Recorded disclosure events</div></div><div class="card"><div class="num">{e['comparison_values']:,}</div><div class="lbl">Independent numerical comparisons</div></div></div>
<h2>Evaluation design</h2>
<p>Four modeled clinical attributes, sixteen weighted profile states, three recipient roles and eight ordered event templates per clinical profile. The cohort and all model parameters are generated or specified for software validation. No patient records were collected or analyzed.</p>
<h2>Implementation validation</h2>
<table><thead><tr><th>Prespecified check</th><th>Result</th></tr></thead><tbody>
<tr><td>Maximum deviation from independently coded finite-state enumerator</td><td>{e['maximum_absolute_difference_bits']:.9f} bits</td></tr>
<tr><td>Within 0.000001-bit tolerance</td><td>{'Yes' if e['all_within_tolerance'] else 'No'}</td></tr>
<tr><td>Repeated disclosures yielding zero additional modeled information</td><td>{r['repeated_disclosure']['incremental_zero_bits']:,} / {r['synthetic_profile_count']:,}</td></tr>
<tr><td>Prior-known facts yielding zero additional modeled information</td><td>{r['recipient_prior_knowledge']['incremental_zero_bits']:,} / {r['synthetic_profile_count']:,}</td></tr>
<tr><td>Preference flags matching independent rule</td><td>{r['preference_flag_validation']['exact_match_events']:,} / {r['preference_flag_validation']['total_events']:,}</td></tr>
</tbody></table>
<h2>Sensitivity to correlation assumptions</h2>
<p>Mean absolute modeled change in the probability of chronic kidney disease after diabetes status is disclosed (percentage points). The independent-attribute model retains identical attribute marginals.</p>
<div class="barblock"><strong>Specified correlated model</strong> <span class="muted">{joint:.4f} pp</span><div class="track"><div class="fill" style="width:{min(100,joint*9):.3f}%"></div></div><strong>Independent-attribute comparator</strong> <span class="muted">{independent:.4f} pp</span><div class="track"><div class="fill" style="width:{min(100,independent*9):.3f}%"></div></div><div class="muted">Largest absolute per-event information difference across assumptions: {co['max_absolute_event_bit_difference_joint_vs_independent']:.6f} bits. These results show model sensitivity, not empirical predictive superiority.</div></div>
<h2>Stored-record integrity challenges</h2><table><thead><tr><th>Challenge</th><th>Expected behavior reproduced</th></tr></thead><tbody>{challenges}</tbody></table>
<div class="note"><strong>Critical limitation:</strong> an internally rehashed replacement record can validate without the independently trusted original anchor. Cryptographic receipt integrity alone cannot prove that every data access has been logged, who authored the record, or that sharing was lawful.</div>
<h2>Scientific positioning</h2><p>The software combines established information-theoretic accounting with recipient-specific state, preference review, a patient-readable report and hash-linked receipts. None of these individual ideas is claimed as a new privacy theorem. An independently demonstrated advance beyond established audit and quantitative-information-flow approaches remains a substantive research goal.</p>
<p class="muted">Reproduce the evidence with <code>python reproduce.py</code>; see docs/VALIDATION_PROTOCOL.md and docs/RESEARCH_NOVELTY.md. Functional computational verification is not clinical validation.</p>
<footer>TwinPrivacy · Open-source computational methods · Research evidence generated deterministically from the repository</footer>
</main></body></html>
"""


if __name__ == '__main__':
    r = run_validation(ROOT / 'evidence' / 'results')
    print(f"PASS | {r['synthetic_profile_count']} synthetic profiles | {r['event_count']} events | "
          f"{r['independent_oracle']['comparison_values']} oracle comparisons | "
          f"maximum residual {r['independent_oracle']['maximum_absolute_difference_bits']:.9f} bits")
