> **SUPERSEDED — historical evidence only.** The DAY24 ladder, retry/prototype queues and long AE GUI method are cancelled. [Lean Workflow v2.0](LEAN_VIDEO_PRODUCTION_WORKFLOW.md) governs current production. Historical results below are preserved; do not resume these instructions or use their PASS as new-system proof.

# Visual Tool Qualification Protocol

**Status:** REQUIRED before Visual System Lock  
**Purpose:** choose the primary visual-generation route by measured quality and fidelity, not by remaining credits, convenience, or model novelty.

## 1. Qualification principle

> Same frame. Same brief. Same evaluation rubric.

A model/tool does not become primary because:
- it has free credits;
- it is already connected;
- it is fast;
- it is fashionable;
- it produced one beautiful image.

It becomes primary because it executes the channel's locked visual intent reliably.

## 2. Candidate set

Test at least **two viable candidates** when access permits.

Candidates may include:
- OpenAI image generation;
- OpenArt models;
- Runway image models;
- another Council-approved specialized image tool.

If fewer than two viable candidates can actually be tested, status remains:
`TOOL_QUALIFICATION_INCOMPLETE`

Do not fake a comparison.

## 3. Benchmark frame

Use one Council-approved reference-frame brief that is difficult enough to expose:
- prompt drift;
- composition control;
- negative-space control;
- object-count discipline;
- material/texture treatment;
- forbidden-element compliance.

Do not use three unrelated topics.

## 4. Scoring

Score 0–5 per criterion, then apply weights:

| Criterion | Weight |
|---|---:|
| Prompt fidelity | 30 |
| Composition control | 20 |
| Style consistency / reference fidelity | 20 |
| Artifact quality | 10 |
| Editability / usefulness in production | 10 |
| Speed | 5 |
| Cost | 5 |

Quality + fidelity deliberately dominate price.

## 5. Automatic failure

A candidate fails regardless of beauty if it:
- repeatedly adds forbidden elements;
- changes the requested composition materially;
- merges multiple concepts;
- creates unrequested multi-panel outputs;
- cannot preserve negative space;
- invents documentary evidence;
- makes controlled iteration impossible.

## 6. Selection

Council receives the scorecard.

Technical Operator reports:
- tool;
- model;
- settings;
- job/generation ID;
- cost;
- runtime;
- deviations.

Visual Art Director scores craft/fidelity.
Thumbnail Designer scores packaging/readability where relevant.
Red Team scores prompt drift and AI slop.
Technical Operator scores controllability/repeatability.
Finance records cost but does not choose the winner.

Primary tool:
- highest qualified total, subject to no automatic-failure finding.

Backup tool:
- next qualified route with materially different failure mode or useful fallback.

## 7. Credits rule

> Remaining credits MUST NOT select the primary tool.

Credits may determine whether a benchmark can be executed today. They do not convert an untested or lower-fidelity tool into the channel standard.

## 8. Requalification

Re-run qualification when:
- primary model materially changes;
- tool settings change in a way that affects outputs;
- repeated prompt-drift defects appear;
- a new candidate materially outperforms the current route;
- the visual identity itself changes.

## 9. Current state

Until this protocol is completed with real same-brief evidence:

- primary still generator: `UNQUALIFIED`
- backup still generator: `UNQUALIFIED`
- Visual System Lock: `BLOCKED`
- full-length episode: `BLOCKED`
