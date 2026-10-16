# Studio Pilot 001 — PP04 Asset Plan

Status: **ASSET_PLAN_READY_FOR_BRIDGE_INGEST**
Primary program: **Adobe Bridge 2025**

## Asset architecture

The 41 locked shot blocks are organized into **11 asset collections**.

- **01_REALITY_HOME** — Ordinary American home environment; used by V01.1, V07.1, V08.1; source strategy: ORIGINAL_OR_LICENSED.
- **02_HERO_LAPTOP** — Generic employer laptop + shipping box; used by V01.2, V01.3, V02.3, V03.3, V07.1, V08.5, V08.6; source strategy: ORIGINAL_OR_LICENSED.
- **03_MAPS_SPATIAL** — U.S./Nashville maps; used by V01.4, V02.1, V04.1, V07.4; source strategy: ORIGINAL_VECTOR_OR_MAP_SAFE.
- **04_EVIDENCE_DATA** — Official evidence/data cards; used by V01.5, V02.2, V04.3, V05.4, V06.1, V06.2, V06.3, V06.4, V06.5; source strategy: OFFICIAL_SOURCE.
- **05_HUMAN_CUTOUTS** — Human/operator silhouettes; used by V01.4, V02.4, V05.3, V08.4; source strategy: ORIGINAL_OR_LICENSED.
- **06_TRUST_SIGNAL_SYSTEM** — Employee/trust-signal card system; used by V03.1, V03.2, V05.1, V05.2, V05.5, V08.2, V08.3; source strategy: ORIGINAL_DESIGN.
- **07_DISTRIBUTED_SCALE** — Distributed homes/farm scale system; used by V04.1, V04.2, V04.4; source strategy: ORIGINAL_DESIGN.
- **08_CASE_SCALE** — Proven-case scale/count system; used by V06.1, V06.2, V06.3, V06.4, V06.5; source strategy: OFFICIAL_FACTS_ORIGINAL_VISUALS.
- **09_SENSITIVE_ACCESS** — Sensitive data/source code/defense abstraction; used by V06.6; source strategy: ORIGINAL_ABSTRACT.
- **10_EVIDENCE_CHAIN** — Physical evidence-chain system; used by V07.2, V07.3, V07.4, V07.5; source strategy: ORIGINAL_DESIGN.
- **11_FINAL_METAPHOR** — Final identity metaphor; used by V08.4, V08.6; source strategy: ORIGINAL_DESIGN.

## Bridge labels

- Green — approved style fit
- Yellow — source / rights review
- Red — rejected / do not use
- Blue — official source reference

## Mandatory metadata

Every ingested asset receives:
- project ID;
- asset group ID;
- shot references;
- source class;
- rights state;
- visual-system keyword;
- rating;
- version.

## Style rejection rule

Any candidate that drifts into dark-first, cyberpunk, dashboard/news UI, generic AI cinematic, or fabricated evidence is rejected in Bridge before it reaches Shot Design.

## PP04 gate

- 11/11 asset groups mapped: PASS
- 41/41 shots mapped: PASS
- Bridge collections defined: PASS
- rights/source status model defined: PASS
- naming/versioning defined: PASS
- Art Direction Lock preserved: PASS

**PP04 planning result: READY_FOR_BRIDGE_INGEST**
