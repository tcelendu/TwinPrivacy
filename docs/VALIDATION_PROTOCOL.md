# TwinPrivacy: computational validation protocol

**Version 0.6.0 | 7 November 2026 | Scope: structured sharing events**

## Research objective

To assess whether the TwinPrivacy implementation correctly calculates recipient-conditioned disclosure information and information shifts under an explicitly specified joint probability model, and whether hash-linked receipts detect altered stored histories when the original terminal receipt is retained separately.

## Research questions

1. Does TwinPrivacy reproduce conditional pointwise information calculated by a separate direct-probability enumerator to within 0.000001 bits?
2. Does the software avoid attributing additional information to records that repeat facts already available to a given recipient?
3. Does allowing dependencies among clinical attributes change the inferred information exposure compared with an independent-attribute reference model holding marginals constant?
4. Do specified modifications to a stored disclosure history fail integrity verification against a retained terminal digest?

These questions concern **algorithm behavior under a stated probabilistic model**. They are not clinical outcome, compliance or real-world privacy effectiveness claims.

## Study design and dataset

- **Dataset:** 512 fully synthetic clinical profiles, sampled with Python `random.Random` and fixed seed **20261107**. Each record is assigned a `SYN-TP` identifier indicating its nonclinical origin.
- **Model:** 16 weighted combinations of four Boolean attributes—type 2 diabetes, chronic kidney disease, asthma and medication-allergy status—from `examples/privacy_verification_scenario.json`.
- **Source of weights:** author-specified demonstration parameters. No clinical dataset was used to estimate prevalence or correlations. The values must not be interpreted as empirical epidemiological estimates.
- **Additional clinical context:** generated age, HbA1c, eGFR, FEV1/FVC and an allergy label. The engine does **not** analyze these numerical/contextual columns. In particular, a single synthetic eGFR reading is not a clinical diagnosis of CKD.
- **Disclosure design:** eight structured event templates per profile (three recipients, repeated release, recipient prior knowledge, and declared preference rules), yielding **4,096 events**. Generated facts and priors are internally consistent with the selected profile.
- **Data access:** No patient recruitment, records or protected health information were used.

## Outcomes and comparisons

### Primary outcome: numerical correctness

For each event, the independently implemented reference routine calculates

`I_event = log2(P(prior known) / P(prior known AND released facts))`

and cumulative information relative to the same recipient's initial known facts, by directly enumerating compatible weighted states. The reference code does not use the TwinPrivacy posterior, entropy or hashing functions. The primary outcome is the maximum absolute difference against TwinPrivacy's six-decimal output. **Pass threshold: < 0.000001 bits.**

For each of 4,096 events, two values are checked (incremental and cumulative): **8,192 pairwise comparisons**.

### Deterministic behavioral checks

- Re-disclosure of the same clinical attribute value to the same recipient contributes 0 new conditional bits.
- A fact explicitly listed in a recipient's prior knowledge contributes 0 new conditional bits when repeated.
- Preference flags agree with an independent set-membership rule based on the stated recipient preferences.
- Hash-linked event history and analytical context are checked against a retained reference digest.

### Comparator A: simple access-event counting

The event-count approach registers each release as an event. TwinPrivacy retains each event in the log but assigns zero **additional modeled information** to repeats and prior-known facts. The two measurements have different units; no cross-unit accuracy claim is made.

### Comparator B: independence ablation

A 16-state product distribution is constructed using the same marginal probabilities as the correlated model while assuming the four attributes are independent. Run identical disclosures under both models and compare:

- the absolute probability change for CKD after learning diabetes status;
- the absolute differences in incremental information values across all events.

This reveals **sensitivity to model assumptions**, not superiority over a real-world baseline or an inferred causal relationship.

### Receipt adversarial checks

Mutate an event's attribute, remove an event, reorder two events, alter the analysis model, and construct a regenerated alternative event history. Check each altered record against the original terminal receipt digest. Demonstrate separately that an internally consistent regenerated record can validate **without** the original trusted external anchor. This is essential for correct interpretation of the security properties.

## Reproduction

Requirements: Python 3.11 or newer; standard library only.

```bash
python reproduce.py
```

Outputs:

- `data/synthetic_clinical_profiles.csv`
- `data/DATA_PROVENANCE.json`
- `evidence/results/validation_results.json`
- `evidence/results/profile_state_counts.csv`
- `evidence/results/VALIDATION_SUMMARY.md`
- `evidence/results/VALIDATION_REPORT.html`
- `outputs/patient_disclosure_statement.html`

The command also runs the complete unittest suite and produces the original reference analysis outputs.

## Interpretation and validity boundaries

This validation has an **in-model oracle**: the same declared joint probability model informs the example generator and independent reference computations. Therefore agreement is evidence of implementation correctness, not external validation of the chosen model. The specified distributions, profile generator, and deterministic test cases cannot provide unbiased estimates of clinical sensitivity, calibration, security under a live adversary, population generalizability, or patient benefit.

The demonstration does not process free text or images, does not prove that all real-world accesses are logged, and cannot authenticate an event's origin from hash chaining alone. It does not implement differential privacy or a composable worst-case privacy guarantee.

## Reproducible reporting principles

All tabulated findings are computed from the repository. No statistical significance tests are reported because the experiment is a deterministic functional evaluation of generated inputs rather than a random clinical sample designed to estimate population effects. No institutional review board approval, patient recruitment, or clinical follow-up is claimed.
