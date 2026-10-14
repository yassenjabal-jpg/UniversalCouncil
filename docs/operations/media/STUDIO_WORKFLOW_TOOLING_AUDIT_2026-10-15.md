# The Studio — Workflow & Tooling Audit

**Date:** 2026-10-15  
**Scope:** all current Studio production roles  
**Goal:** give each role a real production tool, while avoiding tool sprawl and preserving the five-stage / three-gate workflow.

## Executive decision

The Studio should operate as a compact professional production studio, not as twelve specialists each using a separate app.

### Proposed core studio stack

#### Install now / primary stack
1. **Adobe Premiere Pro 2026** — primary NLE / story and picture edit.
2. **Adobe Photoshop 2026** — thumbnails, raster compositing, retouching.
3. **Adobe Illustrator 2026** — vector diagrams, editorial assets, AE-ready artwork.
4. **Adobe Audition 2026** — dialogue edit, sound design, rough/final mix for current scale.
5. **Adobe Media Encoder 2026** — controlled queue, transcodes, delivery presets.
6. **Zotero** — research/source library and fact-check evidence.
7. **PureRef** — visual references and art-direction boards.
8. **Subtitle Edit** — subtitle/localization timing and QC.
9. **MediaInfo GUI/CLI** — independent technical metadata verification.
10. **Youlean Loudness Meter 2** — loudness / true-peak QC.

#### Already available / no additional desktop installation required
- Adobe After Effects 2026 — motion/compositing.
- Creative Cloud.
- Descript connector — transcript/rough utility only.
- Runway / OpenArt — generated media.
- Figma / Canva — connected design utilities.
- vidIQ connector — audience / competitor / title / thumbnail / retention research.
- YouTube Studio — native title/thumbnail testing and channel analytics.
- Frame.io — use through Premiere / web if included with the Adobe plan.

#### Do not install yet
- **DaVinci Resolve 21** — excellent all-in-one finishing/color/Fairlight alternative, but duplicates Premiere/Audition/AE at the current stage.
- **Pro Tools** — professional audio-post reference, but excessive for the current YouTube production scale.
- **iZotope RX 12** — add only if real narration recordings reveal repair problems Audition cannot handle efficiently.
- dedicated paid SFX library manager / DAM — defer until the asset library is large enough to justify it.

## Studio-pattern findings

Professional collaborative workflows separate story edit from motion/VFX and make review timecode-aware. Adobe Premiere supports Team Projects, shared editing, Frame.io review, and direct After Effects Dynamic Link. After Effects remains the motion/compositing environment, not the entire editorial pipeline.

Blackmagic Resolve confirms the same organizational pattern from another ecosystem: editor, colorist, VFX artist and sound engineer work as separate specialties in one coordinated project. Avid's audio-post workflow likewise separates dialogue, sound design and final mix.

Therefore The Studio target is:
**Premiere timeline → AE motion/VFX → Audition sound/mix → Media Encoder export → independent MediaInfo/Youlean/Frame.io QC.**

---

# Role-by-role Studio review

## 1. Media Producer / Production Coordinator

### Current weakness
Production state is well governed in GitHub, but media-specific versions, review notes, timestamp feedback and WIP asset handling are not first-class.

### Studio pattern
Centralized media versions, timestamped review, stage handoffs and visible approval state.

### Tools
**Primary:** Frame.io + Premiere Team Projects  
**Secondary:** existing GitHub contracts for governance/evidence

### Use
- Frame.io project per episode;
- cuts uploaded as versions, not loose files;
- timecoded notes replace chat-only feedback;
- GitHub remains governance/source-of-truth for policy, not the day-to-day media review UI.

### Install
No separate Frame.io desktop install required initially if Premiere integration/web access is available.

---

## 2. Editorial Director / Showrunner

### Current weakness
Script authority exists, but story decisions do not live directly against the editable picture timeline.

### Studio pattern
Showrunner reviews structure against sequences and markers, not only prose documents.

### Tools
**Primary:** Adobe Premiere Pro  
**Review:** Frame.io  
**Planning:** repo markdown remains canonical

### Use
- story skeleton and selects in Premiere;
- chapter/beat markers;
- notes pinned to exact timecodes;
- final editorial authority remains with Showrunner.

