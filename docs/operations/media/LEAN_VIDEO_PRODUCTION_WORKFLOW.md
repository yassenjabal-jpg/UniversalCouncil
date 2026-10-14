# Lean Video Production Workflow v2.0

**Effective:** 2026-10-15, Asia/Baghdad. **Scope:** channel production on PR #30.
**State:** active governing method; one-time system pilot NOT RUN. No new video quality or throughput PASS is claimed.

This document and `company/config/channel_operating_system.json` replace the DAY24 P0/P1/P2/P3 ladder, retry phases, prototype queues and lengthy After Effects GUI automation. Repository evidence is the sole execution truth. Old material remains under a SUPERSEDED banner and in `history/DAY24_LEGACY_CONFIG_2026-10-14.json`; historical PASS is not a receipt for the new system.

## Five stages, one final authority each

| Stage | Final authority | One consolidated output | Active-work target |
|---|---|---|---|
| Research/Script | Editorial Director / Showrunner | Evidence-backed script, claim ledger, chapter beats, narration intent; independent factual observations | 60–90 min |
| Visual Direction | Visual Art Director / Frame Curator | One-page treatment: motif, palette/type, source treatment, semantic motion, asset plan and selected thumbnail brief | 20–30 min |
| Asset Pack | Media Producer / Production Coordinator | One manifest: assets, usage rights, provenance, editable Arabic text, narration, music/SFX and job receipts | 45–60 min |
| Edit/Motion | Motion & Picture Editor | One project, narration-first chapter assembly, rough cut, targeted revision, picture/audio/captions/export | 90–150 min |
| Final QC | Independent QC Reviewer | Exact master hash, measurements, full playback findings and closed defect list | 20–30 min |

Total target: **235–360 active minutes** for an 8+ minute episode. This is a planning hypothesis, not a demonstrated benchmark. Record wall time, active time, service queue and render time separately. Source complexity, owner narration availability and factual uncertainty can exceed the target; simplify visuals before weakening factual integrity or quality.

The Council designs the system and challenges material risks at the three existing gates. It does not vote on ordinary frames, prototypes, motion presets, or prompts. Stage authorities settle craft choices within the locked brief. Advisers are activated only for a concrete unresolved issue. Fact-check independence and independent final QC remain mandatory. The Producer controls cost/schedule and asset delivery; editorial truth stays with the Showrunner, visual treatment with the Art Director. The Owner retains narration identity/brand veto and publication authority; publishing is a separate authorization action, not a fourth production gate.

## Exactly three gates

1. **Preproduction Lock — Showrunner.** Approve one script+treatment+asset-plan package after independent material-claim checks, rights sourcing plan, feasible native tool route, narration plan and budget. Art Director's treatment/pack brief signoff is included in the package, not another review queue. Chapters carry evidence IDs; the source/rights ledgers remain distinct. Two script drafts maximum; further edits address specific defects rather than repeat five-pass cycles.
2. **Rough Cut Review — Showrunner.** Watch the continuous cut with its narration, temporary or final music and transitions. Send one consolidated timecoded list for story, pacing, comprehension, visual grammar, factual presentation, rights and synchronization. One normal revision round. An unresolved material defect keeps this same gate open; it does not create a new prototype gate. Editor then conforms picture, audio and subtitles in the same project.
3. **Final QC — Independent QC Reviewer.** Review the full exact export once, with targeted inspection only when a defect warrants it. Verify facts/rights, accepted human voice, Arabic shaping/RTL/mobile readability, narration completeness, visual continuity, audio intelligibility and sync. Measure 1920×1080 or higher, at least 24 fps, no watermark, −14 LUFS ±1 and true peak ≤−1 dBTP as internal delivery targets. Episode duration ≥480 seconds. Close all material defects; targeted repairs re-open only affected receipts. Check file integrity and archive the editable project, manifest and master.

No per-frame or per-prototype Council review, mandatory reference-board regeneration, animatic approval, separate spotting/picture-lock/mix/export gates, or required multi-tool bake-off. Existing craft libraries and the reference's temporal grammar are reusable guidance, not acceptance queues. Synthetic visuals never stand in for documentary evidence.

## One primary editor and one backup

**Primary: Descript through the connected native API and Agent Underlord.** One project/composition holds editing, practical semantic motion, voice, music/SFX, captions and export. Import the pack once; submit one structured editing brief covering the full narration/chapter assembly and one consolidated revision request. Observe job results and project state before claiming success. Use reusable layouts and restrained object/text motion; do not regenerate every scene or attempt exact reconstruction of every reference frame.

