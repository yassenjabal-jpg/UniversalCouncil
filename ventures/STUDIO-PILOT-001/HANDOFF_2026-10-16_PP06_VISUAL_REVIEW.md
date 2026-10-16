# STUDIO-PILOT-001 — HANDOFF
## Continue from PP06 Visual Execution V2
Date: 2026-10-16

## 1. Source of truth

Repository:
`yassenjabal-jpg/UniversalCouncil`

Working branch:
`studio/pilot-001-w1-v2-story-slate`

Do not trust old chat claims over the repository.
The actual repository, governing files, manifests, and current branch state are authoritative.

---

## 2. Current macro state

Writing: **COMPLETE / SCRIPT_LOCK ACTIVE**

Pre-production:
- PP01 Script Breakdown — PASS
- PP02 Visual Story Case — PASS
- PP03 Art Direction — **ART_DIRECTION_LOCK**
- PP04 Asset Plan — PASS
- PP05 Rights & Source Pre-clearance — PASS
- PP06 Shot Design — **REOPENED FOR REAL PHOTOSHOP EXECUTION**
- PP07 Storyboard — **BLOCKED until Owner approves PP06 visual execution**

Current PP06 state:
**AWAITING_OWNER_VISUAL_REVIEW**

Do not advance to PP07 until Owner explicitly approves the Photoshop keyframes.

---

## 3. Locked title

**لماذا احتاجت كوريا الشمالية 187 لابتوب داخل بيوت أمريكية؟**

The title is Owner-locked.

Accuracy constraint:
The official evidence supports approximately **187 computer devices**, including laptops/KVM equipment, not proof that all 187 were laptops.
The first-minute qualifier is mandatory and cannot be removed downstream.

---

## 4. Locked script

Canonical locked script:
`ventures/STUDIO-PILOT-001/W2_S10_LOCKED_SCRIPT.md`

Locked script blob SHA:
`26769f91cb98eb3f80d0634aae2ab8880f5ecb3a`

No downstream stage may silently rewrite narration, title, factual qualifiers, legal status, story order, or material visual promises.

Material script change => formal Return Ticket to Writing + new S10 lock.

---

## 5. Governing visual system

The **only permitted visual system** is:

**Editorial Renaissance Motion**

Governing files:
- `docs/operations/media/EDITORIAL_RENAISSANCE_VISUAL_BIBLE.md`
- `docs/operations/media/REFERENCE_FRAME_SPECS.md`
- `ventures/STUDIO-PILOT-001/PP03_ART_DIRECTION_LOCK.json`

No legacy/alternate visual system is permitted.

Core lock:
- Paper Ivory / white-light dominates.
- Cobalt / Clear Blue / Sky Blue are structural.
- Brass Gold / Deep Forest are accents.
- Charcoal is text/anchor only, never dominant.
- 16:9.
- 35–55% negative space.
- one hero object per frame.
- no dark-first fallback.
- no neon/cyberpunk.
- no dashboard/news UI.
- no generic AI-cinematic look.
- no fabricated evidence.

Channel-specific motifs:
1. Laptop as editorial portal.
2. Cobalt route + brass annotation.
3. Layered identity paper fragments.
4. Selective laptop-edge page-turn transition.

---

## 6. PP06 design state

The 41-shot matrix remains the detailed structural source:
`ventures/STUDIO-PILOT-001/PP06_SHOT_DESIGN_MATRIX.json`

The old PP06 SVG/wireframe previews are **not final visual execution**.
They were layout diagrams only.

After Owner correctly challenged this, PP06 was reopened for real Photoshop execution.

Current real Photoshop execution record:
`ventures/STUDIO-PILOT-001/PP06_VISUAL_EXECUTION_V2.json`

Current manifest:
`ventures/STUDIO-PILOT-001/PP06_MANIFEST.json`

Status:
**AWAITING_OWNER_VISUAL_REVIEW**

---

## 7. Actual Photoshop execution

Photoshop 2025 on YASSIN was used to create native layered PSD documents through Photoshop COM automation.

These are actual Photoshop-created documents, not SVG designs opened in Photoshop.

Current 8 keyframes:

1. KF01 — V01.4 — M01
   Device here / human elsewhere
2. KF02 — V02.5 — M02
   Freeze contrast: device here, human elsewhere
3. KF03 — V03.3 — M03
   Location pin belongs to laptop, not person
4. KF04 — V04.3 — M04
   40+ / ~187 / 70+ separated evidence contexts
5. KF05 — V05.2 — M05
   Employee decomposes into identity/interview/device/work/account
6. KF06 — V06.5 — M06
   Financial/consequence scale
