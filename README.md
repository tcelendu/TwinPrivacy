# TwinPrivacy

**Patient-verifiable accounting of health-information disclosures**  
**Open-source research software · Version 0.6.1 · Python 3.11+ · MIT code licence**

TwinPrivacy is a reproducible analytical framework for evaluating information disclosed to distinct recipients across digital health services. The software differentiates new disclosures from repeated records, accounts for recipient-specific prior knowledge, detects model-implied shifts in information about related clinical attributes, and produces patient-readable statements supported by hash-linked disclosure receipts.

The repository provides an end-to-end executable workflow: a declared input model, disclosure events, independently testable analytical code, a machine-readable verification record, and an accessible HTML report.

## Reproduce everything with one command

No external dependencies, credentials, accounts or network access are required. Use **Python 3.11 or later** from the repository directory:

```bash
python reproduce.py
```

This command executes the complete automated test suite, recalculates the analytical results, checks the retained receipt chains, and recreates the report files in `outputs/`.

**Open `outputs/patient_disclosure_statement.html` in a web browser.** This is the patient-facing report. It contains a disclosure overview, recipient-specific information totals, a chronological event record, sharing-preference review flags, and explanations of model-implied changes in information about other clinical attributes.

For independent verification of the saved output:

```bash
python verify.py outputs/enhanced_analysis.json outputs/trusted_receipt_anchor.txt
```

The terminal receipt digest should be retained independently before any subsequent changes to the record. Keeping an anchor file alongside the record facilitates reproducibility but does not, by itself, protect against both files being replaced.

## Features

| Component | Function |
| --- | --- |
| Conditional disclosure analysis | Estimates incremental and cumulative pointwise information in bits from a declared weighted joint profile model |
| Recipient-aware modeling | Maintains separate recipient knowledge states and declared baseline information |
| Correlation-sensitive analysis | Identifies model-implied shifts in the probability of attributes not directly disclosed in the current event |
| Repeat recognition | Records zero additional information for an identical statement already known to the same recipient |
| Sharing-preference check | Identifies disclosures outside declared recipient-specific attribute preferences for human review |
| Record verification | Links disclosure receipts with SHA-256 and commits to the analytical context and retained report |
| Patient disclosure statement | Generates a standalone, printable HTML report with no web dependencies |
| Reproduction | Rebuilds reference and clinical-workbook analyses, verifies receipts and runs all automated tests in one command |

## Data and analytical method

All reference clinical profiles and worked case narratives are **generated research examples, not observations from recruited patients**. The enhanced reference scenario models four clinical attributes: diabetes, chronic kidney disease, asthma and medication allergy. A **16-state joint probability model** represents dependencies between these attributes. The probabilities are specified analytical assumptions for reproducible evaluation; they must not be interpreted as observed prevalence estimates. The demonstration uses structured illustrative clinical disclosures and contains no patient identifiers.

For recipient \(r\), let \(K_{r,t-1}\) denote the recorded information held before disclosure \(t\), and \(D_t\) the newly recorded facts. The conditional pointwise information conveyed by the event is:

\[
I_{r,t} = -\log_2 P(D_t\mid K_{r,t-1}).
\]

The cumulative result is calculated relative to the same recipient's declared baseline. The values represent the *surprisal of the recorded information under the specified model*. They do not quantify clinical harms or establish actual patient re-identification risk. For attributes absent from an event, the software separately reports modeled probability changes associated with that event. See [Methods](docs/METHODS.md) for the formal specification and limitations, and the [input specification](docs/INPUT_SPECIFICATION.md) to adapt the model to a separate study.

## Example analytical results

The enhanced example comprises **eight recorded disclosures to three recipients**. It illustrates a repeated diagnosis disclosure contributing no new information, an indirect increase in the modeled probability of kidney disease after diabetes status is disclosed, and two events identified for review against the registered sharing preferences. All results, including the specific bit values, are generated directly by `python reproduce.py`.

The initial clinical case workbook remains in the repository as a separate reference series, preserving structured respiratory, metabolic and multimorbidity narratives and their original three-attribute analyses. These are worked case-documentation examples; their values should not be represented as independently collected clinical findings.

## Repository structure

