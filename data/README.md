# Dataset documentation and reuse

The file `synthetic_clinical_profiles.csv` contains **512 algorithmically
generated records**, created using the fixed seed **20261107** and the
specified 16-state profile model in
[`../examples/privacy_verification_scenario.json`](../examples/privacy_verification_scenario.json).
Source, generation approach, and scientific limits are recorded in
[`DATA_PROVENANCE.json`](DATA_PROVENANCE.json) and
[`../docs/VALIDATION_PROTOCOL.md`](../docs/VALIDATION_PROTOCOL.md).

## Data dictionary

| Column | Type and interpretation | Used directly in the privacy engine? |
| --- | --- | --- |
| `record_id` | Generated identifier, `SYN-TP-NNNN` | No |
| `age_years` | Age in years, generated from specified rules | No |
| `diabetes` | Binary model attribute (0/1) | Yes |
| `chronic_kidney_disease` | Binary model attribute (0/1) | Yes |
| `asthma` | Binary model attribute (0/1) | Yes |
| `drug_allergy` | Binary model attribute (0/1) | Yes |
| `hba1c_percent` | Generated HbA1c percentage for narrative context | No |
| `egfr_mL_min_1_73m2` | Generated filtration estimate, mL/min/1.73 m² | No |
| `fev1_fvc_ratio` | Generated ratio | No |
| `medication_allergy_label` | Generated categorical allergy description | No |

The modeled attributes arise from a stipulated joint distribution; the
context variables are constructed values. The files do not represent
sampled patients, observed healthcare encounters, or measured prevalence.
Do not infer a real clinical diagnosis from the generated numerical fields.

## Reproduction

From the root of the repository run `python reproduce.py`. This regenerates
the table and the validation evidence using the standard Python library.

## Licence

The generated dataset is offered under **CC0 1.0**, as stated in [LICENSE](LICENSE).
The software that produces it is under the repository's **MIT** licence. Research documentation is under **CC BY 4.0**.
