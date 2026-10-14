# Mandatory Craft Contributors

**Effective:** 2026-10-15  
**Governing workflow:** `LEAN_VIDEO_PRODUCTION_WORKFLOW.md`  
**Purpose:** restore specialist production depth without restoring committee bureaucracy.

## Operating principle

> **Specialists produce → Stage Authority decides → Existing Gate runs once.**

A craft contributor is not a voter, gate owner or reviewer-by-default. The contributor must produce the named artifact inside the relevant stage. The artifact is SHA-bound in the run record. Missing, empty, stale or misattributed craft work blocks the stage lock.

## Required outputs

### Research / Script
- Independent Fact Checker → `claim_ledger`
- Script & Voice Director → `narration_performance_map`
- Audience Growth & Packaging Strategist → `hook_retention_notes`

### Visual Direction
- Motion & Picture Editor → `motion_feasibility_map`
- Music Supervisor & Sound Designer → `sonic_visual_intent`
- Thumbnail & Packaging Designer → `packaging_hook_continuity`

### Asset Pack
- Visual Art Director → `visual_asset_clearance`
- Music Supervisor & Sound Designer → `music_sfx_asset_plan`
- Dialogue & Mix Engineer → `dialogue_mix_input_spec`
- Thumbnail & Packaging Designer → `thumbnail_packaging_spec`

### Edit / Motion
- Script & Voice Director → `narration_continuity_notes`
- Music Supervisor & Sound Designer → `spotting_sheet`
- Dialogue & Mix Engineer → `rough_mix_receipt`
- Visual Art Director → `visual_conform_notes`

### Final QC work
- Dialogue & Mix Engineer → `final_mix_receipt`
- Independent Fact Checker → `final_fact_spotcheck`

### Conditional
If a localized variant is requested:
- Localization Producer → `localization_conform_package`

## What this does not add

- no fourth gate;
- no per-frame review;
- no per-prototype review;
- no Studio-wide vote on routine craft;
- no extra tool tournament;
- no requirement that every specialist approve every other specialist's work.

## Runtime receipt

Each `craft_outputs.<output_id>` entry contains:
- `status = COMPLETE`
- `stage`
- `function_id`
- `author_id`
- `artifact`
- `sha256`

The relevant existing gate fails closed if any mandatory output for stages already completed is missing or stale.
