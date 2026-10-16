# Studio Master Pipeline

Status: CANONICAL MEDIA OPERATIONS
Version: 1.3
Date: 2026-10-16

## Master structure

Every project moves through exactly three macro phases:

1. **Writing**
2. **Pre-production**
3. **Production**

The phases cannot be skipped.

A phase may return work upstream only through a formal feedback/return ticket.

---

# 1. Writing

Writing has two mandatory sections.

## 1A. Market & Title Development

The project does **not** begin with a script or an abstract subject.

It begins by finding a **YouTube-native story premise**: a specific story with a concrete anchor, unresolved tension, viewer stakes and a one-frame packaging idea.

Required sequence:

1. YouTube market/outlier scan — vidIQ
2. Cross-platform/social trend scan — Brave Browser
3. Market/opportunity synthesis — ChatGPT
4. Story premise generation — ChatGPT
5. Story feasibility check — ChatGPT
6. Packaging hypothesis — ChatGPT
7. Generate **exactly three story candidates from three distinct story archetypes**, with **exactly two title variants per story** — ChatGPT
8. Red Team stranger-click challenge — ChatGPT
9. Present the three story cards and all six title variants to the Owner
10. Owner selects exactly one title from exactly one story
11. Save **OWNER_TITLE_LOCK**

The Studio must distinguish **subject** from **story**.

Weak subject:
"AI infrastructure financing"

Required story premise:
a concrete person/object/place/event + an unexpected condition, mystery or contradiction + clear viewer stakes + a payoff that changes how the viewer sees the subject.

Each story card must include:
- topic;
- one-sentence story premise;
- story archetype;
- concrete hero anchor: person, object, place or event;
- tension, contradiction or unresolved mystery;
- viewer stakes / emotional charge;
- why now;
- market signal;
- competition level;
- one key visual;
- one structured thumbnail hypothesis;
- high visual potential;
- evidence feasibility;
- eight-minute story feasibility;
- risk notes;
- exactly two title variants.

The three candidates must use **three different story archetypes**, not merely three different subject categories.

Each thumbnail hypothesis must include:
- hero subject;
- visual tension;
- composition;
- optional 0–4 words;
- explicit confirmation that the image works without explanatory copy.

Each title variant must include:
- title;
- click reason;
- viewer promise;
- how it complements rather than repeats the thumbnail;
- Stranger Click Test = PASS;
- YouTube Title Style = PASS.

A story cannot reach the Owner if it:
- is an abstract category without a story premise;
- relies only on a short-lived trend without a durable story;
- lacks credible research material;
- lacks a concrete anchor;
- lacks tension, contradiction or mystery;
- lacks viewer stakes;
- lacks a strong one-frame thumbnail hypothesis;
- needs filler to sustain the target long-form duration;
- duplicates another candidate's story archetype.

A title cannot reach the Owner if it:
- promises something the episode cannot deliver;
- reads like a newspaper section heading, report title or generic explainer;
- requires explanatory thumbnail text to become interesting;
- fails the Stranger Click Test.

### Discovery evidence rule

Owner Title Gate requires current YouTube-native/outlier evidence.

Allowed:
- normal configured native research;
- an explicitly authorized YouTube-native fallback route that still observes real platform demand/outliers.

If native discovery becomes materially degraded, the Studio records:
**DEGRADED_DISCOVERY_HOLD**

A news/web fallback may establish factual relevance, but it cannot silently substitute for YouTube-native discovery quality.


## Owner Title Gate

The Owner is the final title authority.

The script cannot start until the Owner chooses one of the six title variants, which also locks its associated topic.

After OWNER_TITLE_LOCK:
- automatic title changes are forbidden;
- the studio may propose a revision;
- the proposal must show current title, proposed title, reason, evidence and downstream impact;
- the Owner must explicitly approve the change.

## 1B. Script Development

Entry requirement:
**OWNER_TITLE_LOCK**

