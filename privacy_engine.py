# SPDX-License-Identifier: MIT
"""Recipient-specific disclosure accounting with a stated joint probability model.

The implementation quantifies how recorded disclosures change the set of
possible health profiles and model-implied information for each recipient.
No external services or third-party packages are required.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any

VERSION = '0.6.0'
ZERO_HASH = '0' * 64


def canonical_hash(value: Any) -> str:
    serialized = json.dumps(value, sort_keys=True, ensure_ascii=False,
                            separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()


def _is_atomic(value: Any) -> bool:
    return value is None or type(value) in (bool, str, int)


def _require_facts(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f'{label} must be a JSON object')
    if set(value) - fields:
        raise ValueError(f'{label} contains unknown attributes: {sorted(set(value)-fields)}')
    if not all(_is_atomic(v) for v in value.values()):
        raise ValueError(f'{label} must contain Boolean, integer, string or null values')
    return value


def _matches(profile: dict[str, Any], facts: dict[str, Any]) -> bool:
    return all(profile[k] == v and type(profile[k]) is type(v) for k, v in facts.items())


def _posterior(model: list[dict[str, Any]], known: dict[str, Any]) -> tuple[list[dict[str, Any]], float]:
    matching = [row for row in model if _matches(row['profile'], known)]
    mass = math.fsum(row['weight'] for row in matching)
    return matching, mass


def _entropy(rows: list[dict[str, Any]], mass: float) -> float:
    return -math.fsum((row['weight'] / mass) * math.log2(row['weight'] / mass)
                      for row in rows if row['weight'] > 0)


def _marginal(rows: list[dict[str, Any]], mass: float, field: str, value: Any) -> float:
    return math.fsum(row['weight'] for row in rows if
                     row['profile'][field] == value and type(row['profile'][field]) is type(value)) / mass


def _rounded(value: float) -> float:
    return round(value, 6)


def _read_model(scenario: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    raw_model = scenario.get('population_model')
    if not isinstance(raw_model, list) or len(raw_model) < 2:
        raise ValueError('population_model requires two or more weighted profile states')
    fields: list[str] | None = None
    states: set[str] = set()
    model = []
    for index, row in enumerate(raw_model, start=1):
        if not isinstance(row, dict) or set(row) != {'profile', 'weight'}:
            raise ValueError(f'population_model row {index} needs profile and weight')
        profile = row['profile']
        if not isinstance(profile, dict) or not profile or any(not isinstance(k, str) or not k for k in profile):
            raise ValueError('Every profile must contain named clinical attributes')
        if fields is None:
            fields = sorted(profile)
        elif sorted(profile) != fields:
            raise ValueError('All population profiles must have the same attributes')
        _require_facts(profile, set(fields), 'population profile')
        weight = row['weight']
        if type(weight) not in (float, int) or not math.isfinite(weight) or weight <= 0:
            raise ValueError('Population weights must be positive finite numbers')
        state = json.dumps(profile, sort_keys=True, separators=(',', ':'))
        if state in states:
            raise ValueError('population_model contains duplicate profiles')
        states.add(state)
        model.append({'profile': dict(profile), 'weight': float(weight)})
    total = math.fsum(r['weight'] for r in model)
    for row in model:
        row['weight'] /= total
    return model, fields or []


def analyze_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """Analyze an ordered disclosure series using conditional event surprisal.

    The outcome -log2(P(new facts | recipient's accumulated known facts))
    is conditional pointwise information in bits, not a population-estimated
    clinical re-identification probability or a proof of complete monitoring.
    """
    if not isinstance(scenario, dict):
        raise ValueError('Scenario must be a JSON object')
    model, fields = _read_model(scenario)
    allowed = set(fields)
    identity = scenario.get('scenario_id', 'UNSPECIFIED')
    if not isinstance(identity, str) or not identity.strip():
        raise ValueError('scenario_id must be nonempty')
    patient_reference = scenario.get('patient_reference', 'LOCAL-REFERENCE')
    if not isinstance(patient_reference, str) or not patient_reference.strip():
        raise ValueError('patient_reference must be nonempty')
    actual = _require_facts(scenario.get('actual_profile'), allowed, 'actual_profile')
    if set(actual) != allowed:
        raise ValueError('actual_profile must specify all modeled attributes')
    if not _posterior(model, actual)[0]:
        raise ValueError('actual_profile has no support in population_model')

    priors = scenario.get('recipient_prior', {})
    preferences = scenario.get('recipient_preferences', {})
    releases = scenario.get('releases')
    if not isinstance(priors, dict) or not isinstance(preferences, dict) or not isinstance(releases, list):
        raise ValueError('recipient_prior, recipient_preferences and releases must use the expected JSON types')
    if not releases:
        raise ValueError('At least one disclosure is required')
    labels = scenario.get('attribute_labels', {})
    if not isinstance(labels, dict) or (set(labels) - allowed) or not all(isinstance(x, str) for x in labels.values()):
        raise ValueError('attribute_labels must map modeled attributes to labels')

    known: dict[str, dict[str, Any]] = {}
    baseline_mass: dict[str, float] = {}
    for recipient, prior in priors.items():
        if not isinstance(recipient, str) or not recipient.strip():
            raise ValueError('Recipient identifiers must be nonempty')
        _require_facts(prior, allowed, f'prior knowledge of {recipient}')
        if not _matches(actual, prior):
            raise ValueError(f'Prior knowledge contradicts the reference profile for {recipient}')
        known[recipient] = dict(prior)
        _, baseline_mass[recipient] = _posterior(model, prior)
        if baseline_mass[recipient] <= 0:
            raise ValueError(f'No supported baseline profiles for {recipient}')

    for recipient, fields_allowed in preferences.items():
        if not isinstance(recipient, str) or not recipient.strip() or not isinstance(fields_allowed, list):
            raise ValueError('recipient_preferences requires lists of permitted attribute names')
        if any(not isinstance(x, str) for x in fields_allowed) or set(fields_allowed)-allowed:
            raise ValueError(f'Unknown preference attribute for {recipient}')

    # Embed full analysis assumptions in a context digest. Every receipt commits
    # to this digest; changes in analytical inputs invalidate retained receipts.
    context = {
        'scenario_id': identity,
        'patient_reference': patient_reference,
        'actual_profile': actual,
        'recipient_prior': priors,
        'recipient_preferences': preferences,
        'population_model': model,
        'attribute_labels': labels,
    }
    context_sha = canonical_hash(context)
    events: list[dict[str, Any]] = []
    previous_sha = ZERO_HASH
    event_ids: set[str] = set()
    for sequence, release in enumerate(releases, start=1):
        if not isinstance(release, dict) or 'recipient' not in release or 'facts' not in release:
            raise ValueError(f'Disclosure {sequence} requires recipient and facts')
        recipient = release['recipient']
        if not isinstance(recipient, str) or not recipient.strip():
            raise ValueError(f'Disclosure {sequence} has an invalid recipient')
        facts = _require_facts(release['facts'], allowed, f'disclosure {sequence}')
        if not facts or not _matches(actual, facts):
            raise ValueError(f'Disclosure {sequence} is empty or conflicts with reference profile')
        event_id = release.get('event_id', f'EVT-{sequence:03d}')
        if not isinstance(event_id, str) or not event_id.strip() or event_id in event_ids:
            raise ValueError('Every disclosure event ID must be unique and nonempty')
        event_ids.add(event_id)
        purpose = release.get('purpose', 'Not specified')
        channel = release.get('channel', 'Not specified')
        if not isinstance(purpose, str) or not isinstance(channel, str):
            raise ValueError('Disclosure purpose and channel must be strings')
        if recipient not in known:
            known[recipient] = {}
            baseline_mass[recipient] = 1.0
        before_rows, before_mass = _posterior(model, known[recipient])
        next_known = dict(known[recipient])
        next_known.update(facts)
        after_rows, after_mass = _posterior(model, next_known)
        if before_mass <= 0 or after_mass <= 0:
            raise ValueError('A disclosure is incompatible with the specified model')
        incremental = -math.log2(after_mass / before_mass)
        cumulative = -math.log2(after_mass / baseline_mass[recipient])
        before_entropy = _entropy(before_rows, before_mass)
        after_entropy = _entropy(after_rows, after_mass)
        inferred = []
        for field in fields:
            if field in facts or field in known[recipient]:
                continue
            target_value = actual[field]
            was = _marginal(before_rows, before_mass, field, target_value)
            now = _marginal(after_rows, after_mass, field, target_value)
            if abs(now - was) >= 0.01:
                inferred.append({
                    'attribute': field,
                    'reference_value': target_value,
                    'probability_before': _rounded(was),
                    'probability_after': _rounded(now),
                    'percentage_point_change': round((now - was) * 100, 3),
                })
        if recipient not in preferences:
            preference_status = 'not_configured'
            outside = []
        else:
            outside = sorted(set(facts) - set(preferences[recipient]))
            preference_status = 'review' if outside else 'within_preferences'
        event = {
            'sequence': sequence,
            'event_id': event_id,
            'recipient': recipient,
            'purpose': purpose,
            'channel': channel,
            'disclosed_attributes': dict(sorted(facts.items())),
            'newly_declared_attributes': sorted(set(facts) - set(known[recipient])),
            'incremental_information_bits': _rounded(max(0.0, incremental)),
            'cumulative_information_bits': _rounded(max(0.0, cumulative)),
            'supported_candidate_profiles_before': len(before_rows),
            'supported_candidate_profiles_after': len(after_rows),
            'posterior_entropy_before_bits': _rounded(before_entropy),
            'posterior_entropy_after_bits': _rounded(after_entropy),
            'model_implied_probability_shifts': inferred,
            'preference_status': preference_status,
            'attributes_outside_preferences': outside,
            'analysis_context_sha256': context_sha,
            'previous_receipt_sha256': previous_sha,
        }
        event['receipt_sha256'] = canonical_hash(event)
        previous_sha = event['receipt_sha256']
        events.append(event)
        known[recipient] = next_known

    recipient_summary = []
    for recipient in sorted({e['recipient'] for e in events}):
        related = [e for e in events if e['recipient'] == recipient]
        recipient_summary.append({
            'recipient': recipient,
            'event_count': len(related),
            'cumulative_information_bits': related[-1]['cumulative_information_bits'],
            'attributes_known_after_events': sorted(known[recipient]),
            'events_for_review': sum(e['preference_status'] == 'review' for e in related),
        })
    report = {
        'project': 'TwinPrivacy', 'version': VERSION,
        'scenario_id': identity, 'patient_reference': patient_reference,
        'analysis_basis': 'weighted joint-profile distribution',
        'measure': 'conditional pointwise disclosure information (bits)',
        'attribute_labels': labels,
        'analysis_context': context,
        'analysis_context_sha256': context_sha,
        'population_profile_count': len(model),
        'event_count': len(events), 'recipient_summary': recipient_summary,
        'events': events, 'final_receipt_sha256': previous_sha,
    }
    report['report_sha256'] = canonical_hash(report)
    return report


def verify_analysis(report: Any, trusted_anchor: str | None = None) -> bool:
    """Verify internal hashes, including the original assumptions and optional external anchor.

    A valid chain does not prove completeness, event origin or legal compliance.
    """
    if not isinstance(report, dict) or not isinstance(report.get('events'), list):
        return False
    if report.get('report_sha256') != canonical_hash({k:v for k,v in report.items() if k != 'report_sha256'}):
        return False
    context = report.get('analysis_context')
    if not isinstance(context, dict):
        return False
    sha = canonical_hash(context)
    if report.get('analysis_context_sha256') != sha:
        return False
    previous = ZERO_HASH
    for sequence, event in enumerate(report['events'], start=1):
        if not isinstance(event, dict) or event.get('sequence') != sequence:
            return False
        if event.get('analysis_context_sha256') != sha or event.get('previous_receipt_sha256') != previous:
            return False
        claimed = event.get('receipt_sha256')
        if not isinstance(claimed, str) or claimed != canonical_hash({k: v for k, v in event.items() if k != 'receipt_sha256'}):
            return False
        previous = claimed
    if report.get('final_receipt_sha256') != previous:
        return False
    if trusted_anchor is not None and previous != trusted_anchor.strip():
        return False
    return True
