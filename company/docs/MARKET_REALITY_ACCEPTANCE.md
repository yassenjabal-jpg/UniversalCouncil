# Market Reality Definition Gate — Acceptance Report
Date: 2026-10-08

## Verdict
PASS.

The company now requires a defined target market reality before proposing a commercial venture candidate.

## Enforced dimensions
- WHERE: country and only behavior-relevant geographic precision;
- WHO: age range + life stage + social/occupational segment + user/buyer/payer;
- MONEY: segment-level purchasing capacity, discretionary-budget evidence, existing spend, willingness-to-pay evidence, supported price band and payment methods;
- BEHAVIOR: discovery, first-touch, conversation, trust, payment, delivery/infrastructure and reachability behavior;
- EVIDENCE SCOPE: geography and segment evidence must match the target; foreign evidence may only be secondary context without transfer evidence.

## Discovery modes
- SEGMENT_FIRST
- PAIN_FIRST

Both modes forbid project-first reasoning and evidence reverse-engineering.

## Project proposal control
A project candidate:
- cannot exist before the Market Reality record passes;
- requires an observed problem;
- receives a weighted Market Pull Score;
- cannot use a price above the evidence-supported segment ceiling;
- cannot substitute global evidence for local/target-segment evidence.

## Market Pull Score
Weighted factors include pain frequency, existing spend, urgency, workaround burden, buyer clarity, reachability, Free-AI resistance, repeatability, margin potential, evidence diversity, purchasing capacity and local price fit.

Decision bands:
- <60 REJECT
- 60–74 DISCOVERY
- 75–84 VALIDATION_CANDIDATE
- 85–100 PRIORITY_CANDIDATE

A pivotal gate failure still overrides the score.

## HR / capability consequence
HR & Capability Director now owns local-market research capability gaps. If the company cannot access a material local research channel, it must record and escalate the gap rather than silently replacing it with global evidence.

## Verification
GitHub Actions on the implementation head:
- Python compile: PASS
- Universal Council invariant validator: PASS
- deterministic company tests: 56 PASS

## Activation boundary
This change does not restart any venture and does not authorize outreach, publishing, spending, payment collection or live commercial operation.
