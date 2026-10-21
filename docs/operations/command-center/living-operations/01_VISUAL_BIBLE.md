# Living Operations Visual Bible

Status: IMPLEMENTATION DESIGN CONTRACT  
Platform scope: Windows + Android

The eight pinned images in `living-operations-reference-manifest.json` govern appearance. See `19_REFERENCE_FIDELITY_AUDIT_AND_CONTRACT.md` for the screen-by-screen mapping and correction rationale. Tokens below are implementation approximations, not measured image samples.

## 1. Visual principle

UniversalCouncil should feel like a living operational system in which work, evidence, decisions, tools and roles are tangible objects.

The aesthetic must remain professional.

Target perception:
- intelligent, not mystical;
- lively, not noisy;
- editorial, not corporate-admin;
- spatial, not dashboard-only;
- evidence-aware, not confidence-theater.

## 2. Base surfaces

Light is the primary theme.

Recommended semantic tokens:

- `canvas`: warm near-white — #F7F6F2
- `workspace`: #FBFAF7
- `surface`: #FFFFFF
- `surface-muted`: #F2F2EF
- `ink-primary`: #14213D
- `ink-secondary`: #5F6878
- `border`: #DCE1E8
- `border-strong`: #BFC8D6

Dark mode may be designed later using the same semantic hierarchy; it must not become neon/cyberpunk.

## 3. Semantic colors

Color has two explicit layers: stable role/branch identity and operational state badges. Preserve the reference multicolor medallions, pastel panels, blue actions, violet reasoning and green verified states. Identity color alone never proves activity or success.

- Active / Execution: Blue #2F6BFF
- Verified / Accepted / Completed: Green #16A36E
- Owner Decision / Attention / Suggestion: Gold #D79A18
- Blocker / Risk / Dangerous state: Coral #E35C66
- Reasoning / Discovery / Unknown: Violet #7857E6
- Tool / Connection / Operational activity: Cyan #24AFC9

Rules:
- one object may have one primary semantic state at a time;
- retain the distinct reference role colors at the same restrained coverage;
- secondary role identity may tint a Sigil while state color remains authoritative;
- red is not used for ordinary negative sentiment; reserve it for real blocker/risk/destructive context.

## 4. Typography

Arabic RTL is primary.

Windows preferred family:
- Segoe UI Variable / Segoe UI as first platform-native choice;
- Arabic fallback that preserves clear modern forms.

Android:
- platform-native Noto/Sans Arabic-compatible system typography.

Hierarchy:
- Screen title: match the parent image; Home and completion use prominent bold Arabic headlines, while project titles follow their reference hierarchy.
- Project title: strongest contextual label.
- Section heading: compact.
- Body: readable at normal desktop distance.
- Metadata: never so small that evidence timestamps become unreadable.

Numerical/status data may use tabular figures where available.

English technical terms are permitted when they are product concepts:
`Autopilot`, `VERIFIED`, `UNKNOWN`, `Checkpoint`, `Fork`, `Deep`, provider/tool names.

## 5. Spacing and density

Use an 8px base rhythm with 4px micro increments.

Desktop:
- compact navigation;
- high information density in Project Workspace;
- lower density in Decision Mode;
- visible whitespace around primary focus.

Android:
- touch targets >= 48dp;
- fewer simultaneous objects;
- progressive disclosure.

No large empty hero regions that displace active work.

## 6. Depth model

Depth comes primarily from:
1. tonal surface difference;
2. border strength;
3. focus/contrast;
4. overlap when functionally meaningful.

Preserve the references’ soft card shadows, pastel gradients, luminous circular medallions, subtle halo layers and rounded bordered panels. Do not flatten these into monochrome admin cards.

Decision Mode is the strongest elevated surface.

Hover/focus may use subtle border/intensity change before shadow.

## 7. Role Sigil language

Role Sigils use the reference pictograms inside colored circular medallions (database, user symbol, shield, crown, lock, branching paths). The generic user glyph is allowed; photographic portraits and invented human mascots are not.

Family traits:
- geometric;
- built from shared stroke/shape grammar;
- recognizable at 20–24px;
- expressive at 48–72px;
- supports rings, badges and state layers;
- no face/avatar dependency.

Semantic descriptions only; do not replace the visible reference glyphs with newly invented geometry:

Concept families:
- Evidence — lens/layer verification geometry;
- Red Team — split/opposed prism;
- UX/Human — human-centered flow;
- Synthesis — converging paths;
- Risk — contained warning/impact geometry;
- Studio — frame/timeline/motion geometry;
- Security — protected enclosure;
- Execution — directed operational vector.

State changes may alter:
- ring;
- stroke intensity;
- semantic badge;
- tiny motion treatment.

They must not replace truth labels.

## 8. Iconography

Icons must be:
- simple;
- consistent stroke weight;
- understandable without color;
- supported by labels in ambiguous or high-impact contexts.

Do not use decorative icons that look clickable without a destination.

Every interactive icon must have:
- accessible name;
- tooltip on desktop;
- visible pressed/focused state;
- destination/action documented in Interaction Choreography.

## 9. Project visual anatomy

The Project Workspace must expose a visual hierarchy:

1. Project identity and health.
2. Current stage + Autopilot state.
3. current artifact/current work.
4. Filmstrip/history.
5. owner decisions/blockers.
6. activated roles.
7. tools/models/evidence.
8. deep system detail on demand.

The project is not reduced to a grid of equally weighted panels.

## 10. Media-first adaptation

Project workspaces adapt to artifact type.

Software:
- branch/fork;
- diff;
- tests;
- CI;
- runtime evidence;
- checkpoints.

Video:
- preview;
- timeline;
- waveform;
- markers;
- thumbnail variants;
- render/QC.

Design:
- primary canvas;
- before/after;
- variants;
- comments;
- approval comparison.

Shared chrome remains consistent while the workspace center changes.

## 11. Truth badges

Canonical visible labels:
- VERIFIED
- EVIDENCE-BACKED
- PROPOSAL
- UNKNOWN
- OWNER-DIRECTIVE

Do not hide truth state behind color alone.

## 12. Visual anti-patterns

Reject:
- neon cyberpunk;
- any decorative theme, scenic motif or background language not directly observable in the eight pinned references;
- cartoon room scenes;
- mascot-heavy UI;
- generic KPI tile dashboard;
- glassmorphism as a primary system;
- gradients or glows that restyle the reference; subtle reference gradients and halos are required where present;
- glowing every active object simultaneously;
- excessive saturated color coverage beyond the reference medallions;
- copying the reference video's character/layout/card system.

