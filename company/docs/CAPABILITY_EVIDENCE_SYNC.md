# Capability Evidence Sync v1

## Purpose
Keep UniversalCouncil aware of capabilities that are proven inside approved subprojects without allowing those subprojects to grant themselves authority.

## Producer contract
An approved subproject publishes JSON receipts under:

`.council/capability-receipts/*.json`

Each receipt must identify:
- schema version;
- receipt id;
- source project;
- full source Git commit;
- timezone-aware observed timestamp;
- capability id;
- `RUNTIME_VERIFIED` status;
- evidence level;
- verified scope;
- explicitly unverified scope;
- one or more artifact paths with SHA-256 hashes.

A receipt may not contain authority fields such as classification, effect, approval policy, authentication class, allowed/prohibited scope, or enforcement.

## Consumer contract
`company/config/evidence_sync.json` is the source allowlist and capability-to-authority binding.

`python tools/council_preflight.py`:
1. resolves approved local sources;
2. loads standardized receipts only;
3. checks capability/source allowlists;
4. verifies artifact paths remain inside the source project;
5. verifies every artifact SHA-256;
6. imports the newest receipt per capability into `company/evidence/imported/`;
7. updates only evidence metadata in `company/config/tool_authority.json`;
8. revalidates Council invariants.

## Non-escalation rule
Evidence is not authority.

Evidence Sync is allowed to update:
- `evidence_level`;
- `last_verified_at`;
- `source_or_pin`;
- `evidence_receipt`;
- `verified_scope`.

It must not modify:
- `classification`;
- `authentication_class`;
- `effect`;
- `approval_policy`;
- `allowed_scope`;
- `prohibited_scope`;
- `enforcement`.

Any attempt to place authority-changing fields in a receipt is rejected.

## Missing source behavior
A source that is unavailable on the current host is reported as unavailable. It does not fail closed into invented evidence and it does not promote a capability.

CI validates the imported evidence and registry references already committed to UniversalCouncil. Host-local artifact hashes are reverified when the approved source is available during preflight.

## YASSIN / CouncilVideoStudio
The first registered producer is `CouncilVideoStudio`.

Its first standardized receipt proves the bounded `desktop_computer_use` capability implemented by the YASSIN Control Bridge. UniversalCouncil maps that evidence to two separately governed operations:
- `desktop_computer_use.observe` — READ, owner-explicit;
- `desktop_computer_use.control` — EXECUTE, owner-gated and owner-explicit.

The shared evidence does not override the existing restrictions on credentials, security-setting bypass, purchases, external publishing, messaging, or unapproved destructive actions.
