# Command Center — W1.1 WGC Pilot Evaluation

Date: 2026-10-22  
Status: PILOT FAILED / FALLBACK REVIEWED  
Scope: W1.1 evidence capture only  
PR: #72 — remains Draft / not merged

## Exact-head evidence

Candidate SHA: `4cb1bf61a5d3f1c5613227116e0d0404e5454752`  
GitHub Actions run: `39694125614`  
Artifact: `UniversalCouncil-W1-1-WGC-Pilot-4cb1bf61a5d3f1c5613227116e0d0404e5454752`  
Artifact id: `12389738471`  
Artifact digest: `sha256:811d528d44fb1e2b0c4a9bc6aba8cdb4c1bada52c761282e30fca2013d33cd86`

## WgcSharp 1.1.1 result

Strategy: `WGC_ONLY`  
Silent DXGI fallback: false  
Target: 1440×900 @ 30 FPS  
Samples requested: 30  
Successful frames: 0  
Achieved FPS: 0  
Capture call elapsed: 1886.946 ms  
Error: `WgcSharp WGC-only capture returned no frame.`

Decision:

`FAIL_PUBLIC_API_NOT_SUITABLE_FOR_GOVERNED_30FPS_RECORDER`

This failure is not a motion failure. It is evidence that the selected single-shot WgcSharp public API cannot provide the governed W1.1 evidence path on the current GitHub-hosted Windows runner.

## Source audit finding

WgcSharp 1.1.1 creates a D3D/WGC session per public capture call, skips its first frame, and performs a fixed delay before accepting another frame. That API shape is not a continuous recorder contract and must not be adopted as the W1.1 recorder.

## Bounded fallback decision

Al-Murtakaz authorizes one additional evidence-only experiment:

`PERSISTENT_RAW_WGC_SESSION_PILOT`

The implementation must:
- create one WGC session for the actual Command Center HWND;
- keep the session alive across frame samples;
- retain only the latest actual frame;
- use D3D11 staging readback;
- expose dropped/missed frame evidence;
- prohibit silent DXGI/monitor fallback;
- leave Motion DNA and thresholds unchanged;
- leave the existing RenderTargetBitmap path as diagnostic fallback only until WGC is proven;
- remain outside product/business/runtime truth.

Architectural reference only:
- `WKImods/WKI-Clipper` persistent `WgcWindowCapture` + latest-frame model.

No whole-project import is authorized.

## If persistent WGC also fails in GitHub Actions

Classify the result as a CI-host capture limitation unless product-side evidence proves otherwise. Do not modify animation to compensate. Return to Al-Murtakaz to choose among:
1. a separately governed DXGI path;
2. real YASSIN host evidence if Stage 7 governance permits;
3. another bounded capture host.

Stage 8 remains closed.
