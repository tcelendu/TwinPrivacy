# TwinPrivacy | Reproducible validation findings

**Evaluation design.** Deterministic, in-model computational validation using 512 generated clinical profiles, 4096 structured disclosure events and a specified 16-state joint probability distribution. The clinical records and model parameters are synthetic and are not empirical clinical evidence.

## Primary computational results

| Evaluation | Reproducible finding |
| --- | ---: |
| Patient profiles | 512 |
| Profile states represented | 16 / 16 |
| Disclosure events processed | 4096 |
| Independent reference comparisons | 8192 |
| Maximum absolute deviation from independent enumerator | 0.000000499 bits |
| Reference calculations within prespecified 0.000001-bit tolerance | Yes |
| Repeated disclosures correctly assigned zero incremental bits | 512 / 512 |
| Attributes already known to recipient assigned zero incremental bits | 512 / 512 |
| Preference flag decisions matching independently implemented rules | 4096 / 4096 |
| CKD probability-shift outputs independently checked | 512 |

## Comparator analyses

**Event-count baseline.** A naïve count of release events registers each of the 512 duplicate disclosures and 512 prior-known disclosures as another event. TwinPrivacy instead reports zero additional conditional surprisal for these identical facts. Event count and information bits are distinct quantities and should not be interpreted as comparable measurements.

**Independence ablation.** When the same profile marginals are retained but all four clinical attributes are treated as independent, the mean absolute modeled chronic-kidney-disease probability shift after diabetes disclosure is 0.000000 percentage points, compared with 6.549063 percentage points under the specified correlated model. Across all events, the maximum absolute difference in incremental information between the two assumptions is 1.296191 bits. **These findings demonstrate model sensitivity, not greater real-world predictive accuracy.**

## Integrity challenge results

| Challenge | Observed outcome |
| --- | --- |
| Alter event attribute | Observed |
| Remove recorded event | Observed |
| Reorder events | Observed |
| Alter analysis model | Observed |
| Recomputed history against original anchor | Observed |
| Rewritten history without external anchor passes | Observed |

The final row demonstrates a deliberate limitation: when the trusted external receipt anchor is absent, a replacement history with newly calculated internal hashes can verify as internally consistent. Hash-linked receipts **do not authenticate the origin or completeness of logged events**.

## Interpretation

Under the supplied assumptions, the implementation accurately reproduces conditional pointwise information values using an independently written finite-state enumeration, preserves recipient-specific knowledge, and detects basic tampering against a retained hash anchor. This is computational validation **within a specified analytical model**. It does not establish clinical sensitivity or specificity, a universal privacy bound, completeness of access auditing, or validation against real-life data.

Run `python reproduce.py` from the repository root. See `docs/VALIDATION_PROTOCOL.md`, `docs/RESEARCH_NOVELTY.md`, and `data/DATA_PROVENANCE.json` for full methods and boundaries.
