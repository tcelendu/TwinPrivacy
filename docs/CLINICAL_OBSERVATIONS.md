# Clinical case narratives and disclosure-accounting results


> **Dataset provenance.** The three clinical case narratives below are constructed
> research examples based on designed attribute combinations and disclosure
> sequences. They are **not patient case reports or independently collected
> clinical observations**. Their calculated disclosure results are produced by
> the included software using the stated analytical assumptions.

## Case presentation and analytical context

The three case presentations below provide clinically detailed examples of the documentation, sequential information-sharing records and analytical reporting used in TwinPrivacy. The accompanying disclosure metrics are calculated by the repository from the structured input files.

Only **diabetes status, asthma status and recorded drug-allergy status** are evaluated by the current information model. Clinical observations such as examination findings, laboratory results, treatment history and longitudinal course are documented to establish the case narrative; they are not automatically incorporated into the reported information-gain values.

## Individual clinical case presentations

### Case 1: Asthma and antimicrobial allergy in a shared-care pathway (TP-CL-01)

**Clinical presentation and assessment.** A 42-year-old woman was reviewed in a respiratory clinic after six weeks of increasingly frequent wheeze, nocturnal cough and exertional dyspnoea against a seven-year history of asthma. At assessment, blood pressure was 124/78 mmHg, pulse 82 beats/min, respiratory rate 16 breaths/min and peripheral oxygen saturation 97% on room air. Mild expiratory wheeze was present without increased work of breathing. Pre-bronchodilator forced expiratory volume in one second (FEV₁) was 2.08 L, increasing to 2.43 L after bronchodilator administration (absolute increase 350 mL; 16.8% relative to baseline). Blood eosinophils were 0.32 × 10⁹/L and HbA1c was 5.5%. These findings supported the established diagnosis of asthma.

Medication reconciliation identified a previous generalized urticarial reaction occurring approximately 30 minutes after amoxicillin exposure. No airway compromise or hypotension had been documented; no subsequent formal allergy testing was available. The reaction was therefore retained as a *reported immediate-type antibiotic hypersensitivity*, rather than classified as immunologically confirmed penicillin allergy. Inhaler technique and adherence were reviewed. At six-week follow-up, nocturnal symptoms were less frequent, and the medication-safety alert remained visible to the respiratory team.

**Information-sharing pathway.** The respiratory service transferred an asthma-status field and a medication-safety flag to a clinical researcher. The asthma field was transmitted twice to that same recipient. The treating respiratory clinician had pre-existing knowledge of the asthma diagnosis, but not the recorded antibiotic reaction. The five disclosure events were assessed sequentially against these distinct baseline knowledge states.

**Recorded disclosure results.**

| Event | Recipient | Attribute communicated | Incremental gain (bits) | Cumulative gain (bits) |
| ---: | --- | --- | ---: | ---: |
| 1 | `clinical_researcher` | asthma status: present | 1.0 | 1.0 |
| 2 | `clinical_researcher` | asthma status: present | 0.0 | 1.0 |
| 3 | `clinical_researcher` | recorded drug-allergy status: present | 1.0 | 2.0 |
| 4 | `respiratory_clinician` | asthma status: present | 0.0 | 0.0 |
| 5 | `respiratory_clinician` | recorded drug-allergy status: present | 1.0 | 1.0 |

**Interpretation.** The first disclosure to the research recipient reduced the eight possible states to four (1.0 bit). Repeating asthma status to the same recipient produced no further reduction. Release of the allergy-status field reduced the remaining states to two, bringing cumulative gain to 2.0 bits. The respiratory clinician gained no additional information from the already-known asthma diagnosis but acquired 1.0 bit when the allergy-status field was communicated.


### Case 2: Type 2 diabetes surveillance across clinical and research recipients (TP-CL-02)

**Clinical presentation and assessment.** A 59-year-old man with a nine-year history of type 2 diabetes attended routine metabolic review because home glucose readings remained above target. He was receiving metformin and an additional glucose-lowering agent, with medication adherence, nutrition and activity reviewed during the visit. Blood pressure was 146/86 mmHg and body mass index was 29.4 kg/m². HbA1c was 8.2%, fasting plasma glucose 174 mg/dL, serum creatinine 0.98 mg/dL, estimated glomerular filtration rate 88 mL/min/1.73 m² and urinary albumin-to-creatinine ratio 16 mg/g. No active foot ulceration was identified, and bedside protective sensation was preserved. There was no reported asthma history or recorded medication hypersensitivity.

The index assessment characterized glycaemic control as above the individualized treatment target, prompting medication and self-management review. HbA1c at approximately three months was 7.5%. The disclosure analysis evaluated the diagnosis and the documented absence of asthma and drug allergy; the glucose measurements, treatment regimen and follow-up outcome remained clinical context and did not contribute to the model's three-attribute information measure.

**Information-sharing pathway.** A structured record extract was sent to a research analytics service that had no declared baseline knowledge of the three attributes. The treating diabetes clinician was already aware of the diabetes diagnosis. The record sequence included diabetes status, the absence of asthma, drug-allergy status and a repeat notification of diabetes to the analytics service.

**Recorded disclosure results.**

| Event | Recipient | Attribute communicated | Incremental gain (bits) | Cumulative gain (bits) |
| ---: | --- | --- | ---: | ---: |
| 1 | `research_analytics` | type 2 diabetes status: present | 1.0 | 1.0 |
| 2 | `diabetes_clinician` | type 2 diabetes status: present | 0.0 | 0.0 |
| 3 | `research_analytics` | asthma status: absent | 1.0 | 2.0 |
| 4 | `research_analytics` | recorded drug-allergy status: absent | 1.0 | 3.0 |
| 5 | `diabetes_clinician` | recorded drug-allergy status: absent | 1.0 | 1.0 |
| 6 | `research_analytics` | type 2 diabetes status: present | 0.0 | 3.0 |