### Install
**Premiere Pro 2026 — INSTALL NOW**

---

## 3. Independent Fact Checker

### Current weakness
Claim ledgers are strong, but source collection is manually distributed across markdown/URLs.

### Studio/research pattern
Structured source library with metadata, tags, attachments and durable citation retrieval.

### Tools
**Primary:** Zotero  
**Secondary:** browser/web research + repository claim ledger

### Use
- collection per episode;
- tags for VERIFIED / CONTESTED / PRIMARY / SECONDARY / VISUAL-EVIDENCE;
- snapshots/PDFs stored with source record;
- claim ledger links back to Zotero source entry.

### Install
**Zotero — INSTALL NOW**

---

## 4. Script & Voice Director

### Current weakness
Narration maps exist as documents, but voice performance, pickups, timing and waveform decisions are not handled in a real audio workspace.

### Studio pattern
Performance direction is line-by-line; pickups, pauses, alternate takes and timing are audible against picture.

### Tools
**Primary:** Adobe Audition  
**Utility:** Descript for transcript/text cleanup

### Use
- record/import narration;
- markers for emphasis/pause/pickup;
- comp best takes;
- export dialogue stem to Premiere;
- Descript remains transcript utility, not final mix.

### Install
**Adobe Audition 2026 — INSTALL NOW**

---

## 5. Visual Art Director / Frame Curator

### Current weakness
Visual Bible is strong, but reference boards and source artwork are split between documents, generated images and ad-hoc files.

### Studio pattern
A dedicated reference board plus layered raster/vector source artwork before motion begins.

### Tools
**Primary reference board:** PureRef  
**Raster:** Photoshop  
**Vector/editorial:** Illustrator  
**Existing utilities:** Figma / Canva / Runway / OpenArt

### Use
- one PureRef board per episode;
- approved reference clusters, palette, typography and texture;
- Photoshop master comps for photographic/mixed-media frames;
- Illustrator for diagrams, line art, motifs and vector systems prepared for AE.

### Install
**PureRef — INSTALL NOW**  
**Photoshop 2026 — INSTALL NOW**  
**Illustrator 2026 — INSTALL NOW**

---

## 6. Motion & Picture Editor

### Current weakness
After Effects is being forced to act as NLE, motion system, audio workspace and delivery tool.

### Studio pattern
NLE owns story/picture timeline. AE owns motion/compositing. Linked comps return to the NLE.

### Tools
**Primary NLE:** Premiere Pro  
**Motion/VFX:** After Effects 2026  
**Export/transcode:** Media Encoder

### Use
- Premiere owns episode sequence and picture edit;
- AE only for shots/comps that require motion/VFX/editorial graphics;
- Dynamic Link or rendered intermediates as appropriate;
- Media Encoder handles export queue while editing can continue.

### Install
**Premiere Pro 2026 — INSTALL NOW**  
**Media Encoder 2026 — INSTALL NOW**  
After Effects already installed.

### Target routing after qualification
**Premiere = picture-edit authority tool**  
**After Effects = motion/VFX authority tool**  
Do not change production config until Premiere is installed and passes a qualification test.

---

## 7. Music Supervisor & Sound Designer

### Current weakness
Temporary music/SFX are inserted late and often inside the picture/motion environment.

### Studio pattern
A spotting pass creates cue intent before the final edit; dialogue/music/effects remain separate stems.

### Tools
**Primary:** Adobe Audition  
**Future optional:** dedicated SFX library manager when asset volume justifies it

### Use
- spotting sheet translated into Audition session markers;
- separate DX / MX / FX buses;
- design recurring sonic motifs;
- export stems, not only a baked stereo mix.

### Install
Audition is shared with the Voice Director and Mix Engineer; no second DAW needed initially.

---

## 8. Dialogue & Mix Engineer

### Current weakness
AE has been used for audio finishing; this is adequate only for prototypes.

### Studio pattern
Dedicated DAW for dialogue edit, EQ/de-essing/noise control, automation, ducking, stems, loudness and delivery.

### Tools
**Primary now:** Adobe Audition  
**QC meter:** Youlean Loudness Meter 2  
**Future specialist repair:** iZotope RX 12 only if required  
**Studio reference:** Pro Tools, not required now

