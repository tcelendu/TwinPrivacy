# TwinPrivacy: research evidence brief

## Working title

**Patient-verifiable longitudinal accounting of health-data disclosures using recipient-conditioned information measurement**

## Scientific premise

A record of when health data were released does not on its own quantify what a recipient learned from the release. The incremental disclosure depends on the recipient's earlier information, repetitions in the sharing history and dependence among clinical attributes. TwinPrivacy implements a reproducible, individual-level structured-disclosure evaluation workflow under an explicitly defined probability model.

## Research question

**Can a patient-facing verification tool accurately account for incremental, recipient-specific information contained in recorded structured health-data disclosures, and can it expose sensitivity to correlations and weaknesses in the integrity of the disclosure record?**

## Methods

An open-source Python implementation processes a specified 16-state joint model for four clinical attributes (diabetes, chronic kidney disease, asthma, medication allergy). A deterministic generator (seed 20261107) creates 512 synthetic clinical profiles and corresponding recipient-conditioned disclosure histories, producing 4,096 events. Two numerical quantities per event—incremental and cumulative conditional pointwise information—are compared with a separately implemented direct-enumeration reference computation (8,192 comparisons; tolerance 0.000001 bits). Comparator analyses consist of simple event counting and an independent-attribute product model with identical marginal probabilities. Additional challenges introduce five forms of log modification or replacement to examine retained-receipt integrity.

## Results

Reproduce the numerical results using `python reproduce.py` and see `evidence/results/VALIDATION_SUMMARY.md`. The software demonstrates reference agreement within the stated numerical tolerance, zero additional modeled information for repeated or prior-known facts, sensitivity to declared correlations, and tamper detection relative to a trusted terminal receipt. It also explicitly illustrates why internally consistent log hashes cannot prove the completeness or authenticity of recorded activity.

## Current contribution and next hypothesis

The present artifact integrates recipient-conditioned analysis, sequential information accounting, patient preference review, and portable hash-linked receipts for structured health-data releases. Each constituent idea has prior art; unique theoretical novelty has not been established. A grant-stage advance would need to test a stronger verification mechanism—preferably event completeness and/or quantification of information conveyed by free-text and derived clinical answers—against appropriate prior systems under a defined adversarial threat model.

## Scientific boundaries

The validation data and probability model are generated, not empirical. The result is evidence of algorithm correctness under a specified model, not validation on clinical data, a formal privacy guarantee, detection of unlogged access, or a claim about actual patient outcomes.
