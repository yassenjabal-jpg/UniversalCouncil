# Reference Overlay Prototype Workflow

Date: 2026-10-20  
Status: MURTAKAZ-GATED INTERACTION HARNESS  
Scope: P1 interaction/UX work while reference-capable desktop production tooling is unavailable

## Goal

Continue product work without changing or regenerating the canonical visual pixels.

The prototype renders the exact canonical Home reference image as the visible base layer and adds transparent semantic interaction regions above it.

This allows work on:

- hover/focus states;
- Role Context;
- Model & Reasoning inspection;
- keyboard access;
- composer routing semantics;
- project-card actions;
- persistent-region navigation;
- truth/disabled behavior;
- accessibility and interaction review.

## Non-authoritative status

This prototype is **not** a new visual artifact.

It cannot satisfy:

- Home visual approval;
- P1 visual completion;
- Stage 8 opening;
- runtime execution authority.

The canonical PNG remains the visible source of truth.

## Fidelity guarantee

The prototype must:

1. use `references/01-home_owner_workspace.png` directly;
2. not redraw the Home screen underneath;
3. not use generated UI imagery;
4. not alter the canonical image bytes;
5. keep all eight Home Council member identities interactive;
6. keep debug overlays optional and off by default.

## Interaction layer

The first harness covers:

- eight Council Pulse members;
- reasoning inspector entry points;
- Council / Studio / Auto routing cards;
- three Active Work project cards;
- Autopilot card;
- lower owner panels;
- primary execution action;
- Tool Dock;
- right navigation semantic regions.

## Review mode

Press `D` to toggle debug outlines.

Press `Escape` to close the active inspector.

Tab/Shift+Tab traverses interactive hotspots.

## Next use

The overlay can continue to grow while desktop tooling is unavailable.

When Photoshop/DC returns, the same semantic map becomes the implementation checklist for the editable reconstruction, so this work is not discarded.
