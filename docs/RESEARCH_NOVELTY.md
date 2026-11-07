# Scientific positioning and novelty assessment

**TwinPrivacy | Version 0.6.0 | Evidence-linked prior-art review (7 November 2026)**

## Problem addressed

A patient may receive a list of data-sharing events but still be unable to assess how much *additional* health information each recipient could infer from those releases. TwinPrivacy investigates a patient-facing disclosure ledger that conditions a recorded release on the recipient's specified prior knowledge, tracks information across multiple releases, flags departures from stated sharing preferences, and verifies retained records using a hash chain and an independently preserved receipt anchor.

**The implemented contribution is an integration and reproducible evaluation of known analytical and record-integrity concepts in a health-information sharing workflow.** The present evidence does not establish a novel privacy metric, first-ever system, formal security guarantee, or clinically validated solution.

## Position relative to established research and standards

| Prior approach | Established function | TwinPrivacy's current relationship and remaining limitation |
| --- | --- | --- |
| **HL7 FHIR AuditEvent** | Structured audit events describe what happened, with involved agents, purposes and context; patient-facing accounting reports are contemplated. | TwinPrivacy provides a local patient-readable **information accounting** layer for supplied structured event records. It does not implement FHIR ingestion, verify audit completeness or claim patient-facing logs are new. |
| **Quantitative information flow / g-leakage** | Prior work quantifies information disclosure using attacker gain and vulnerability and recognizes different leakage measures. | TwinPrivacy uses **conditional pointwise surprisal** under a user-supplied discrete joint model; this is a familiar information-theoretic quantity, not g-leakage or a novel theorem. |
| **Pufferfish privacy** | Formalizes secrets, prior beliefs, dependent data and prior disclosures; later research analyzes composition. | Recipient prior knowledge and correlated health attributes are relevant to both, but TwinPrivacy does **not** implement or prove Pufferfish privacy or a sound compositional upper bound. |
| **Differential privacy and privacy odometers** | DP places formal constraints on release mechanisms; odometers track adaptive privacy-loss parameters. | TwinPrivacy does not add noise, define neighboring datasets, compute DP epsilon or provide a DP privacy budget. Its observed disclosure surprisal must not be confused with a DP privacy-loss parameter. |
| **Hash-linked audit histories** | Cryptographic digests can make retained records tamper-evident when the verification reference is trusted. | TwinPrivacy hashes the analytical context and event chain. It does not prove record completeness, authorship, timing, or remote attestation; replacing both history and an untrusted anchor can evade detection. |

## Candidate contribution for a research proposal

**A recipient-calibrated, patient-facing disclosure-verification workflow that combines** (i) sequential accounting of structured health-attribute releases, (ii) prior-knowledge conditioning, (iii) explicit sensitivity to modeled clinical correlations, (iv) patient sharing-preference review and (v) portable integrity-checked receipts.

The candidate novelty should be described as **an application-specific integration and experimental research direction**, subject to a deeper systematic search and comparison with existing implementations. It is not yet a demonstrated theoretical or technical advance over the strongest published methods.

## Empirical evidence in this repository

`evidence/results/VALIDATION_SUMMARY.md` supplies reproducible results across 512 synthetic profiles and 4,096 events, compared with an independently coded finite-state reference calculator, a simple event count and an independence ablation. These tests demonstrate correct calculations within the specified model and sensitivity to correlation assumptions. They do not establish that TwinPrivacy is more secure or clinically effective than existing systems.

## Research gap that could justify grant funding

A stronger and potentially distinct scientific contribution would require **at least one falsifiable advance** beyond this prototype, such as:

1. A patient-checkable method for confirming that a disclosure ledger is **complete**, rather than merely tamper-evident, with explicit trust assumptions and adversarial tests.
2. A formally specified compositional bound for **free-text, derived figures and repeated disclosures** that allows changes in recipient knowledge and quantifies uncertainty in the assumed population model.
3. Integration with real-world audit interfaces (e.g., standards-based FHIR AuditEvent export) plus adversarial evaluation against patient-attribute inference attacks and independent implementations.

These are **future research questions, not implemented features**. The call expressly prioritizes verification by the affected individual, cumulative sharing disclosures, free text and recipient knowledge.

## Primary sources / standards

1. HL7 International. *FHIR R5 AuditEvent.* https://hl7.org/fhir/auditevent.html
2. Alvim MS, Chatzikokolakis K, Palamidessi C, Smith G. *Measuring Information Leakage Using Generalized Gain Functions.* IEEE CSF, 2012. https://doi.org/10.1109/CSF.2012.26
3. Kifer D, Machanavajjhala A. *Pufferfish: A Framework for Mathematical Privacy Definitions.* ACM TODS, 2014. https://doi.org/10.1145/2514689
4. Bai J, He G, Gu X, Kifer D, Maeng K. *Composition for Pufferfish Privacy.* PVLDB, 2026. https://doi.org/10.14778/3828612.3828632
5. Rogers R, Roth A, Ullman J, Vadhan S. *Privacy Odometers and Filters: Pay-as-You-Go Composition.* NeurIPS, 2016. https://papers.neurips.cc/paper/2016/hash/58c54802a9fb9526cd0923353a34a7ae-Abstract.html
6. OpenDP. *Typical Workflow; differential privacy parameters.* https://docs.opendp.org/en/stable/getting-started/typical-workflow.html
7. Open Science Foundation. *Verifiable privacy for digital health twins* open call, 2026. https://opening.science/apply/health-twin-privacy-2026/

**Review scope:** focused, cited comparison of highly relevant primary sources and standards. It is **not** a systematic literature review or a patent/novelty clearance.
