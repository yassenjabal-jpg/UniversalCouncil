# Home Reference Overlay Prototype

This is a non-authoritative interaction harness.

It displays the exact canonical Home reference image and places transparent semantic controls above it.

## Run

From the repository root:

```bash
python -m http.server 8080
```

Then open:

`/docs/operations/command-center/living-operations/prototypes/home-reference-overlay/`

Directly opening `index.html` also works in modern browsers.

## Controls

- Tab / Shift+Tab: traverse hotspots.
- Enter / Space: activate focused semantic object.
- D: toggle hotspot debug outlines.
- Escape: close inspector.

## Fidelity

Visible base image:

`../../references/01-home_owner_workspace.png`

The prototype must never replace this with generated UI pixels.

## Scope

This proves interaction semantics while desktop/Photoshop tooling is unavailable.

It is **not** a P1 visual artifact and cannot be approved as the final Home design.
