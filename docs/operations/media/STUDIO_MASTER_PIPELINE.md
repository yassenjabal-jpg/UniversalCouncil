# Studio Master Pipeline

Status: CANONICAL MEDIA OPERATIONS
Version: 1.0
Date: 2026-10-15

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

The project does **not** begin with a script.

It begins with reading the market, current audience interest and social/platform signals.

Required sequence:

1. YouTube market scan — vidIQ
2. Cross-platform/social trend scan — Brave Browser
3. Market/opportunity synthesis — ChatGPT
4. Story feasibility check — ChatGPT
5. Generate **exactly three** title candidates — ChatGPT
6. Present all three to the Owner
7. Owner selects exactly one
8. Save **OWNER_TITLE_LOCK**

Each title card must include:
- title
- why now
- market signal
- story angle
- click reason
- viewer promise
- competition level
- visual potential
- evidence feasibility
- eight-minute story feasibility
- risk notes

A title cannot reach the Owner if it:
- relies only on a short-lived trend without a durable story;
- promises something the episode cannot deliver;
- lacks credible research material;
- lacks enough visual potential;
- needs filler to sustain the target long-form duration.

## Owner Title Gate

The Owner is the final title authority.

The script cannot start until the Owner chooses one of the three titles.

After OWNER_TITLE_LOCK:
- automatic title changes are forbidden;
- the studio may propose a revision;
- the proposal must show current title, proposed title, reason, evidence and downstream impact;
- the Owner must explicitly approve the change.

## 1B. Script Development

Entry requirement:
**OWNER_TITLE_LOCK**

Stages:

S0 — Story Question  
S1 — Research Pack  
S2 — Story Architecture  
S3 — First Script  
S4 — Editorial Rewrite  
S5 — Independent Fact Check  
S6 — Narration Rewrite  
S7 — Locked Script

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
