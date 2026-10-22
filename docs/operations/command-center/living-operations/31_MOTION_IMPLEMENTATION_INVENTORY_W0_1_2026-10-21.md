# W0.1 — Motion Implementation Inventory + Baseline Freeze
## CC-MOTION-W0-1-IMPLEMENTATION-INVENTORY-2026-10-21

Status: **MOTION_RETURN_BASELINE_LOCK**  
Phase: **W0.1 — Formal Return + Baseline Freeze**  
Audited implementation HEAD: `9285da24be6bee97564f7f47cbcaf7dee1ad3989`  
Canonical base: `4b2a7bffe93e1defc93080906f87d7f8d123d66f`  
PR: **#72 — OPEN / DRAFT / NOT MERGED**  
Return Ticket: `CC-MOTION-RT-001-2026-10-21` — **OPEN**

## 1. Formal return is retained

The owner's rejection of the prior motion evidence remains an acceptance failure. The current branch is a **Wave 0 implementation experiment**, not a final motion candidate. Nothing in W0.1 authorizes merge, Stage 8, runtime authority, live execution, or a visual redesign.

The exact-head P1 evidence run `39651044966` produced WPF and Android artifacts successfully, but the Al-Murtakaz evidence gate failed. The governing full-motion threshold remains **60 visibly changing frames**; the known result is **52**. This threshold is not reduced.

## 2. Frozen canonical visual baseline

The visual baseline is the exact eight-image set governed by `18_REFERENCE_ONLY_VISUAL_LOCK.md` and `state/command-center/living-operations-reference-manifest.json`. The WPF project links these files as Resources through `UniversalCouncil.CommandCenter.csproj`; no replacement visual system is authorized.

| # | Role | Git blob SHA | Governing SHA-256 |
|---:|---|---|---|
| 1 | `home_owner_workspace` | `9a76a1f6a7465efd7cd4c2a4dc22675884472416` | `7cb7d12f8819576ad4992158f6f0eb098ae3350a3684118ffc43192ea56749eb` |
| 2 | `living_project_workspace` | `c2f3f70892a6ed63ba651398a4cd522810d9644b` | `6f412a1f11e9e9f32df810194dbd4df1c42b973be9dcfb80354f10fb1cf3b799` |
| 3 | `software_autopilot_project` | `1a24721098bf11dfd3b87ca7ad7ec2a64967d6eb` | `cb2c26d0d54a0a0c6aef3d03cc65737d3a27084fe8228112b719379d7ab966ec` |
| 4 | `studio_project` | `0e146dfa224b7c91a0f42aedc3d2c82b897bbd03` | `e2f012f6207006a5068152027ccbef8cd55f866b25e60899a113937ebe523664` |
| 5 | `owner_decision_mode` | `488b1f468c82adc38cc8095f547e9bba6ef0000b` | `6351f755874fd9cec7cad4d8136d6c84eb8c3e8111a1d9ba219054f6d2488eeb` |
| 6 | `checkpoint_recovery_fork` | `fa8b40914e39c02b1ff7552a837297b9f59d8ef0` | `7b1ceb447bebb3e9d488749e1beb4f82bf03fb078e58a2035c3ed2a58fe69076` |
| 7 | `pulse_visual_project_story` | `1936832c57e1ec7422a4236d20627780a4868e01` | `f92ff13312e11ac6e52914a8cb595e0c870027f45ea8161aadaf72217cb483ed` |
| 8 | `project_complete_work_receipt` | `fbf62d916d66e7a8a97dedf2aea4923a70ad90a2` | `f8db7163bc4e5396cd2d58563cf2d513504cef7863da299851142ce554e22b7f` |

Visual law remains: **REFERENCE FIRST, DELTA SECOND, NO VISUAL REINVENTION**.

## 3. Signature motion implementation coverage

| Signature family | Status | What exists at audited HEAD | Governing sequence still missing |
|---|---|---|---|
| `ROLE_ACTIVATION` | **PARTIAL** | bounded activation ring/pulse; 480ms route line from a screen-specific hard-coded origin to clicked role | ROLE_ACTIVATED semantic-event consumption; event-backed participating-role set; route identity/provenance bound to a real routing event |
| `ARTIFACT_HANDOFF_RETURN` | **PARTIAL** | 620ms local artifact travel inside the Handoff Pulse target | real source object highlight; semantic source-to-destination route; destination acceptance highlight; ARTIFACT_HANDOFF_STARTED/ACCEPTED event backing; ARTIFACT_RETURNED reverse route; inspectable Return Ticket transition |
| `OWNER_DECISION_FOCUS` | **PARTIAL** | 700ms generic Decision screen entrance; static background de-emphasis in native reconstruction; bounded local action cue; truthful owner intent preview | OWNER_DECISION_REQUIRED event-backed hierarchy transition; decision-card elevation choreography distinct from generic screen entry; OWNER_DECISION_RECORDED resolution-to-history transition |
| `RECOVERY` | **PARTIAL** | 620ms bounded rewind marker; truthful RECOVERY INTENT PREVIEW with no fake restored state | forward-flow stop tied to recovery state; focus actual last VERIFIED checkpoint; pending restored-state hold; CHECKPOINT_RESTORED_VERIFIED settlement; failure-to-UNKNOWN/HOLD choreography |
| `FORK_BRANCH` | **PARTIAL** | 640ms temporary line split cue; static branch comparison visuals; truthful non-authoritative intent preview | FORK_CREATED event backing; source rail pause; A/B identity emergence as part of motion; original-preserved transition; equal-weight compare transition; explicit BRANCH_SELECTED settlement |
| `VERIFIED_COMPLETION_WORK_RECEIPT` | **PARTIAL** | static Work Receipt reconstruction; 760ms generic screen entrance | PROJECT_COMPLETED_VERIFIED event consumption; verified-stage settle sequence; final-artifact gather; active-motion stop as completion semantics; restrained completion cue; event-backed next-action reveal |