7. KF07 — V07.4 — M07
   Disguise path reverses into evidence path
8. KF08 — V08.4 — M08
   Valid-looking signals remain while the human changes

Binary outputs:
`ventures/STUDIO-PILOT-001/pp06_photoshop_keyframes/`

Each keyframe has:
- layered PSD;
- Photoshop-exported PNG;
- sRGB-compatible JPEG review preview.

Current binary-output commit lineage includes:
- `18745c9` — PSD + PNG Photoshop outputs
- `4404da4b0b137c8eb4365d35d78a1a24ba24539c` — JPEG review previews after rebase/push

Do not mistake the earlier `pp06_previews/` wireframes for the current Photoshop execution.

---

## 8. Why JPEG previews exist

The Photoshop PNG files rendered black in GitHub/Android for the Owner even though pixel inspection showed normal RGB content.

They were re-encoded to standard JPEG RGB/sRGB-compatible previews.

For mobile review, use the `*_preview.jpg` files, not the original PNG.

---

## 9. Visual review delivery rule — OWNER DIRECTIVE

Default visual-review delivery channel:
**Dropbox**

GitHub remains source of truth for:
- PSD originals;
- manifests;
- version history;
- canonical project files.

For Owner visual review:
prefer:
1. Dropbox
2. direct ChatGPT attachment when available
3. GitHub raw/direct image link
4. GitHub media viewer only as last resort

Memory event:
`memory/events/2026-10-16/MEM-20261016-231000-pp06share.json`

Snapshot subject:
`youtube.review_image_delivery.default`

Dropbox review-folder convention:
`/Studio Reviews/<project_id>/<stage>/`

Current Dropbox review folder created successfully:
`/Studio Reviews/STUDIO-PILOT-001/PP06`

Important current limitation:
Dropbox Desktop is NOT installed on YASSIN.
The current Dropbox connector cannot directly upload arbitrary local YASSIN files.
Therefore the folder currently exists as the approved destination, but do NOT claim the eight JPEGs were uploaded there unless a future tool action actually verifies upload completion.

If a later chat gains a supported route for file upload from YASSIN or generated conversation attachments, upload the 8 JPEG previews to this Dropbox folder.

---

## 10. Current Owner review gate

PP07 Storyboard must remain blocked.

Next action:
- present/review the 8 Photoshop keyframes;
- collect Owner comments;
- revise PP06 visual execution inside Photoshop if needed;
- only after explicit Owner approval:
  - set `PP06_VISUAL_LOCK`;
  - update PP06 manifest to PASS;
  - proceed to PP07 Storyboard.

Do NOT interpret silence or “continue” after unrelated discussion as approval unless context clearly refers to these keyframes.

---

## 11. Important technical truth

The first PP06 execution claim was corrected.

Earlier:
- SVG wireframes were generated externally;
- Photoshop was only opened/verified.

Current corrected execution:
- Photoshop itself created and saved layered PSDs;
- PNG/JPEG review outputs derive from those Photoshop documents.

Maintain this distinction in all future status reporting.

---

## 12. YASSIN

Primary device:
**YASSIN**

Remote device ID:
`4ca4bced-f8ec-41f7-b8af-9fb86e0ede61`

Local repo:
`C:\Users\alnaseem\Desktop\UniversalCouncil`

Local Photoshop keyframes:
`C:\Users\alnaseem\Desktop\STUDIO-PILOT-001_ASSETS\PP06_PHOTOSHOP_KEYFRAMES`

Photoshop 2025 executable:
`E:\Adobe 2025\Adobe Photoshop 2025\Photoshop.exe`

Use GUI/specialized creative tools as primary craft path.
Desktop Commander is secondary/orchestration.
Do not replace visual craft work with code merely because code is easier.

---

## 13. Production philosophy

The Studio is a serialized production line.

One active craft department at a time.
One primary creative program per stage.
Program switches occur at stage boundaries.
Downstream departments do not silently repair upstream defects.
Use Return Tickets.

Observe -> act -> verify -> checkpoint.

UNKNOWN != SUCCESS.

Do not claim completion without evidence.

---

## 14. Immediate instruction for the new chat

Start by reading the current repo state and the files listed above.

Then say clearly:

**Current gate: PP06 AWAITING_OWNER_VISUAL_REVIEW. PP07 is blocked.**

If the Owner asks to continue PP06:
continue refining the 8 Photoshop keyframes inside Photoshop 2025.

If the Owner approves the visual direction:
create PP06 Visual Lock, update manifests, and then begin PP07 Storyboard.

Do not regress to old visual systems.
Do not use the old SVG wireframes as final visual references.
Use Dropbox as the preferred review delivery channel when technically possible and verified.