### Use
- dialogue cleanup in Audition;
- music ducking and stem management;
- final mix outside AE;
- Youlean confirms LUFS / true peak before Final QC.

### Install
**Audition 2026 — INSTALL NOW**  
**Youlean Loudness Meter 2 — INSTALL NOW**  
RX/Pro Tools — DEFER.

---

## 9. Audience Growth & Packaging Strategist

### Current weakness
This role previously contributed opinions without a real analytics/research surface.

### Creator-studio pattern
Topic, competitor, title, thumbnail and retention decisions are evidence-backed.

### Tools
**Primary:** vidIQ connector already available  
**Native truth:** YouTube Studio

### Use
- vidIQ: keyword research, outliers, trending videos, competitor/channel search, title score, thumbnail score, retention/channel analytics where authorized;
- YouTube Studio: actual channel analytics and native title/thumbnail testing;
- the strategist hands the Showrunner a compact hook/retention brief, not a generic trend report.

### Install
No desktop install required for Studio use.
Optional vidIQ browser/mobile app is user convenience only.

---

## 10. Thumbnail & Packaging Designer

### Current weakness
AI generation has carried too much of the thumbnail craft.

### Studio/creator pattern
Generated/photographic assets are raw material; final hierarchy, masking, retouching and type are authored deliberately.

### Tools
**Primary:** Photoshop  
**Vector/type support:** Illustrator  
**Research/testing:** vidIQ + YouTube Studio

### Use
- build one layered PSD master;
- generate only source elements when needed;
- mobile-scale check;
- final A/B test happens through native YouTube tooling when eligible.

### Install
Photoshop + Illustrator — shared core installs.

---

## 11. Localization Producer

### Current weakness
Localization exists as a contract but lacks a dedicated timing/QC environment.

### Studio pattern
Translation is followed by subtitle timing, line-length/readability QC and reconform against final picture.

### Tools
**Primary:** Subtitle Edit  
**Conform:** Premiere Pro

### Use
- subtitle timing against waveform/video;
- translation pass;
- line/readability checks;
- export SRT/VTT;
- conform timing if final edit changes.

### Install
**Subtitle Edit — INSTALL NOW**

---

## 12. Independent QC Reviewer

### Current weakness
The runtime performs strong automated checks, but the human QC surface is not specialized.

### Studio pattern
Independent playback plus technical metadata, loudness and version-aware review.

### Tools
**Technical metadata:** MediaInfo  
**Loudness:** Youlean Loudness Meter  
**Review/versioning:** Frame.io  
**Playback:** Premiere or independent player

### Use
- verify codec/resolution/frame-rate/audio metadata independently of the editor;
- measure LUFS / true peak separately from the mix session;
- full playback with timecoded defect log;
- hash final master only after visual/audio review.

### Install
**MediaInfo — INSTALL NOW**  
**Youlean Loudness Meter 2 — INSTALL NOW**

---

# Installation priority

## Tier 1 — changes the quality of the next video
1. Premiere Pro 2026
2. Photoshop 2026
3. Illustrator 2026
4. Audition 2026
5. Media Encoder 2026
6. Zotero
7. PureRef

## Tier 2 — QC/localization
8. Subtitle Edit
9. MediaInfo
10. Youlean Loudness Meter 2

## Tier 3 — optional after real production evidence
- iZotope RX 12
- DaVinci Resolve 21
- Pro Tools
- dedicated SFX asset manager

# YASSIN capacity note

Observed:
- Windows 11 Pro 64-bit
- Intel Core i5-12400F
- 16 GB RAM
- NVIDIA RTX 4060 Ti
- After Effects 2026 + Creative Cloud installed

This is sufficient to begin 1080p Premiere/AE work, but **RAM is the first likely bottleneck** when Premiere + AE + Photoshop/Audition run together. For sustained 4K or heavier mixed-media work, 32 GB RAM should be treated as the next hardware upgrade.

# Adoption rule

No proposed tool becomes a governing production dependency merely because it is installed.

For each new program:
1. install;
2. run one bounded qualification task;
3. record what it can/cannot do on YASSIN;
4. assign the role/tool only after PASS;
5. retain exactly one primary tool for each craft function where possible.

This prevents the Studio from repeating the earlier mistake of choosing tools by availability instead of measured fitness.
