# W1.1 — YASSIN Persistent WGC Evidence Path

Date: 2026-10-22  
Status: IMPLEMENTED / REAL-HOST EXECUTION PENDING  
Scope: EVIDENCE CAPTURE ONLY

## Purpose

Prepare exact-head Full Motion and Reduced Motion evidence on the real interactive YASSIN Windows host after GitHub-hosted WGC proved functional but unsuitable as the final compositor/cadence environment.

## Boundary

The capture implementation remains inside `UniversalCouncil.CommandCenter.UiSmoke`.

No capture dependency is introduced into:
- product runtime truth;
- business/data layers;
- MainWindow navigation semantics;
- Stage 8;
- live execution authority.

The existing RenderTargetBitmap recorder remains unchanged as a diagnostic fallback.

## New governed path

`--wgc-motion-evidence` uses:

`actual Command Center HWND -> persistent Windows.Graphics.Capture session -> latest actual BGRA frame -> 30 Hz Stopwatch sampling -> existing lossless PNG background encoder -> existing motion metrics`

No monitor fallback, DXGI fallback, interpolation, optical flow or post-production is permitted.

## Acceptance

The WGC host path is not accepted merely because it records.

The existing Full Motion thresholds remain unchanged:
- changed frames >= 90 at 30 FPS;
- longest changed run >= 9;
- motion runs >= 8.

Reduced Motion existing limits remain unchanged.

The existing real-time tolerance remains unchanged:
- capture duration within 1.25 seconds of target;
- max sample lateness <= 100 ms.

Additional WGC requirements:
- actual Command Center HWND;
- exact 1440x900 capture geometry;
- source frame errors = 0;
- fallback_used = false;
- silent_dxgi_fallback = false;
- exact-head SHA binding;
- raw frame hashes and video integrity hashes.

## YASSIN host kit

GitHub Actions now builds an exact-head host kit containing:
- published UiSmoke executable;
- `w1_1_yassin_wgc_evidence.ps1`;
- WPF-only Al-Murtakaz validator;
- exact candidate SHA.

The kit is execution tooling only. Building the kit is not real-host evidence and cannot accept W1.1.

## Current block

Remote Desktop Commander reports YASSIN online but remote commands are paused because the connected account reached its monthly tool-call allowance.

This is an external access limitation, not a product or WGC failure.

W1.1 remains ACTIVE / NOT ACCEPTED.
PR #72 remains Draft / not merged.
Stage 8 remains NOT_OPENED.
