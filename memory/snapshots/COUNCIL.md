# Memory Snapshot — COUNCIL

> Generated from append-only memory events. Do not edit manually.

## council.agent_runtime_truthfulness
- **Event:** `MEM-20261012-192851-8f2e25`
- **Level:** `L3_CANONICAL`
- **Kind:** `policy`
- **Confidence:** `evidence_backed`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** Do not describe Council role perspectives as physically independent agents unless separate model/runtime processes actually exist; role simulations in one ChatGPT execution context must be labeled honestly.
- **Details:**
  - `claim_separate_agents_only_with_runtime_evidence`: true
  - `current_rule`: structured independent position contracts may exist within one model context
- **Tags:** council, agents, truthfulness, runtime

## council.desktop_computer_use.contract
- **Event:** `MEM-20261012-192851-a4376c`
- **Level:** `L3_CANONICAL`
- **Kind:** `architecture`
- **Confidence:** `verified`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** Full Windows desktop control is a first-class execution capability, not a permanent Council member; prefer application-native automation, then semantic UI Automation, and use physical mouse/keyboard only as fallback with verified before/after state.
- **Details:**
  - `control_hierarchy`: ["application-native API/script", "semantic UIA", "pywinauto fallback", "physical keyboard/mouse last"]
  - `credential_entry_forbidden`: true
  - `implementation_repo`: CouncilVideoStudio
  - `observe_and_control_separate`: true
  - `raw_coordinate_only_when_semantic_exists`: false
  - `state_change_verification_required`: true
- **Tags:** council, desktop, uia, computer-use

## council.governance.current_structure
- **Event:** `MEM-20261012-192851-1c158b`
- **Level:** `L3_CANONICAL`
- **Kind:** `status`
- **Confidence:** `verified`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** UniversalCouncil core governance remains v0.3.0; later layered v0.4+ restructuring is a candidate pending measured bake-off and is not yet the governing role structure.
- **Details:**
  - `governing_version`: 0.3.0
  - `restructure_adopted`: false
  - `source_file`: config/roles.json
- **Tags:** council, governance, roles

## council.hybrid_execution.contract
- **Event:** `MEM-20261012-192851-ec1124`
- **Level:** `L3_CANONICAL`
- **Kind:** `architecture`
- **Confidence:** `verified`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** Council execution uses a hybrid DC+GUI fabric: native/API first, then Desktop Commander control plane, reusable routines, semantic UIA and visual GUI assistance; state-changing work requires verification and UNKNOWN is never success.
- **Details:**
  - `automation_graduation_after_verified_repeats`: 3
  - `compact_projection`: true
  - `delta_context`: true
  - `execution_order`: ["native_api_or_connector", "dc_control_plane", "reusable_routine", "gui_semantic_uia", "gui_visual_assist"]
  - `max_deterministic_batch_steps`: 6
  - `raw_coordinates_enabled`: false
  - `single_physical_controller`: true
  - `source_file`: company/config/hybrid_execution.json
  - `t3_owner_confirmation_required`: true
- **Tags:** council, hybrid, dc, gui, verification

## council.restructure.layered_candidate
- **Event:** `MEM-20261012-192851-99b4c6`
- **Level:** `L3_CANONICAL`
- **Kind:** `proposal`
- **Confidence:** `evidence_backed`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** The preferred restructuring candidate is a layered Council with a Decision Orchestrator, bounded core challenge capabilities, on-demand specialist federation, separate operators and meta-governance; adoption requires bake-off evidence before changing governing role files.
- **Details:**
  - `adoption_state`: PROVISIONAL_RESTRUCTURE_CANDIDATE
  - `candidate_layers`: ["Owner", "Decision Orchestrator", "Core challenge capabilities", "Specialist federation", "Operators", "Venture cells", "Meta-governance"]
  - `core_challenges`: ["Evidence & Verification", "Red Team / Falsification", "Execution & Feasibility", "Risk & Assurance", "Human & Adoption", "Value & Economics"]
  - `do_not_change_governing_roles_without_bakeoff`: true
