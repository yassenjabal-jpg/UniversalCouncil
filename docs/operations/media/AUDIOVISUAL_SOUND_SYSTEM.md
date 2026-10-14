> **Procedure precedence:** [Lean Workflow v2.0](LEAN_VIDEO_PRODUCTION_WORKFLOW.md) governs production. Any pilot ladders, per-frame/prototype reviews, additional gates or mandatory tool comparisons below are SUPERSEDED. Craft/reference guidance remains reusable; its historical approval labels do not approve a new export.

# Audio-Visual Sound System v1

## Core doctrine

**Sound is designed with picture, not added after picture.**

The soundtrack is a narrative layer equal to typography, color, framing and motion.

The system has four independent audio dimensions:
1. Dialogue / Narration (DX)
2. Music (MX)
3. Sound Design / Effects (FX)
4. Atmosphere / Room / Texture (AMB)

Final output also includes FULL master.

---

## 1. Sonic Concept — before Reference Frame Lock

Owner:
Music Supervisor & Sound Designer.

Created immediately after Story Thesis + Visual Treatment.

Required fields:
- episode sound world;
- music-state arc;
- instrumentation palette;
- episode sonic motifs;
- silence map;
- transition-sound palette;
- dialogue-density map.

Examples:

History episode:
wood, paper, clockwork, restrained strings/plucked instruments, mechanical ticks used selectively.

Digital-system episode:
soft pulses, packet-like micro-clicks, fiber/air textures, restrained synthetic rhythm.

Business episode:
paper/ledger/percussion/low pulse, not generic "corporate inspirational" music.

Rule:
The sound world changes by episode, while the channel's restraint, clarity and mix hierarchy remain consistent.

---

## 2. Spotting Session

Participants:
Showrunner
Motion & Picture Editor
Music Supervisor & Sound Designer
Script & Voice Director

Timing:
before Reference Frame Lock and again at Animatic Gate.

For every story beat decide:
- narration state;
- music state;
- SFX need;
- silence need;
- sync anchor;
- transition sonic idea;
- prelap/postlap;
- dynamic intention.

Output:
AUDIOVISUAL_BEAT_MAP.md

No final sound files are required yet.

---

## 3. Music states

M0 — Silence / room
M1 — Curiosity
M2 — Motion / build
M3 — Explanation bed
M4 — Tension
M5 — Reveal
M6 — Reflection
M7 — Resolution

These states are narrative roles, not fixed tracks.

### Music rules

- do not run one bed continuously under the whole video;
- use silence as contrast;
- never add a riser simply because a reveal occurs;
- arrangement must leave room for Arabic consonants and narration;
- use music changes at story-state changes, not every edit;
- avoid over-scoring factual explanation;
- no licensing/source ambiguity;
- save stems whenever possible.

---

## 4. Cue Sheet

Every cue includes:
- Cue ID
- In TC
- Out TC
- Duration
- Music state
- Narrative purpose
- Energy
- BPM/tempo
- Tonal center/key if relevant
- Instrumentation
- Source/license
- Stem availability
- Dialogue density
- Sync hits
- Ducking note
- Edit points

A cue may be:
licensed music,
original composition,
generated music with valid rights/provenance,
or silence.

Assurance must be able to answer:
"Why are we legally allowed to use this?"

---

## 5. Sound Design

Sound design should explain material, motion and scale.

### Useful categories

Object:
paper, clock, metal, glass, cable, switch, page.

Mechanism:
gear, data movement, line draw, route, connection, flow.

Transition:
object pass, page shift, masked reveal, zoom-through.

Scale:
subtle impact/air/low-frequency support.

Atmosphere:
room, street, archive, laboratory, nature.

### Anti-patterns

- swoosh on every transition;
- bass hit on every title;
- generic trailer boom;
- random digital glitch;
- loud UI clicks on every label;
- SFX that describe motion already obvious on screen;
- stock cinematic rise repeated across episodes.

---

## 6. Dialogue chain

Owner:
Dialogue & Mix Engineer.

Process:
1. edit/pick best takes;
2. remove errors/pickups;
3. noise repair only as necessary;
4. clip gain;
5. corrective EQ;
6. de-ess;
7. gentle dynamics;
8. automation;
9. breath editing only when distracting;
10. final intelligibility QC.

Principle:
Do not sterilize the human voice.

Keep:
- natural micro-breaths;
- small timing imperfections;
- warmth;
- real phrase rhythm.

---

## 7. Internal mix targets

These are **our production targets, not YouTube requirements**.

Program master:
- integrated target: **-14 LUFS ±1**
- true peak ceiling: **-1 dBTP**
- documentary loudness-range guideline: **~6–10 LU**

Dialogue:
- always intelligible;
- spectral space prioritized before simply lowering music;
- automation first, sidechain only when useful.

Music under dense narration:
- typically around **12–18 dB perceptually below narration**, adjusted by arrangement and frequency content.

Localized versions:
- target perceived loudness within **±1 LU** of Arabic master where practical.

Do not chase a number if intelligibility or natural dynamics become worse.

---

## 8. Audio-visual sync

### Sync anchors

Every important audiovisual hit gets:
- Beat ID
- Visual event
- Audio event
- Intended relationship

Intentional hit:
target ±1 frame.

Action SFX:
target ±1–2 frames unless deliberate anticipation/delay.

### Relationships

ON:
sound occurs with picture action.

PRELAP:
sound arrives before image to lead viewer.

POSTLAP:
sound carries across cut.

COUNTERPOINT:
sound deliberately contrasts image.

SILENCE:
no cue by design.

### Important principle

Music does not need to cut on every visual edit.
Prefer musical phrase integrity unless the edit is a narrative hit.

---

## 9. Picture Lock and reconform

Final music edit and detailed SFX begin only after Picture Lock.

Any picture timing change after lock creates:
**AUDIO_RECONFORM_REQUIRED**

Reconform checks:
- cue in/out;
- music edit;
- SFX hits;
- transition tails;
- reverb tails;
- automation;
- subtitles/dubs if timing moved.

No hidden picture changes after audio handoff.

---

## 10. Audio-Visual Sync Gate

Review full video twice:

### Pass A — eyes open
Check:
- impact alignment;
- transition feel;
- voice/picture semantic alignment;
- music arc;
- visual rhythm.

### Pass B — screen hidden / eyes closed
Check:
- story still understandable;
- music does not manipulate constantly;
- silence exists;
- narration sounds natural;
- SFX do not become noise.

### Pass C — sound muted
Check:
- visual story still coherent;
- effects are not compensating for weak visual logic.

A strong video survives all three passes differently.

---

## 11. Monitoring QC

Check on:
- good headphones/studio monitor;
- ordinary earbuds;
- phone speaker;
- mono;
- low playback volume.

Problems to catch:
- buried narration;
- harsh sibilance;
- excessive bass;
- missing ambience;
- phase cancellation;
- pumping;
- SFX spikes;
- fatigue.

---

## 12. Stem delivery

Required:
DX — dialogue
MX — music
FX — effects
AMB — ambience
FULL — master

For multilingual versions:
- preserve M&E-style combination where practical;
- dialogue remains replaceable;
- translated timing may request picture/audio reconform.

---

## 13. Audio QC defects tracked

Pilot logs:
- audio_revision_count
- dialogue_cleanup_minutes
- music_sound_design_minutes
- mix_master_minutes
- av_sync_defects
- audio_qc_defects

Goal:
quality improves while revision and cleanup time decline.
