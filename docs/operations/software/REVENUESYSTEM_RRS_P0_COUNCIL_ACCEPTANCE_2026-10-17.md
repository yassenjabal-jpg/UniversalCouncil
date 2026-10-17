# RevenueSystem 2.0 — RRS-P0 Council Acceptance Review
Date: 2026-10-17
Status: LOCAL GO WITH CONDITIONS / CI PENDING

## Product

RevenueSystem 2.0 foundation now runs as a real isolated WPF shell, not source-only XAML.

Revenue branch:
`rebuild/rs2-p0-foundation`

Revenue PR:
`#79`

Revenue head under CI:
`a19e98a82a3a3795912ab353e895cce42e43b5ba`

## Council votes

### Art Director
**PASS FOUNDATION / REFINEMENT REQUIRED**

The shell is clearly separate from the legacy RevenueSystem. The Studio identity is visible through ivory, cobalt, brass and forest, with no architectural imagery.

Still required:
- stronger editorial hierarchy in the context bar;
- larger/clearer command-rail type at constrained sizes;
- more deliberate brass annotation;
- stronger inspector authorship;
- final packaged Arabic typography lock.

### UI/UX
**PASS FOUNDATION**

Strict viewport matrix:
- 1280×720 PASS
- 1366×768 PASS
- 1536×864 PASS
- 1600×900 PASS
- 1920×1080 request PASS within Windows 1920×1032 work area

Every run:
- 229 named visible elements
- 0 layout warnings

Workspace switching, Finance restoration, search focus and palette semantics all pass.

### Architecture
**PASS WITH DEFERRED ASYNC-ADAPTER DEBT**

No View-owned persistence was introduced.

Required before G6:
replace `FinanceLedgerReadAdapter → CustomerAccountService` synchronous wrapper with a native async read adapter.

### QA
**LOCAL PASS WITH QUALIFICATIONS**

Physical OS Ctrl+K/Escape could not be injected because the YASSIN background automation desktop correctly blocks SendInput when the target is not foreground. The source route and semantic palette behavior pass.

Actual physical 125%/150% DPI raster rendering is not proven. Effective layout equivalents pass:
- 125% equivalent: 1536×864
- 150% equivalent: 1280×720

### Performance
**BASELINE RECORDED**

Synthetic isolated startup ready:
approximately 1.39–1.40 seconds.

Working set sample:
~163.5 MB before and ~168.1 MB after 3 automation round-trips.

The 4.33 s UIA round-trip sample is explicitly **not** product switch latency; it is automation-harness timing.

## Local decision

**GO WITH CONDITIONS**

This authorizes continuation into Finance Ledger read-pilot refinement after CI closes successfully.

It does not authorize:
- final visual-system lock;
- production DB/LAN;
- merging to main without the normal gates;
- treating keyboard/DPI qualifications as solved.

## CI

GitHub Windows CI #413 is running on the exact Revenue head above and includes the dedicated RRS2 source validator and RRS2 1366×768 UI smoke.

Final P0 closure waits for that run.