- **Tags:** council, restructure, candidate, bakeoff

## memory.fabric.queue_runtime
- **Event:** `MEM-20261012-184951-a40fa1`
- **Level:** `L3_CANONICAL`
- **Kind:** `capability`
- **Confidence:** `verified`
- **Updated:** `2026-10-12T18:49:51+03:00`
- **Summary:** Queue-based Universal Memory autosync is runtime verified after PR #16: writes stage in the gitignored pending queue, sync to GitHub main, and leave the working tree clean after successful delivery.
- **Details:**
  - `acceptance_checks`: ["pending queue receives event", "serialized autosync pushes to GitHub main", "successful sync clears processed pending event", "tracked working tree remains clean", "GitHub Memory Rebuild regenerates canonical catalog", "Memory Preflight and FTS retrieval observe the event"]
  - `acceptance_host`: YASSIN
  - `merge_commit`: 83c395de9918c70a67a3f27e3364a5e6d5465176
  - `pr`: 16
- **Tags:** memory, autosync, queue, github, runtime-verified

## memory.fabric.runtime
- **Event:** `MEM-20261012-183737-303672`
- **Level:** `L3_CANONICAL`
- **Kind:** `capability`
- **Confidence:** `verified`
- **Updated:** `2026-10-12T18:37:37+03:00`
- **Summary:** Universal Memory Fabric completed a real YASSIN-to-GitHub autosync round trip and is runtime verified for append-only event persistence, canonical rebuild, Git-backed preflight, and local FTS retrieval.
- **Details:**
  - `acceptance_host`: YASSIN
  - `acceptance_steps`: ["local memory event write", "detached origin/main worktree sync", "GitHub main push", "canonical snapshot/catalog rebuild", "Git-backed Memory Preflight", "SQLite FTS retrieval"]
  - `implementation_merge`: bddbf13634162d404569006499f244c3e555f299
  - `initial_rebuild_commit`: 660ba5ea172466fa5cc142c87b6e83bfef7f27ba
- **Tags:** memory, github, runtime-verified, autosync

## memory.migration.legacy_artifacts_round2
- **Event:** `MEM-20261012-193314-f37832`
- **Level:** `L3_CANONICAL`
- **Kind:** `status`
- **Confidence:** `verified`
- **Updated:** `2026-10-12T19:33:14+03:00`
- **Summary:** Legacy memory migration round 2 recovered the original Media Venture Council synthesis and all five channel concept decks from the ChatGPT Library and converted their durable strategy into canonical GitHub memory.
- **Details:**
  - `no_sensitive_personal_data_migrated`: true
  - `policy_boundary`: historical platform policy findings are timestamped context and must be refreshed before operational decisions
  - `recovered_files`: ["00_Council_Synthesis_Media_Venture(1).pdf", "01_What_If_Arabia.pdf", "02_Inside_The_Deal.pdf", "03_File_404.pdf", "04_Behind_The_System.pdf", "05_City_2099.pdf"]
  - `recovery_scope`: YouTube/Media venture only
- **Tags:** memory, migration, library, round2

## memory.migration.legacy_chat_round1
- **Event:** `MEM-20261012-192851-bfc437`
- **Level:** `L3_CANONICAL`
- **Kind:** `status`
- **Confidence:** `verified`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** Legacy memory migration round 1 captures durable YouTube/Media strategy, RevenueSystem requirements, and Council architecture/governance context; exact historical five-channel concepts and detailed prior YouTube policy findings remain intentionally unresolved rather than guessed.
- **Details:**
  - `excluded_sensitive_domains`: ["health/private personal context"]
  - `migrated_domains`: ["project/youtube", "project/media", "project/revenuesystem", "council"]
  - `migration_rule`: requirements from chat are not execution evidence; repository remains source of truth
  - `remaining_recovery`: ["exact historical five channel concepts", "exact prior YouTube policy/monetization findings", "any old artifacts not present in current repository or accessible chat context"]
- **Tags:** memory, migration, legacy-chat, round1
