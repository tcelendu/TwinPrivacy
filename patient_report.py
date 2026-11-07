# SPDX-License-Identifier: MIT
"""Standalone, accessible patient-facing verification report generator."""
from __future__ import annotations

from html import escape
from typing import Any
from privacy_engine import verify_analysis


def _h(value: Any) -> str:
    return escape(str(value), quote=True)


def _bits(value: float) -> str:
    return f'{value:.3f}'


def render_patient_report(report: dict[str, Any], anchor: str | None = None) -> str:
    """Return a locally viewable HTML disclosure statement (no external assets)."""
    valid = verify_analysis(report, anchor)
    labels = report['attribute_labels']
    patient_reference = report['patient_reference']
    rows = []
    detail = []
    review_events = sum(e['preference_status'] == 'review' for e in report['events'])
    for event in report['events']:
        facts = ', '.join(f'{labels.get(k, k)}: {v}' for k, v in event['disclosed_attributes'].items())
        status = {
            'review': 'Outside recorded sharing preferences',
            'within_preferences': 'Within recorded sharing preferences',
            'not_configured': 'Preferences not recorded',
        }[event['preference_status']]
        rows.append(f'<tr><td>{event["sequence"]}</td><td>{_h(event["recipient"])}</td>'
                    f'<td>{_h(facts)}</td><td class="num">{_bits(event["incremental_information_bits"])}</td>'
                    f'<td>{_h(status)}</td></tr>')
        shifts = ''
        for shift in event['model_implied_probability_shifts']:
            shifts += f'<li>{_h(labels.get(shift["attribute"],shift["attribute"]))}: '
            shifts += f'{shift["probability_before"] * 100:.1f}% → {shift["probability_after"] * 100:.1f}% '
            shifts += f'(model-implied change {shift["percentage_point_change"]:+.1f} percentage points)</li>'
        if not shifts:
            shifts = '<li>No additional probability shift above the reporting threshold.</li>'
        detail.append(f'<section class="event"><h3>Event {_h(event["sequence"])} · {_h(event["event_id"])}</h3>'
                      f'<p><strong>Recipient:</strong> {_h(event["recipient"])} · '
                      f'<strong>Purpose:</strong> {_h(event["purpose"])} · '
                      f'<strong>Channel:</strong> {_h(event["channel"])}</p>'
                      f'<p><strong>Disclosed:</strong> {_h(facts)}</p>'
                      f'<p><strong>Additional information:</strong> {_bits(event["incremental_information_bits"])} bits; '
                      f'<strong>cumulative:</strong> {_bits(event["cumulative_information_bits"])} bits. '
                      f'<strong>Preference check:</strong> {_h(status)}.</p>'
                      f'<p class="subheading">Potential inference about attributes not directly disclosed in this event</p>'
                      f'<ul>{shifts}</ul><p class="digest">Receipt SHA-256: {_h(event["receipt_sha256"])}</p></section>')
    recipient_lines = [
        f'<tr><td>{_h(r["recipient"])}</td><td class="num">{r["event_count"]}</td>'
        f'<td class="num">{_bits(r["cumulative_information_bits"])} bits</td>'
        f'<td class="num">{r["events_for_review"]}</td></tr>'
        for r in report['recipient_summary']
    ]
    integrity_label = 'PASS — recorded sequence is internally consistent' if valid else 'FAIL — verification requires review'
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>TwinPrivacy | Patient disclosure statement · {_h(patient_reference)}</title>
<style>
:root {{color-scheme:light;--ink:#172b40;--muted:#566779;--line:#dce4e9;--surface:#f4f7fa;--accent:#14636a}}
*{{box-sizing:border-box}}body{{font:16px/1.55 system-ui,-apple-system,Segoe UI,Arial,sans-serif;color:var(--ink);background:#fff;margin:0}}
main{{max-width:1010px;margin:auto;padding:34px 24px 70px}}header{{border-bottom:3px solid var(--ink);padding-bottom:22px}}
h1{{font-size:2.3rem;line-height:1.15;margin:.15em 0}}h2{{font-size:1.3rem;margin:36px 0 10px}}
h3{{font-size:1.05rem;margin:0 0 10px}}p{{margin:10px 0}}.eyebrow{{text-transform:uppercase;letter-spacing:.12em;font-size:.78rem;font-weight:750;color:var(--accent)}}
.subtitle,.small{{color:var(--muted)}}.small{{font-size:.84rem}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:12px;margin-top:25px}}
.metric{{border:1px solid var(--line);padding:16px;border-radius:8px;background:var(--surface)}}.metric b{{display:block;font-size:1.6rem}}
.tablewrap{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;font-size:.93rem}}th{{text-align:left;color:var(--muted);background:var(--surface);font-weight:700}}
th,td{{padding:11px 9px;border-bottom:1px solid var(--line);vertical-align:top}}.num{{white-space:nowrap;text-align:right}}.event{{border:1px solid var(--line);padding:22px;margin:14px 0;border-radius:8px}}
.subheading{{font-weight:700}}.digest{{font:12px/1.5 ui-monospace,monospace;overflow-wrap:anywhere;color:var(--muted)}}
.notice{{border-left:4px solid var(--accent);padding:12px 16px;background:var(--surface)}}footer{{border-top:1px solid var(--line);margin-top:40px;padding-top:16px;color:var(--muted)}}
@media print{{main{{padding:12mm}}.event{{break-inside:avoid}}}}
</style></head><body><main>
<header><div class="eyebrow">TwinPrivacy / Patient disclosure statement</div>
<h1>Your health-information disclosure record</h1>
<p class="subtitle">Reference {_h(patient_reference)} · Scenario {_h(report['scenario_id'])} · Engine v{_h(report['version'])}</p>
<p>This statement explains information contained in the recorded releases, how it changes recipient-specific knowledge under the declared information model, and which disclosures warrant review against recorded sharing preferences.</p></header>
<div class="grid"><div class="metric"><span>Recorded disclosures</span><b>{report['event_count']}</b></div>
<div class="metric"><span>Receiving organizations</span><b>{len(report['recipient_summary'])}</b></div>
<div class="metric"><span>Events to review</span><b>{review_events}</b></div>
<div class="metric"><span>Receipt integrity</span><b>{'Pass' if valid else 'Fail'}</b></div></div>
<h2>Record verification</h2><p><strong>{_h(integrity_label)}</strong></p>
<p class="small">Final receipt digest: {_h(report['final_receipt_sha256'])}</p>
<p class="notice">Verification establishes consistency of the supplied record and its analysis assumptions. It does not establish that every real-world access was logged, confirm the recipient's identity, or certify legal compliance. External retention of the digest is needed to detect whole-record replacement.</p>
<h2>Summary by recipient</h2><div class="tablewrap"><table><thead><tr><th>Recipient</th><th class="num">Events</th><th class="num">Cumulative information</th><th class="num">Review</th></tr></thead><tbody>{''.join(recipient_lines)}</tbody></table></div>
<p class="small">Information values are conditional pointwise surprisal in bits under the specified profile distribution. They are not empirical estimates of patient re-identification risk.</p>
<h2>Disclosure history</h2><div class="tablewrap"><table><thead><tr><th>Event</th><th>Recipient</th><th>Attributes recorded</th><th class="num">New information</th><th>Preference check</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<h2>Individual event explanations</h2>{''.join(detail)}
<footer>Generated from the reproducible TwinPrivacy analytical workflow. The underlying profile weights, disclosures, recipient baseline knowledge and preference settings are retained with the machine-readable report.</footer>
</main></body></html>'''
