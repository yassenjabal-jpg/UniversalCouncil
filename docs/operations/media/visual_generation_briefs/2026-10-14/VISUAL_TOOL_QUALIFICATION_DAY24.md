# Visual Tool Qualification — DAY24 Same-Frame / Same-Brief Benchmark

**Date:** 2026-10-14  
**Protocol:** `docs/operations/media/TOOL_QUALIFICATION_PROTOCOL.md`  
**Benchmark brief:** `DAY24-CS-v1.1-SINGLE`  
**Comparison contract:** SAME FRAME + SAME BRIEF + ONE ASSET

## Candidates actually executed

| Candidate | Route | Task ID | Credits | Visual result |
|---|---|---:|---:|---|
| A | Runway / nano-banana-pro | `27cc520d-0989-4ef9-9a0a-e647ead0cc12` | 20 | high material quality, strong fidelity |
| B | Runway / gen-4 | `988ae570-22a2-429a-9bdb-b7381f144db8` | 8 | material prompt drift |
| C | Runway / nano-banana-2-lite | `2d283532-dde8-4bad-8922-622896c4963a` | 4 | strongest constraint fidelity and editability |

OpenArt was checked but had 0 credits and therefore was not treated as a viable executed comparison candidate.

A Seedream route was attempted but the connected Runway plan blocked execution. It is not scored.

## Council visual review

### Candidate A
Strengths:
- excellent paper/material realism;
- correct ivory field and left negative space;
- one hero object only;
- restrained palette and tiny plum accent;
- immediately readable and premium.

Minor drift:
- daylight/night split became a more complex angular relationship rather than two clean material halves;
- internal central circle adds a small secondary structural feature;
- radial system is elegant but slightly more designed than the literal brief.

### Candidate B
Strengths:
- tactile paper feel;
- clear segmentation concept;
- usable editorial texture.

Material drift:
- disc moved toward the center instead of center-right;
- background became a strong 50/50 ivory/blue split;
- blue field became too dominant;
- visible gold/brass feeling appeared;
- object became folded/fan-like rather than a clean thick card disc;
- weaker negative-space discipline.

Red Team: qualified benchmark output **FAIL** for primary-route selection.

### Candidate C
Strengths:
- strongest match to the requested composition;
- clear center-right placement;
- roughly correct left-side negative space;
- one hero object;
- very clean daylight/night material split;
- radial grooves remain the dominant idea;
- no literal celestial imagery;
- easy to retouch, composite and animate;
- tiny plum registration accent is preserved.

Minor drift:
- less luxurious material rendering than Candidate A;
- simpler artifact finish.

Red Team: **PASS**.

## Weighted scorecard

Scale 0–5 before weighting.

| Criterion | Weight | A | B | C |
|---|---:|---:|---:|---:|
| Prompt fidelity | 30 | 4.6 | 2.6 | 4.9 |
| Composition control | 20 | 4.5 | 2.2 | 4.9 |
| Style/reference consistency | 20 | 4.6 | 3.0 | 4.4 |
| Artifact quality | 10 | 4.8 | 3.9 | 4.2 |
| Editability | 10 | 4.4 | 3.1 | 4.8 |
| Speed | 5 | 4.3 | 3.5 | 4.5 |
| Cost | 5 | 2.5 | 4.2 | 5.0 |
| **Weighted total** | **100** | **89.2** | **58.1** | **94.1** |

## Decision

### Primary visual generator
`runway:nano-banana-2-lite`

Status: **QUALIFIED_PRIMARY**

Reason:
It won because fidelity, composition control and editability were strongest. Its lower cost is a benefit, not the selection reason.

### Backup visual generator
`runway:nano-banana-pro`

Status: **QUALIFIED_BACKUP**

Reason:
It delivers stronger material richness and may be preferred for hero/final art when a small fidelity tradeoff is acceptable.

### Rejected for current identity lock
`runway:gen-4`

Status: **NOT_QUALIFIED_FOR_PRIMARY_IDENTITY_EXECUTION**

Reason:
Prompt drift was too high on the benchmark.

## Governance note

This benchmark qualifies **models/routes**, not the whole Runway platform unconditionally. Requalification is required after material model changes or repeated fidelity defects.

The primary route may now be used for P0 Reference Frame Lock.

No merge to `main` is authorized by this artifact.
