# Memory Snapshot — project / media

> Generated from append-only memory events. Do not edit manually.

## media.pilot.measurement
- **Event:** `MEM-20261012-192851-3f76af`
- **Level:** `L3_CANONICAL`
- **Kind:** `requirement`
- **Confidence:** `verified`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** No full-scale media operation before a three-video pilot; measure production cost/effort and quality, and if published also measure CTR and audience-retention outcomes before scaling.
- **Details:**
  - `operational_metrics`: ["production_time_per_video", "owner_human_minutes_per_video", "tool_cost_per_video", "cost_per_published_minute", "revision_count", "factual_policy_defects", "packaging_quality"]
  - `pilot_videos`: 3
  - `pre_scale_required`: true
  - `published_metrics`: ["ctr", "first_30_second_retention", "average_percentage_viewed", "watch_time", "subscribers_per_video", "returning_viewers"]
  - `source_file`: company/config/media_venture.json
- **Tags:** media, pilot, metrics

## media.production.workflow
- **Event:** `MEM-20261012-192851-eae0a7`
- **Level:** `L3_CANONICAL`
- **Kind:** `architecture`
- **Confidence:** `verified`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** The media venture uses an end-to-end production workflow from market/research and scripting through storyboard/assets, Adobe/AI production, finishing, packaging, QC and performance learning.
- **Details:**
  - `authority_boundary`: publishing remains separately gated
  - `source_files`: ["company/config/media_venture.json", "company/docs/MEDIA_VENTURE_CAPABILITY_ACCEPTANCE.md"]
  - `workflow`: ["market and topic research", "idea and hook selection", "fact research", "script", "storyboard", "asset generation/collection", "motion assembly and editing", "audio/captions", "title/thumbnail packaging", "QC/export", "distribution when authorized", "analytics and iteration"]
- **Tags:** media, workflow, production

## media.production_cell.current
- **Event:** `MEM-20261015-025700-lean13`
- **Level:** `L3_CANONICAL`
- **Kind:** `architecture`
- **Confidence:** `verified`
- **Updated:** `2026-10-15T02:57:00+03:00`
- **Summary:** Media Production Cell v1.3 uses a small always-active Producer/Showrunner core, stage-routed craft capabilities, an explicit Cinematography / Shot Design function, and recoverable cross-application handoffs where UNKNOWN is never success.
- **Details:**
  - `added_function`: Cinematography / Shot Design
  - `anti_bureaucracy_rules`: ["do not call every function for every stage", "artifact delta or blocker by default", "parallelize independent craft work when safe", "one synthesis per gate"]
  - `core_functions`: ["Media Producer / Production Coordinator", "Editorial Director / Showrunner"]
  - `governing_config`: company/config/media_venture.json
  - `governing_doc`: docs/operations/media/MEDIA_PRODUCTION_CELL.md
  - `mandatory_clearance`: ["Independent Fact Checker"]
  - `operating_model`: SMALL_CORE_ROUTED_CRAFT_CAPABILITIES
  - `recovery_doc`: docs/operations/media/STUDIO_EXECUTION_RECOVERY.md
  - `recovery_invariants`: ["UNKNOWN != SUCCESS", "checkpoint before application handoff", "independent postcondition after state change", "same-route retry bounded to one", "authorized fallback only"]
  - `research_rationale`: docs/research/2026-10-15-agentic-video-studio-comparison.md
  - `version`: 1.3
- **Supersedes:** `MEM-20261013-015655-c15cc7`
- **Tags:** media, studio, lean-routing, cinematography, shot-design, recovery

## media.specialized_tool_policy.current
- **Event:** `MEM-20261012-212638-4d1282`
- **Level:** `L3_CANONICAL`
- **Kind:** `policy`
- **Confidence:** `verified`
- **Updated:** `2026-10-12T21:26:38+03:00`
- **Summary:** Media production now follows SPECIALIZED TOOL FIRST / CODE LAST FOR CRAFT. Code may orchestrate, validate, automate and QC, but may not substitute for missing professional editing, motion, sound-design, mixing/mastering or finishing tools. Missing craft capability is a CAPABILITY_GAP.
- **Details:**
  - `code_allowed_for`: ["orchestration", "manifests", "versioning", "automation", "QC", "provenance", "metrics"]
  - `code_not_default_substitute_for`: ["picture editing", "motion design", "sound design", "dialogue mastering", "final mix/master", "professional export/finishing"]
  - `current_desktop_gaps`: {"audition_2026": "NOT_RUNTIME_VERIFIED", "davinci_resolve_fairlight": "NOT_RUNTIME_VERIFIED", "media_encoder_2026": "NOT_RUNTIME_VERIFIED", "premiere_pro_2026": "NOT_RUNTIME_VERIFIED"}
  - `current_verified_tools`: {"after_effects_2026": "RUNTIME_VERIFIED", "canva": "INSTALLED", "descript": "CONNECTED_AND_AVAILABLE", "figma": "INSTALLED", "openart": "INSTALLED", "runway": "AUTHENTICATED_IMAGE_ONLY_NO_VIDEO_MODELS"}
  - `governing_config`: company/config/media_specialized_tool_policy.json
  - `governing_doc`: docs/operations/media/SPECIALIZED_TOOL_FIRST_POLICY.md
  - `hard_gate`: Public final master is blocked until professional NLE + professional audio finishing are runtime-verified.
  - `merge_commit`: a0365b82fe47cd709847c7a4eff7a45f89465fe3
  - `policy`: SPECIALIZED_TOOL_FIRST_CODE_LAST_FOR_CRAFT
- **Tags:** media, specialized-tools, code-last, capability-gap, quality

## media.venture.capability
- **Event:** `MEM-20261012-182200-c3d4e5`
- **Level:** `L3_CANONICAL`
- **Kind:** `status`
- **Confidence:** `verified`
- **Updated:** `2026-10-12T18:22:00+03:00`
- **Summary:** Media venture uses a venture-scoped production team and requires a 3-video pilot before scale; After Effects motion assembly is runtime verified while full finishing/publishing/analytics remain gated.
- **Details:**
  - `after_effects_motion_assembly`: RUNTIME_VERIFIED
  - `analytics_ingestion`: NEEDS_RUNTIME_VERIFICATION
  - `live_publish_authority`: false
  - `pilot_videos`: 3
  - `platform_publishing`: CAPABILITY_GAP
  - `source_file`: company/config/media_venture.json
  - `video_editing`: PARTIAL_RUNTIME_VERIFIED
- **Tags:** media, youtube, pilot, after-effects