### Classification rule

- **IMPLEMENTED**: governing semantic sequence exists and is backed by the required semantic state/event.
- **PARTIAL**: some visible implementation exists, but the governing sequence/event backing is incomplete.
- **MISSING**: no meaningful implementation of the required motion exists.
- **SPEC_ONLY**: documented behavior exists with no corresponding product motion path.

No signature family qualifies as fully **IMPLEMENTED** at the audited baseline.

## 4. Secondary motion inventory

- **EIGHT_SCREEN_ENTRY — IMPLEMENTED_EXPERIMENT:** Per-screen opacity/scale/translate 420-760ms; no matching exit choreography.
- **DRAWER_OPEN_CLOSE — IMPLEMENTED:** 240ms open slide + fade; 190ms close; immediate Reduced Motion state.
- **REFERENCE_IMAGE_FADE — IMPLEMENTED_MICRO:** 220ms fade; not accepted as signature motion.
- **FILMSTRIP_VERSION_ENTRY — MISSING:** Version cards are static; inspector is interactive.
- **PULSE_REVEAL — PARTIAL:** Generic bounded region cue exists; story-to-action transfer is absent.
- **PULSE_TO_TASK_DECISION_RESEARCH — SPEC_ONLY:** Drawer text describes semantic actions; no creation transition.
- **AUTOPILOT_CURRENT_STATE_CHOREOGRAPHY — SPEC_ONLY:** No WAITING_OWNER or RECOVERING event-state animation path in MainWindow.
- **ARTIFACT_RETURN — MISSING:** No reverse route / Return Ticket animation in MainWindow.

## 5. Concrete code findings

- `RunScreenEntranceMotion` adds per-screen 420–760ms opacity/scale/translate entry motion. It is useful as an experiment, but there is no corresponding semantic exit choreography.
- `AnimateRoleRouteCue` draws a 480ms route to the clicked role, but it is hotspot/fixture driven rather than a `ROLE_ACTIVATED` event consumer.
- `AnimateHandoffCue` moves a temporary artifact inside the Handoff Pulse region for 620ms. It does not encode source → destination → accept/return semantics.
- `AnimateRewindCue` is a bounded 620ms marker rewind. It does not select the real last VERIFIED checkpoint or wait for `CHECKPOINT_RESTORED_VERIFIED`.
- `AnimateForkSplitCue` draws a temporary split for 640ms. A/B identity, preserved original, compare and explicit selection are not choreographed.
- Decision actions remain **intent previews** and correctly avoid fabricating owner decisions or resumed execution.
- Work Receipt is reconstructed and navigable, but `PROJECT_COMPLETED_VERIFIED` is not consumed and the completion gather/settle sequence is absent.
- Filmstrip versions are static; Pulse-to-task/decision/research is described in the UI but not motion-implemented.
- Reduced Motion guards correctly suppress the current experiment's travel where present, but full semantic parity cannot be complete while the governing full sequences are absent.

## 6. W0.1 defects

1. **W0.1-D01 — Blocking later waves:** all six signature families remain partial.
2. **W0.1-D02 — Blocking later waves:** no event-backed verified completion and no Artifact Return reverse-route implementation.
3. **W0.1-D03 — Process:** roadmap/ticket metadata had a stale `latest_head=27252eee...`; the audited implementation baseline is `9285da24be6bee97564f7f47cbcaf7dee1ad3989`.
4. **W0.1-D04 — Acceptance:** P1 Exit Evidence run `39651044966` failed the unchanged visible-motion threshold although both capture jobs completed.

## 7. Evidence baseline

- WPF Full + Reduced Motion job: `119399680764` — success.
- Android Semantic Companion job: `119399681191` — success.
- Al-Murtakaz P1 Exit Evidence Gate job: `119401865606` — failure.
- WPF evidence artifact: `12370411610`, digest `sha256:8340cc88fa283b78d7e1165813e63694ead3e8ad4141590b7d098ad11dbac665`.
- Android artifact: `12370516017`, digest `sha256:0525470bafde1a33fd9a2bf62dfbb786599b7e633a7a029dd75634930813cb67`.

Known full-motion diagnostic: 28s / 560 frames / 20 FPS / 52 changed frames / longest continuous run 6 / 15 motion events. The acceptance floor stays 60 changed frames.

## 8. Gate verdict

**W0.1 is accepted only as a truthful baseline freeze, not as motion acceptance.**

Gate: `MOTION_RETURN_BASELINE_LOCK`

This gate means:
- owner rejection is preserved;
- PR #72 remains an experiment and may not merge;
- the exact eight-screen visual baseline is frozen;
- implemented/partial/missing coverage is explicit;
- stale evidence-head metadata is corrected to the audited evidence head;
- Stage 7 truth remains intact;
- W0.2 may begin only after this gate is committed and validated.

It does **not** mean the motion defect is solved.

W0.2 status at this document: **NOT STARTED**.
