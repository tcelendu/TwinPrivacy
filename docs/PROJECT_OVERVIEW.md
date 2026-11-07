# TwinPrivacy: Research project overview

## Rationale

Digital health systems distribute health information across clinical, research and analytics settings. A conventional log describes records transferred; it may not explain whether the information was already known to the recipient or whether seemingly limited disclosures alter what may be inferred about other sensitive attributes. Patients need interpretable accounts of the information transferred to different recipients, together with understandable means of assessing record integrity.

## Technical contribution

TwinPrivacy combines recipient-specific state tracking, conditional pointwise disclosure information, a weighted joint clinical-attribute model, sharing-preference review checks and hash-linked receipts. It presents findings in two complementary outputs: a detailed machine-readable analytical record and an accessible, printable patient statement.

The software explicitly separates **recorded attributes** from **model-implied inferences** and **record integrity** from **completeness of event capture**. These distinctions prevent stronger claims than the available information can support.

## Demonstration scope

The enhanced reference scenario covers four clinical attributes, 16 possible joint states, eight disclosures and three recipient services. All model probabilities and disclosures are declared in a version-controlled reference file. The existing clinical case workbook provides narrative examples and legacy three-attribute analyses for continuity.

## Evaluation strategy

Key testable properties include: (1) identical repetitions contributing zero additional information to the same recipient; (2) the effect of declared baseline knowledge; (3) correlated-attribute inference shifts; (4) flags for disclosures outside documented sharing preferences; (5) reproducible numerical results; and (6) detection of altered or reordered disclosure events and modified analytical assumptions.

The included automated tests exercise these properties. Further independent study is needed to assess privacy-utility tradeoffs, realistic clinical data distributions, event-capture completeness, cross-institution interoperability, recipient behavior and user comprehension of patient-facing reports.

## Reproduction

Run `python reproduce.py` from the repository root. The complete patient report and machine-readable results are generated in `outputs/` without external services.
