# Methods and analytical specification

## Scope

TwinPrivacy measures the information conveyed by an ordered series of **recorded clinical-attribute releases** to distinct recipients. Its units of analysis are (i) each recipient-specific disclosure event and (ii) the recipient's cumulative recorded knowledge relative to a declared baseline. It is a disclosure-accounting implementation, not a substitute for authenticated event capture.

## Input specification and provenance

The enhanced reference scenario in `examples/privacy_verification_scenario.json` specifies a reference patient profile, a 16-state weighted joint distribution covering diabetes, chronic kidney disease, asthma and medication allergy, recipient baseline facts, an ordered disclosure series and optional recipient-specific sharing preferences. The model's probabilities are explicit demonstration assumptions rather than epidemiological rates. Original clinical workbook narratives remain available as worked examples for understanding how clinical documentation could be mapped to the software's limited attribute representation.

Each joint profile has a positive weight and covers all modeled fields. The engine validates values, duplicates, contradictions, unsupported states, malformed recipients and invalid preferences before calculating results. Weights are normalized to sum to one.

## Conditional pointwise information

Let \(X\) denote the complete attribute state, \(K_{r,t-1}\) the facts known to recipient \(r\) before event \(t\), and \(D_t\) the facts contained in the event. The **conditional pointwise information** conveyed by a recorded disclosure is:

\[
I_{r,t} = -\log_2 \Pr(D_t \mid K_{r,t-1})
        = \log_2 \frac{\Pr(K_{r,t-1})}{\Pr(K_{r,t-1}, D_t)}.
\]

Cumulative information is measured relative to the declared baseline \(K_{r,0}\):

\[
C_{r,t} = -\log_2 \Pr(K_{r,t} \mid K_{r,0}).
\]

For consistent events, this measure cannot be negative; it is zero for a repeated fact that adds no additional knowledge to that recipient. The code also reports the Shannon entropy of the candidate profile distribution before and after each event. Unlike conditional pointwise information, the entropy change is not guaranteed to be positive for every realized event.

## Correlation and indirect inference

Unlike the original uniform three-attribute reference model, the enhanced demonstration specifies a joint distribution with correlations. When a recipient learns one attribute, the model may update the probabilities assigned to other attributes that were **not directly released**. For each event, the engine reports changes of at least 1 percentage point in the probability of the reference profile's value of an as-yet-unknown attribute. Such changes represent *model-implied inference potential*, not observed recipient behavior and not verified inference by a real system.

## Recorded sharing preferences

The input can specify the attribute categories declared for each recipient. Events outside these categories are marked `review`; events within them are marked `within_preferences`. Where no preference is provided, the status is `not_configured`. These labels are for patient-facing inspection, not a determination of consent, legal validity or actual authorization.

## Hash-linked disclosure receipts

Every event includes a SHA-256 digest of its canonical JSON representation and the digest of the preceding event. The event also includes a SHA-256 commitment to the analytical context (joint distribution, reference profile, recipient priors and preferences). The complete saved report has an additional content digest. The `verify.py` command rechecks both the linkages and report consistency, with an optional separately retained terminal digest.

These checks demonstrate the internal integrity of the retained input and report. They cannot prove the origin or completeness of a record; a malicious actor holding control of the full record and the only copy of the anchor can replace both. Greater guarantees would require trusted event capture, cryptographic signatures and independent digest anchoring.

## One-command reproducibility

From the repository root, run:

```bash
python reproduce.py
```

The script runs the complete unit test suite, generates the enhanced analysis, rebuilds baseline and clinical-workbook results, checks all receipt histories and writes the following to `outputs/`:

- `enhanced_analysis.json` — full machine-readable analysis and verification context;
- `patient_disclosure_statement.html` — patient-facing event statement;
- `trusted_receipt_anchor.txt` — terminal digest for separate retention;
- `reference_disclosure_report.json` — retained baseline assessment;
- `clinical_case_results.json` — case-workbook analysis;
- `reproduction_manifest.json` — run inventory and result summary.

The default workflow requires only Python 3.11+ and its standard library, with no downloads, API calls, credentials or network access. Automated tests include mathematical consistency, repeated disclosure handling, correlated-attribute inference, baseline recipient knowledge, input validation, event integrity, tampering and HTML escaping.

## Scientific limits and future evaluation

The present system is an inspectable proof-of-method for structured disclosures. Its probabilities are not derived from representative clinical populations. Its clinical context is not parsed from free text, and the engine does not discover undisclosed transfers. It does not independently verify actual consent, real-world recipient knowledge, clinical harms, identity authentication or re-identification risk. These constraints define testable research extensions rather than demonstrated capabilities.
