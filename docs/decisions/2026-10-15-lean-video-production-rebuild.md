# Decision: replace the DAY24 production method

Owner directive: stop permanently the lengthy DAY24 P0/P1/P2 and slow After Effects GUI workflow; redesign and implement only on the existing PR #30 branch. This decision supersedes `2026-10-14-lock-production-system-before-full-video.md` for current production, while preserving all historical evidence.

The governing replacement is [Lean Video Production Workflow v2.0](../operations/media/LEAN_VIDEO_PRODUCTION_WORKFLOW.md): five stage owners, exactly three gates, one short system pilot, Adobe After Effects native automation as the current edit/motion/delivery route, and Descript limited to rough/transcript utility work. No main merge or publication.

## Council review record

Two separately executed review agents evaluated the repository and proposal. These were actual separate agent runs in this task, not claims of external Council members or different base models. Execution/Media reviewed feasibility and latency; Risk/Red Team reviewed hidden gates, factual/rights protection and evidence integrity. The primary agent synthesizes and implements; craft authority remains with each named stage owner.

Execution findings adopted: remove both runtime mirrors of the old ladder; one consolidated cut review; maximum two script drafts, bounded missing-asset generation; no editor tournament; explicit stop after bounded backup failure. Estimated 235–360 active minutes remains an unmeasured target.

Risk findings adopted: distinguish authenticated connection from output qualification; preserve independent factual review and final QC; bind approvals to actual artifact hashes; invalidate affected approvals on content changes; keep system pilot separate from commercial observations; reject historical pilot PASS as new proof.

Tradeoff: practical semantic motion and reusable chapter layouts replace exact frame-by-frame reconstruction. Quality still requires coherent visual grammar, authentic evidence, Arabic readability, intelligible accepted narration and measured clean delivery. If the tool cannot satisfy these, report the concrete capability gap inside the existing gates.

Baseline read before edits: PR #30 draft/open, head `2564d2153e787601557883b0de5985db6a61daff`, base main `af9fabe14e58a1793c40f3237475e4e8cd05d834`; Company Stage 0 run `38635618895` and CodeQL run `38635619112` both success. Live Descript drive read succeeded; no new media pilot/export/throughput PASS was observed.


## Routing correction — 2026-10-15

Council review of the measured pilot found the original routing wasteful: the configured Descript delivery route had already demonstrated native RTL, 720p and watermark defects. The active contract now routes delivery/edit-motion to Adobe After Effects 2026 after a current-session probe. Descript remains available for rough/transcript utility work and is explicitly ineligible for Final Delivery on the current connector/plan. A primary AE failure stops as CAPABILITY_GAP; it does not silently retry the known-failed Descript delivery path.
