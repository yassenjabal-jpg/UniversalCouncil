# Living Operations Acceptance and Review Gates

Status: IMPLEMENTATION QUALITY GATES

A screen is not accepted because it "looks close" to a concept image.

It must pass all applicable gates.

## Gate V — Visual

Pass when:
- layout follows Visual Bible;
- semantic colors are correct;
- Arabic RTL hierarchy is strong;
- Project Workspace is richer than Home;
- no generic SaaS/KPI appearance;
- Role Sigils use the approved abstract family;
- no copied reference motifs.

## Gate I — Interaction

Pass when:
- every clickable-looking object has a real action;
- every icon has destination/action documentation;
- no dead surfaces;
- disabled actions explain why;
- context is preserved;
- keyboard and touch equivalents exist where applicable.

## Gate M — Motion

Pass when:
- motion has semantic purpose;
- timing class is appropriate;
- no excessive loops;
- recovery/fork/handoff motion reflects real state;
- Reduced Motion communicates identical meaning;
- no animation precedes truth verification.

## Gate T — Truth

Pass when:
- UNKNOWN is not styled as success;
- VERIFIED comes from real evidence;
- model/provider/tool states are truthful;
- mobile/desktop do not fabricate connectivity;
- role presentation does not imply nonexistent independent agents.

## Gate E — Evidence

Pass when:
- material claims expose Evidence Peek;
- provenance is reachable without leaving core flow;
- artifact/version links are real;
- Work Receipt references evidence.

## Gate A — Accessibility

Pass when:
- full keyboard path exists on Windows;
- focus is visible;
- color is not sole carrier of meaning;
- text/touch sizing is usable;
- Reduced Motion is available;
- Android touch targets meet platform expectations.

## Gate P — Performance

Pass targets:
- responsive primary interaction;
- no permanent high-frequency animation;
- virtualized long histories;
- cached thumbnails;
- media proxy path;
- no obvious jank during routing/Filmstrip/Decision transitions.

Studio may define a stricter measured frame budget during implementation.

## Gate C — Cross-platform semantic consistency

Windows and Android must agree on:
- project state;
- Autopilot state;
- truth badge;
- checkpoint identity;
- decision identity;
- artifact/version identity.

They may differ in layout and gesture.

## Gate S — Security/Authority

Pass when:
- UI actions do not bypass gateway/application authority;
- Android approval is not treated as server authorization;
- notifications do not expose secrets;
- destructive operations are explicit;
- no new Stage 8 authority is implied.

## Screen-specific gates

### Home
- one dominant primary action;
- no infrastructure-first onboarding.

### Project
- current work obvious;
- Filmstrip real;
- activated roles inspectable;
- Autopilot state inspectable;
- tools/evidence contextual.

### Decision
- strongest dissent shown;
- consequences visible;
- recommendation not confused with authority.

### Fork/Recovery
- original history preserved;
- branch parent visible;
- recovery state truthful.

### Pulse
- media/context first;
- no social popularity mechanics;
- promotion actions create separate typed artifacts.

### Work Receipt
- only actual measured/known cost/time/model/tool information shown;
- final artifacts and evidence accessible.

## Final Studio recommendation statuses

- ACCEPT
- ACCEPT WITH MINOR FIXES
- RETURN FOR VISUAL/MOTION REWORK
- BLOCK — TRUTH/INTERACTION VIOLATION

A BLOCK on truth/authority cannot be waived by visual preference.