W2 is a YouTube-native storytelling system, not an article-writing pipeline.

Stages:

S0 — Story Question  
S1 — Research Pack  
S2 — Story Architecture  
S3 — Hook & Retention Map  
S4 — First Script  
S5 — YouTube Editorial Rewrite  
S6 — Visual/Narrative Pass  
S7 — Independent Fact Check  
S8 — Voice/Narration Rewrite  
S9 — Red Team Retention Review  
S10 — Locked Script

### Script rules

Before the first full script, S3 must map:
- the first-30-second hook;
- the central mystery;
- the title-payoff bridge;
- open loops;
- the reason to continue through every major interval;
- a visual beat for every retention interval.

Preferred story/visual change:
**every 30–60 seconds**.

Hard ceiling:
**no more than 90 seconds without a new reason to continue**.

The opening cannot begin with background exposition before the hook.

Every major beat must declare a narrative function:
- HOOK
- SETUP
- ESCALATION
- REVEAL
- PAYOFF
- RESET

### YouTube Editorial Rewrite

S5 must remove:
- article-style paragraphs;
- institutional/report language;
- redundant context;
- filler written only to extend runtime;
- explanations that arrive before the viewer has a reason to care.

The script must be understandable when heard, not merely when read.

### Visual/Narrative Pass

S6 requires every major segment to have a visual purpose.

If a paragraph cannot become:
- evidence;
- explanation;
- action;
- demonstration;
- meaningful atmosphere;
- transition;
- or a visual reveal,

it must be rewritten or removed.

### Retention clearance

Before Script Lock:
- First-30-Second Gate = PASS
- Anti-Article Test = PASS
- Spoken-Language Test = PASS
- Visual Beat Map = PASS
- Open Loop Map = PASS
- Cold Viewer Test = PASS
- Independent Fact Check = PASS
- Red Team Retention Review = PASS
- filler segments remaining = 0
- article-like paragraphs remaining = 0
- unsourced material claims remaining = 0

The Red Team must identify likely drop-off timestamps and require each risk to be resolved before lock.

S10 may create **SCRIPT_LOCK** only after all W2 gates pass.


Writing exits only when:
- OWNER_TITLE_LOCK exists;
- SCRIPT_LOCK exists.

---

# 2. Pre-production

Entry requirement:
**SCRIPT_LOCK**

Purpose:
Turn the locked script into a complete manufacturing plan before craft production starts.

Stages:

1. Script Breakdown — ChatGPT
2. Visual Story Case — ChatGPT
3. Art Direction — Adobe Photoshop 2025
4. Asset Plan — Adobe Bridge 2025
5. Rights & Source Pre-clearance — Brave Browser
6. Shot Design — Adobe Photoshop 2025
7. Storyboard — Adobe Photoshop 2025
8. Camera & Continuity Plan — Adobe Photoshop 2025
9. Sonic Concept & Spotting — Adobe Audition 2025
10. Narration Performance Plan — ChatGPT
11. Title Promise Alignment — ChatGPT
12. Animatic — Adobe After Effects 2025
13. Production Readiness Review — ChatGPT

One stage uses one primary program.

A material script problem returns to Writing through a return ticket.

A title/story mismatch creates a proposed title revision for the Owner; it never silently changes the locked title.

Pre-production exits only at:
**PRODUCTION_READY_LOCK**

---

# 3. Production

Entry requirement:
**PRODUCTION_READY_LOCK**

Official mode:
**Serial Production Line with Feedback Gates**

Only one craft department is active on the project at a time.

The Producer remains active only as a control plane:
- schedule;
- stage opening/closing;
- checkpointing;
- handoff acceptance;
- recovery;
- bounded human-assistance coordination.

The Producer does not edit craft artifacts.

## Department sequence

### P01 — Voice & Narration
Adobe Audition 2025

Stages:
- narration recording
- dialogue cleanup
- narration master QC

