> **SUPERSEDED — historical evidence only.** The DAY24 ladder, retry/prototype queues and long AE GUI method are cancelled. [Lean Workflow v2.0](../../LEAN_VIDEO_PRODUCTION_WORKFLOW.md) governs current production. Historical results below are preserved; do not resume these instructions or use their PASS as new-system proof.

# Phase 6 Asset Production Manifest — DAY24 Retry

**Date:** 2026-10-14  
**Parent shot bible:** `P1_DAY24_SHOT_BIBLE_ASSET_GRAPH_v2.0.md`  
**Production kit:** `VISUAL_PRODUCTION_KIT_v1.1.md`  
**Primary motion route:** Adobe After Effects 2026 on YASSIN  
**Phase 5 gate:** PASS  
**Status:** **ACTIVE**

## 1. Phase objective

Produce and QC only the assets required by the locked shot bible.

No full pilot assembly begins until this manifest reaches:
### **P1R-ASSET_QC_PASS**

## 2. Asset registry

| ID | Asset | Class | Current state | Phase-6 action |
|---|---|---|---|---|
| A01 | cobalt / ivory / charcoal fields | NATIVE-AE | READY | retain |
| A02 | Arabic + Latin typography package | NATIVE-AE | OPEN | install/lock preferred font family and verify AE shaping |
| A03 | long segmented strip | NATIVE-AE | READY | refine hierarchy only |
| A04 | macro groove / segment texture | GENERATED/PROCEDURAL | OPEN | produce final macro material asset |
| A05 | 12 / 12 / 24 vector system | NATIVE-AE | READY | retain exact deterministic geometry |
| A06 | Met 11.150.50b1 evidence | REAL-EVIDENCE | READY | preserve source-faithful pixels |
| A07 | decan markers / graphic field | NATIVE-AE | PROTOTYPE PASS | refine print/halftone treatment |
| A08 | contemporary hand — pull | PHOTO/ILLUSTRATION | FINAL CANDIDATE | QC cutout/contact/editorial treatment |
| A09 | contemporary hand — pinch/stretch | PHOTO/ILLUSTRATION | FINAL CANDIDATE | derive same visual family; QC contact |
| A10 | flexible segmented object | NATIVE-AE | READY | retain |
| A11 | technical drawing/grid | NATIVE-AE | READY | strengthen line-build animation in assembly |
| A12 | 24-unit sculptural object | NATIVE-AE 2.5D | OPEN | build final reusable object |
| A13 | halftone/dither transition language | NATIVE-AE | OPEN | create deterministic treatment preset/spec |
| A14 | paper/material SFX family | AUDIO | DEFER PHASE 7 | no Phase-6 work |
| A15 | music | AUDIO | DEFER PHASE 7 | no Phase-6 work |
| A16 | final narration | AUDIO | DEFER PHASE 7 | no Phase-6 work |

## 3. Typography lock

Preferred:
- Noto Kufi Arabic — display
- Noto Sans Arabic — body/labels
- Source Serif 4 — Latin/numerals

Current YASSIN check:
- preferred Noto Arabic families are not installed;
- Segoe UI / Arabic Typesetting / Simplified Arabic are available only as temporary fallbacks.

Action:
1. install preferred open-source font families from their official source;
2. verify Arabic shaping inside AE;
3. render one typography QC frame;
4. record font family/version in this manifest.

## 4. A04 macro texture requirements

Must provide:
- cream/ivory tactile macro surface;
- one clear division groove;
- enough real/material texture to bridge photography→vector;
- no parchment fantasy;
- no marble/gold;
- no clock face;
- no text;
- no second focal object.

Target use:
S01→S02→S03.

QC:
- reads as real material at macro scale;
- does not become another “premium paper product shot”;
- groove can align exactly with native AE baseline.

## 5. A08/A09 hand family requirements

Existing candidate:
`E:\UC_MOTION_QUALIFICATION\A08_hand_pull.jpg`

Use only as contemporary explanatory imagery, never evidence.

QC:
- credible anatomy;
- clean mask edge;
- neutral lighting;
- no jewelry/branding;
- hand pose supports pull/pinch causality;
- editorial integration via crop/field/print treatment;
- contact point aligns with target geometry.

If one source can serve both A08 and A09 through crop/position without visual contradiction, reuse is preferred over generating a second unrelated hand.

## 6. A12 sculptural 24-unit object

Preferred implementation:
native AE 2.5D/vector-derived object.

Requirements:
- exactly 24 deterministic units;
- can transition from technical grid;
- supports three surface states in S11;
- can split/recombine;
- no AI counting;
- no clock-face shorthand.

## 7. A13 halftone / dither language

Requirements:
- deterministic;
- supports photo→graphic transformation;
- preserves evidence boundary;
- restrained enough for premium editorial look;
- no glitch/noise aesthetic;
- reusable across B05/B06 and selected transitions.

## 8. Evidence QC

A06:
- institution: The Metropolitan Museum of Art;
- object: 11.150.50b1;
- Public Domain / Open Access;
- repository copy exists at:
  `docs/operations/media/pilots/assets/met_549494_11.150.50b1.jpg`.

Final evidence beat rules:
- source-faithful color/content while acting as evidence;
- only crop/scale/mask/mount/label;
- explanatory line/marker stays outside pixels;
- source label remains readable but subordinate.

## 9. Phase-6 pass criteria

Phase 6 passes only when:
1. final typography family is installed/verified in AE;
2. A04 macro texture passes QC;
3. A08/A09 hand family passes QC;
4. A12 exact 24-unit object passes geometry QC;
5. A13 halftone/dither treatment is defined and test-rendered;
6. evidence asset remains rights/source verified;
7. all non-audio shot dependencies are READY;
8. no full-Council blocker remains.

## 10. Next gate

When all criteria pass:
### **P1R-ASSET_QC_PASS**

Then Phase 7 — Audio Spine may proceed.

Full picture assembly still waits for:
- Phase 7 audio spine lock;
- Phase 8 full animatic pass.
