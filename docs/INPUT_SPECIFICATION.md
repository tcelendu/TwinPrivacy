# Input specification and adaptation guide

The enhanced analysis is configured in `examples/privacy_verification_scenario.json`. The workflow is entirely local and reads structured JSON.

## Required study-model fields

- `scenario_id`: unique reference for the analytical run.
- `patient_reference`: non-identifying reference used in the report.
- `actual_profile`: one value for every modeled attribute.
- `population_model`: a list of unique states; each state has a complete `profile` and a positive `weight`. The program normalizes weights to sum to one.
- `recipient_prior`: an optional mapping of each recipient's declared prior knowledge.
- `releases`: an ordered list of one or more events, each containing `recipient` and a `facts` dictionary. Optional descriptions include `event_id`, `purpose`, and `channel`.

## Optional disclosure-review fields

- `attribute_labels`: human-readable descriptions of attributes shown in the patient report.
- `recipient_preferences`: a mapping of recipient IDs to the attribute categories recorded as acceptable for that recipient. Entries beyond these categories generate review flags; their presence does not establish that a disclosure was legally unauthorized.

## Preparing a separate project

1. Create your own source scenario JSON rather than overwriting the included reference file.
2. Define the attributes, accepted values and complete profile states relevant to the project.
3. State explicitly how the joint distribution and its weights were derived. Use an appropriate analytical model; do not represent illustrative model weights as observed clinical prevalence.
4. Record each recipient's evidence-supported baseline information and each documented disclosure event in order.
5. Declare preference categories only when supported by your project materials; otherwise omit them and retain the `not_configured` status.
6. Run `python twinprivacy.py --scenario YOUR_FILE.json --format json` to inspect the analytical result. To regenerate the complete patient report with the one-command pipeline, configure the scenario input in `reproduce.py` and run `python reproduce.py`.
7. Preserve the independently retained terminal receipt anchor and evaluate the output against your study's validation plan.

## Technical definitions

Conditional pointwise information and model-implied probability changes depend on the fully specified joint distribution. Changing the model changes these numerical results even if the event sequence remains unchanged. All recipients are analyzed independently, so summing information across recipients is not meaningful without a separate shared-knowledge model.

The software processes only the structured attributes supplied to it; descriptive clinical case fields, laboratory values, free-text history and recipient behavior outside the event history do not automatically enter the calculation.
