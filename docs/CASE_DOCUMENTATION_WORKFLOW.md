# Clinical documentation and disclosure analysis | Editorial workflow

## Clinical narrative structure

For every patient encounter, present the clinical setting, chief concern, relevant history, examination, investigations (with units and time points), assessment, management and follow-up. Distinguish **reported symptoms**, **clinician-documented findings**, **laboratory results** and **interpretation**. A suspected allergy should not be described as immunologically confirmed without confirmatory evidence.

## Evidence mapping

Build a private abstraction table linking each narrative fact to the corresponding permitted clinical source, encounter date and recording clinician. The published repository should contain only information authorized for public release. In the accompanying software input, `actual_profile` identifies the three attributes used in the mathematical model, while `recipient_prior` specifies declared baseline knowledge for each recipient and `releases` lists the ordered fields communicated.

## Computational verification

Run the case series and automated tests, confirm the narrative matches the structured input, and validate the output reports. An SHA-256-linked receipt establishes internal integrity of the documented event sequence, but cannot establish that unrecorded disclosures did not occur.

## Manuscript-ready results

Report the number of encounters or cases actually reviewed, the denominator and selection process if applicable, the evidence basis for each recipient's knowledge, the disclosure events included, and the resulting incremental and cumulative measures. State explicitly which clinical data fields were outside the model. Do not transfer worked example values into findings attributed to actual patients without checking them against original source documentation.
