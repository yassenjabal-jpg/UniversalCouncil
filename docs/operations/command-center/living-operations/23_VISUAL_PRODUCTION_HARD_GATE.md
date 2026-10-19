# P1 Visual Production Hard Gate

Date: 2026-10-20  
Status: FAIL-CLOSED / MURTAKAZ-GATED  
Scope: canonical UI visual production during P1

## Why this exists

Repeated drift occurred because repository governance was stronger than the actual image-production path.

The repository said "reference first", but a visual tool could still be invoked from a shortened text description. Once that happened, the model compressed or reinterpreted the canonical screen:

- member/Sigil identities became generic icons;
- routing paths disappeared;
- screen regions were merged or omitted;
- unsupported roles appeared;
- multiple screens were compressed into one composite;
- the result was inspected only after drift had already occurred.

This protocol moves enforcement **before rendering**.

## Core law

For canonical UI screens in P1:

**No freeform UI generation. No text-only reconstruction. No multi-screen composite.**

The canonical reference is the immutable parent.

A visual job is allowed only when the production tool can consume the actual parent reference bytes and the job is registered before render.

## Allowed production modes

Only these modes are allowed:

### REFERENCE_EDIT

The canonical reference image is the direct input to the editing tool.

Use for:
- bounded cleanup;
- typography correction;
- alignment cleanup;
- clarity/refinement;
- state variation that preserves layout identity.

### LAYER_RECONSTRUCTION

The canonical reference is opened as the base and rebuilt into editable layers while preserving the same composition and semantic object inventory.

Use for:
- Photoshop/Figma/manual vector reconstruction;
- componentization;
- editable production master.

### PIXEL_PRESERVING_REFINEMENT

The canonical reference stays visually primary and changes are tightly bounded.

Use for:
- local cleanup;
- resolution/clarity work;
- small fidelity fixes.

## Forbidden production modes

The following are forbidden for canonical P1 UI screens:

- TEXT_TO_IMAGE;
- TEXT_ONLY_RECONSTRUCTION;
- STYLE_TRANSFER;
- GENERATED_IMAGE_DERIVATIVE;
- MULTI_SCREEN_COMPOSITE;
- MOODBOARD_DERIVATION;
- FREEFORM_REDESIGN.

A tool that cannot receive the canonical reference bytes is **not eligible** for a canonical UI job.

## Single-screen law

One visual job = one canonical parent screen.

Do not ask a model to produce Home + Project + Decision + Recovery + Receipt in one image.

Cross-screen consistency is reviewed from separate artifacts after each screen passes fidelity review.

## Preflight registration

A visual job must exist in the manifest **before rendering begins**.

Required preflight fields:

- job_id;
- parent_role;
- parent_sha256;
- production_mode;
- tool_name;
- single_screen_only = true;
- preflight_registered = true;
- screen_inventory_id;
- member_inventory_verified;
- allowed_delta;
- reference_binding_evidence path.

If any field is missing, rendering is blocked.

## Reference-binding evidence

Before rendering, create a JSON receipt proving that the production tool received the actual canonical parent.

Required receipt fields:

- job_id;
- parent_role;
- parent_path;
- parent_sha256;
- tool_name;
- production_mode;
- tool_received_reference_bytes = true;
- single_screen = true;
- render_started_after_preflight = true;
- screen_inventory_id;
- member_inventory_verified.

The validator verifies the receipt against the manifest.

A checkbox or prose claim is not enough.

## Generated-image quarantine

No generated image may become the parent/source for another canonical UI artifact.

Rejected generations are permanently quarantined.

Generated candidates may be reviewed as evidence of failure, but never promoted into the visual source chain.

## Multi-screen composite quarantine

Any output containing more than one flagship screen is not a P1 screen artifact.

It may be used only as a non-authoritative review illustration if explicitly labeled as such.

It cannot satisfy:
- Home approval;
- Project Workspace approval;
- Decision Mode approval;
- Recovery/Fork approval;
- Work Receipt approval.

## Object-inventory gate

Every job must load the matching canonical screen inventory.

For screens containing Council/Studio members:

- member/Sigil inventory must be explicitly verified;
- canonical member set must be preserved unless a reviewed delta says otherwise;
- generic icon substitution is forbidden;
- routing/state/reasoning/interaction layers may not be silently dropped.

## Tool eligibility

Eligible examples:
- Photoshop editing/reconstruction with canonical image opened;
- Figma reconstruction when the canonical image is imported as the parent;
- deterministic local layer/vector reconstruction from the canonical image.

Ineligible:
- image generation from text alone;
- any tool that cannot accept the canonical reference image;
- any workflow where the reference is merely described in prose.

## Artifact completion

After render:

1. save output;
2. compute output SHA-256;
3. create side-by-side comparison evidence;
4. inspect every required screen object;
5. inspect member/Sigil fidelity;
6. run governance review;
7. run workshop/visual review;
8. only then allow APPROVED_BY_AL_MURTAKAZ.

## Current Home consequence

`P1-HOME-ARTIFACT-001` is invalidated as a production attempt because it did not satisfy the actual-reference production path.

The next valid Home job is:

`P1-HOME-ARTIFACT-002`

It may begin only after a qualifying tool is available and the canonical Home reference is bound as a direct input.

## Fail-closed principle

When the eligible production tool is unavailable, **wait**.

Do not substitute a text-to-image tool.

Delay is preferable to another false artifact.