**Interpretation.** The analytics recipient acquired 1.0 bit each from the diagnosis of diabetes, the recorded absence of asthma and the recorded absence of drug allergy, reaching 3.0 cumulative bits. Repetition of the diabetes field added 0.0 bits. The diabetes clinician gained no new information from the established diagnosis but gained 1.0 bit from the drug-allergy field. The numerical findings reflect the three-field specification and do not quantify clinical severity or real-world re-identification probability.


### Case 3: Multimorbidity with recipient-specific baseline knowledge (TP-CL-03)

**Clinical presentation and assessment.** A 67-year-old woman with type 2 diabetes and persistent asthma attended an integrated primary-care visit following transfer between clinical services. The medication review confirmed glucose-lowering treatment and inhaled controller therapy. She reported a previous urticarial reaction after a penicillin-class antibiotic, although confirmatory allergy evaluation had not been completed. At presentation, blood pressure was 132/80 mmHg, pulse 78 beats/min, peripheral oxygen saturation 96% and body mass index 27.8 kg/m². Mild expiratory wheeze was noted. HbA1c was 7.6%, estimated glomerular filtration rate 62 mL/min/1.73 m² and pre-bronchodilator FEV₁ 1.51 L (68% predicted).

Her record therefore contained clinically relevant information across metabolic, respiratory and medication-safety domains. The documented antibiotic reaction was preserved as an allergy alert pending clarification. The privacy analysis focused on how the same diagnosis and allergy-status entries were disclosed to pharmacy, primary-care and outcomes-analytics recipients, each with a different set of declared prior facts.

**Information-sharing pathway.** The pharmacy service already held the antibiotic allergy alert; the primary-care recipient already knew the diabetes diagnosis; and the outcomes-analytics recipient had no declared baseline knowledge. Each recipient was analysed independently. The episode included repeated data fields as well as first-time disclosures of other clinical attributes.

**Recorded disclosure results.**

| Event | Recipient | Attribute communicated | Incremental gain (bits) | Cumulative gain (bits) |
| ---: | --- | --- | ---: | ---: |
| 1 | `pharmacy_service` | recorded drug-allergy status: present | 0.0 | 0.0 |
| 2 | `pharmacy_service` | type 2 diabetes status: present | 1.0 | 1.0 |
| 3 | `primary_care` | type 2 diabetes status: present | 0.0 | 0.0 |
| 4 | `outcomes_analytics` | type 2 diabetes status: present | 1.0 | 1.0 |
| 5 | `outcomes_analytics` | asthma status: present | 1.0 | 2.0 |
| 6 | `outcomes_analytics` | asthma status: present | 0.0 | 2.0 |
| 7 | `primary_care` | recorded drug-allergy status: present | 1.0 | 1.0 |

**Interpretation.** The pharmacy service gained 0.0 bits from repetition of the allergy alert but 1.0 bit from the diabetes-status field. The analytics recipient acquired 2.0 cumulative bits from the diabetes and asthma fields, with no further increment when asthma status was repeated. The primary-care service gained no information from its established diabetes knowledge but gained 1.0 bit from the recorded antibiotic-reaction field. These differences arise from recipient-specific prior information and event order.

## Comparative clinical and computational findings

| Case | Clinical focus | Disclosure events | Highest recipient cumulative gain | Receipt check |
| --- | --- | ---: | ---: | --- |
| TP-CL-01 | Asthma and antimicrobial allergy in a shared-care pathway | 5 | 2.0 bits | Passed |
| TP-CL-02 | Type 2 diabetes surveillance across clinical and research recipients | 6 | 3.0 bits | Passed |
| TP-CL-03 | Multimorbidity with recipient-specific baseline knowledge | 7 | 2.0 bits | Passed |

Across the three case analyses, **18 disclosure events** were processed and included in hash-linked event receipts. Repeated fields contributed zero additional information when the relevant recipient already possessed those facts, while the first disclosure of an unknown binary attribute contributed 1.0 bit under the specified equally weighted eight-state model. Each case passed the software receipt-chain integrity check. This verifies the internal continuity of recorded disclosures, not the completeness of actual access logging.

## How to document and analyse your own clinical records

1. **Source documentation.** Establish the encounter setting and obtain the permitted source material. Record the clinical condition, presenting symptoms, comorbidities, medication exposure, investigations and relevant follow-up with accurate units and dates.
2. **Clinical abstraction.** Write the case chronology from the source record, distinguishing a confirmed diagnosis from a reported adverse drug reaction, suspected condition or unverified history.
3. **Define the disclosure question.** Identify the data fields to be measured and the specific services or users that received them. Do not infer a disclosure solely from the presence of a field in the patient chart.
4. **Establish recipient baselines.** Record which facts each recipient already knew before the event sequence and the evidence supporting that designation.
5. **Construct the event sequence.** Enter the ordered disclosures in `examples/clinical_case_series.json`; use `true` or `false` for the three currently supported attributes.
6. **Reproduce the computational output.** Run `python case_series.py --format json`, compare each recipient’s incremental and cumulative values, and verify the hash-linked receipts.
7. **Report scope precisely.** Separate observed clinical facts from privacy-model inputs and calculated outcomes; document any unobserved disclosures or uncertainty about recipients’ prior knowledge.

## Reproducibility

```bash
python case_series.py
python case_series.py --format json
python -m unittest -v
```

The case input, chronological disclosure events and machine-readable computed outputs are supplied in `examples/clinical_case_series.json` and `examples/clinical_case_results.json`.