```text
TwinPrivacy/
├── reproduce.py                     # One-command reproduction and verification
├── verify.py                        # Verify retained output and terminal digest
├── privacy_engine.py                # Weighted, correlation-aware disclosure analysis
├── patient_report.py                # Standalone, patient-facing HTML statement
├── twinprivacy.py                   # Command-line interface and baseline three-attribute model
├── case_series.py                   # Original case-workbook analyses
├── examples/
│   ├── privacy_verification_scenario.json
│   ├── clinical_disclosure_scenario.json
│   ├── clinical_case_series.json
│   ├── disclosure_report.json
│   └── clinical_case_results.json
├── docs/
│   ├── METHODS.md
│   ├── PROJECT_OVERVIEW.md
│   ├── CLINICAL_OBSERVATIONS.md
│   └── CASE_DOCUMENTATION_WORKFLOW.md
├── outputs/                          # Deterministic reports rebuilt by reproduce.py
├── test_twinprivacy.py
├── test_clinical_cases.py
├── test_privacy_engine.py
├── test_reproduction.py
├── CHANGELOG.md
├── LICENSE
└── README.md
```

### Other useful commands

```bash
# View the weighted scenario in the terminal
python twinprivacy.py --scenario examples/privacy_verification_scenario.json

# Recreate the baseline three-attribute analysis
python twinprivacy.py

# Recreate the clinical case series
python case_series.py

# Run unit tests only
python -m unittest discover -v
```

## Interpretation and boundaries

The software evaluates **supplied recorded disclosures**, not unobserved accesses. Receipt verification detects changes within the retained event history and its analytical context; it does not establish the identity of the original recording party, that all events were logged, or that any sharing complied with a legal consent requirement. The preference check is intended for review rather than an authorization determination. Claims about real-world security, clinical prevalence or regulatory compliance require independent evidence.

This is a research-grade demonstration suitable for methodological assessment and extension, not a validated clinical decision-support system or a production privacy-security product.

## Licences and repository publication

- **Source code and tests:** [MIT licence](LICENSE).
- **Generated profile data and JSON results:** [CC0 1.0](data/LICENSE), with [data dictionary and provenance](data/README.md).
- **Research reports, technical documentation and patient-facing explanatory HTML:** [CC BY 4.0](docs/LICENSE).
- **Public publication:** Follow the [GitHub publication guide](docs/PUBLISH_TO_GITHUB.md). Creating a ZIP does not publish a repository.
- **Automated verification:** [GitHub Actions workflow](.github/workflows/verify.yml) runs the full reproduction command across Python 3.11, 3.12 and 3.13 once the repository is published and Actions is enabled.
- **Research scope and limitations:** See the [validation protocol](docs/VALIDATION_PROTOCOL.md) and [scientific positioning](docs/RESEARCH_NOVELTY.md).

No personal patient data are needed to reproduce the included research results. [Licensing and AI-assistance disclosure](docs/LICENSING_AND_AI_USE.md) documents the file-level permissions and development tools.

## Reproducible research evidence — Version 0.6.0

The same `python reproduce.py` command now generates a deterministic **512-record synthetic clinical cohort**, evaluates **4,096 structured disclosure events**, compares **8,192 information calculations** against a separately implemented finite-state reference routine, performs two explanatory baselines, and tests the limits of cryptographic receipt verification.

Begin with these files:

- [`evidence/results/VALIDATION_SUMMARY.md`](evidence/results/VALIDATION_SUMMARY.md) — reproducible numerical outcomes and comparator analyses
- [`evidence/results/VALIDATION_REPORT.html`](evidence/results/VALIDATION_REPORT.html) — styled report for independent inspection
- [`docs/VALIDATION_PROTOCOL.md`](docs/VALIDATION_PROTOCOL.md) — methods, prespecified outcomes and limitations
- [`docs/RESEARCH_NOVELTY.md`](docs/RESEARCH_NOVELTY.md) — comparison with FHIR AuditEvent, quantitative information flow, Pufferfish, differential privacy and cryptographic audit logs
- [`docs/GRANT_EVIDENCE_BRIEF.md`](docs/GRANT_EVIDENCE_BRIEF.md) — concise, carefully qualified scientific narrative
- [`data/DATA_PROVENANCE.json`](data/DATA_PROVENANCE.json) — provenance of all generated clinical columns

**Scientific interpretation:** The validation provides evidence of numerical implementation correctness under a specified joint model. It does not constitute validation in real patients or proof that all data accesses are recorded. The combined patient-oriented workflow is a candidate research contribution; novelty over existing approaches has not been definitively established.

## Public repository navigation

| Resource | Location |
| --- | --- |
| Source code and automated tests | Root-level `*.py` and `test_*.py` |
| Generated clinical dataset | [`data/`](data/) |
| Methods and validation protocol | [`docs/`](docs/) |
| Example configurations | [`examples/`](examples/) |
| Formal validation results | [`evidence/results/`](evidence/results/) |
| Patient-readable disclosure report | [`outputs/patient_disclosure_statement.html`](outputs/patient_disclosure_statement.html) |
| Publication instructions | [`docs/PUBLISH_TO_GITHUB.md`](docs/PUBLISH_TO_GITHUB.md) |