Handoff:
NARRATION_MASTER_PACKET

### P02 — Visual Asset Production
Stages:
- asset ingest — Adobe Bridge 2025
- raster asset build — Adobe Photoshop 2025
- vector asset build — Adobe Illustrator 2025
- optional 3D asset build — Adobe Substance 3D Stager
- visual asset QC — Adobe Photoshop 2025

Handoff:
VISUAL_ASSET_PACKET

### P03 — Motion & Compositing
Adobe After Effects 2025

Stages:
- motion build
- compositing
- motion QC

Handoff:
MOTION_SEQUENCE_PACKET

### P04 — Picture Editing
Adobe Premiere Pro 2025

Stages:
- editorial rough cut
- picture refinement
- picture lock

Handoff:
PICTURE_LOCK_PACKET

### P05 — Sound Design & Mix
Stages:
- detailed sound design — Adobe Audition 2025
- mix/master — Adobe Audition 2025
- audio-visual sync QC — Adobe Premiere Pro 2025

Handoff:
FINAL_AUDIO_PICTURE_PACKET

### P06 — Thumbnail & Packaging
Stages:
- thumbnail composite — Adobe Photoshop 2025
- packaging typography — Adobe Illustrator 2025
- packaging variants — Adobe Photoshop 2025
- packaging QC — Adobe Photoshop 2025

Handoff:
PACKAGING_PACKET

### P07 — Assurance & Delivery
Stages:
- final fact/policy QC — Brave Browser
- anti-slop gate — Adobe Premiere Pro 2025
- optional multilingual preflight — Adobe Premiere Pro 2025
- final conform QC — Adobe Premiere Pro 2025
- render/export master — Adobe Media Encoder 2025
- export QC — Adobe Premiere Pro 2025
- Owner publish gate — Brave Browser

Handoff:
DELIVERY_MASTER_PACKET

### P08 — Learning & Archive
Stages:
- analytics postmortem — vidIQ
- project archive — Adobe Bridge 2025
- durable learning update — ChatGPT

Handoff:
PROJECT_CLOSED_PACKET

---

# One Program Per Stage

Every stage has exactly one primary program.

A craft worker may not use a second creative program simultaneously inside the same stage.

Changing program requires closing/checkpointing the current stage and opening a new stage.

Recovery/fallback is a separate recovery stage, not a silent program switch.

---

# Handoff Contract

A department must finish its required internal stages before delivery.

Every Handoff Package includes:
- project ID
- handoff ID
- source department
- target department
- completed stages
- artifact manifest
- locked artifacts
- change log
- known limitations
- QC result
- acceptance criteria
- checkpoint
- status

Valid results:

**ACCEPTED**  
The next department starts.

**REJECTED_RETURN_TO_SOURCE**  
The project returns to the source department.

The downstream department does **not** silently repair upstream work.

---

# Return Ticket

A return ticket records:
- source department
- detecting department
- artifact
- defect
- rejection reason
- requested correction
- do-not-change boundary
- resume handoff

The source department fixes its own work and reissues its handoff.

---

# Human Assistance

Human Assistance remains an on-demand bounded exception.

It does not count as a parallel craft department when it is limited to the approved human-assistance packet.

It cannot:
- bypass Owner Title Gate;
- bypass Script Lock;
- bypass Production Ready Lock;
- transfer publish authority;
- silently edit another department's locked craft work.

---

# Non-negotiable gates

G0 — Market Opportunity Gate  
G1 — Owner Title Lock  
G2 — Script Lock  
G3 — Production Ready Lock  
G4 — Narration Handoff  
G5 — Visual Asset Handoff  
G6 — Motion Handoff  
G7 — Picture Lock  
G8 — Sound/Mix + AV Sync Handoff  
G9 — Packaging Handoff  
G10 — Assurance + Export + Owner Publish Gate  
G11 — Learning + Archive Closeout