**Backup: Adobe After Effects 2026 through native project automation and rendering.** Activate only after a blocking primary failure, a diagnosis of at most ten minutes, and a current successful application probe. One backup activation; no GUI loops, tool tournament, or third editing tool. Reuse the same assets, narration, timing and locked creative direction. The retained historical benchmark proves only a short AE render, not current availability or an 8-minute finishing pipeline. If the backup cannot meet required motion/audio/export quality, record CAPABILITY_GAP with the concrete evidence and stop the affected delivery; do not invent a PASS.

Descript connection was verified by reading the authenticated drive. It proves access only. Arabic typography, practical motion, clean export and measured audio still need the one-time system pilot. Existing Descript DAY24 renders are historical, including their limitations. A single tool may satisfy picture and audio finishing if measured output passes Final QC; a separate NLE/DAW brand is no longer mandatory.

Native connectors/automation are expressly authorized for this media workflow by the Owner's replacement directive. The general GUI-first policy for unrelated interactive tasks is unchanged. `select_edit_route` supplies the scoped media route; operators use that route and attach actual receipts. The policy runtime is an evidence validator, not a replacement editor or a fabricated connector implementation.

## One short system pilot, once

Produce **one 30–45 second pilot** through the same five stages and three gates. Include accepted/temp clearly labelled human narration, Arabic title/caption, one authentic rights-cleared evidence asset, an explanation graphic, a semantic transition and representative music/SFX. Use existing materials where rights are clear. Measure real time, cost, generation/revision counts, sync/readability and exact export quality.

The pilot itself requires no preceding pilot. Its exact exported artifact and three accepted receipts qualify the system for full episode production; it is never repeated per episode. No P0/P1/P2 escalation, 60–90-second follow-up, prototype A/B/C comparison, or old PASS substitution. Its own Preproduction Lock covers the test scope; pilot completion is consumed inside the first full episode's Preproduction Lock, not a fourth gate. Configuration readiness and CI PASS are not media-pilot PASS.

Business observations over three released/completed episodes, retained by `validate_media_pilot_record`, measure commercial scaling only. They neither add production gates nor block an 8+ minute first episode after the single system pilot.

## Bounded assets and revisions

Reuse the documented visual kit and licensed archival/real-world sources. Generate only missing explanatory/atmospheric assets, at most two attempts per missing asset and twelve total generation jobs per episode. One official thumbnail concept, one generation job, one standalone thumbnail asset remains the rule. Keep selected prompts isolated, record prompt version/tool/output, and never allow an executor to rewrite the creative brief materially.

Art Director approves the asset-pack direction once inside Preproduction Lock. Producer checks pack completeness and rights once during stage work; this is not a fourth gate. At an exhausted budget, replace an optional generated shot with a simpler rights-cleared image/diagram/layout. Factual or rights blockers cannot be waived by the time budget. Repairs of material errors are recorded separately from routine creative revision rounds.

## Runtime receipt contract

`company/runtime/lean_video_production.py` validates the governing contract, selects the bounded editor route and evaluates production receipts. Each run identifies the episode/system revision, authors, actual artifact paths and SHA-256-bound approvals. Gates identify the final authority, named reviewer, independent checker where applicable, observed checks and explicit defect disposition.

Preproduction hashes script/direction/asset plan. Rough Cut additionally hashes actual assets and the cut. Final QC additionally hashes the export and its measurements. Changes invalidate affected downstream receipts; reexport alone preserves unchanged preproduction/rough-cut inputs but requires new export QC. A missing/empty file, stale hash, wrong authority, unreported defects, self-review, nonfinite measurement, absent pilot or out-of-spec export fails closed. The runtime checks evidence consistency; human observations and measured media remain the source of quality findings.

Use `tools/validate_video_run.py --record <run.json> --gate "Final QC" --system-pilot <pilot.json>` for episodes, omitting `--system-pilot` for the system pilot. Relative artifact paths resolve beside the record. Successful validation emits a private delivery-readiness receipt and never authorizes publication or merging.

## Cancellation and evidence

The old workflow is **SUPERSEDED_CANCELLED**, `resume_allowed=false`. No old phase/prototype is an active work item or new prerequisite. Historical docs/configuration/results are retained verbatim beneath status banners. This cancellation does not claim that an unobserved remote render/job was killed; external jobs have not been inventoried in this change. An operator finding an old in-flight job must record its identity and cancel that specific job safely without discarding unsaved work.

Governing files: this document; channel config; `media_venture.json` for role activation; `media_specialized_tool_policy.json` for native tool boundaries; lean runtime and `tools/validate_video_run.py`; the three relevant test modules plus channel tests. No merge into main, no public publish, and no automatic upload is authorized.
