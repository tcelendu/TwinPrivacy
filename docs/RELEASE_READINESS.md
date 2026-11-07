# Repository release readiness

## Completed and reproducible

- MIT-licensed source; Python standard library only
- Self-contained structured disclosure scenario and declared 16-state model
- Deterministic synthetic clinical cohort with source, seed and limitations recorded
- Independent finite-state reference check for incremental and cumulative information
- Recipient-aware repeats, prior-knowledge cases and preference-flag checks
- Independence ablation and basic tamper-evidence challenge suite
- Patient-facing HTML report and JSON research evidence
- Single-command regeneration with `python reproduce.py`

## GitHub publication packaging completed (not yet published)

- Added a CI workflow that will run after GitHub publication.
- Added MIT/CC0/CC BY 4.0 reuse terms, data dictionary and publication instructions.
- Clarified provenance of worked clinical case narratives.

## Remaining before public scientific claims or grant submission

- [ ] Technical review of model, threat assumptions and disclosure metrics by a privacy/security specialist
- [ ] Reproduce outputs independently on a second computer and record environment/version
- [ ] Decide whether `SYN-TP` data and specified weights are adequate for the stated research question
- [ ] Critically compare with the best available patient-centred audit/disclosure systems, not only event counts
- [ ] Establish an actual research advance beyond an integration of existing concepts
- [ ] Build a credible solution for detecting **omitted events**; hash chains currently do not do this
- [ ] Extend beyond structured Boolean attributes to text/derived information if this is the promised contribution
- [ ] Establish third-party trusted anchor or stronger provenance architecture
- [ ] Review all README, examples and clinical narratives for accurate provenance and supported claims
- [ ] Add maintainers' real names, contacts, citation metadata and repository URL after approval
- [ ] Conduct open-source licence review for any new third-party data or code

This checklist is not evidence that any external entity has approved or certified the work.
