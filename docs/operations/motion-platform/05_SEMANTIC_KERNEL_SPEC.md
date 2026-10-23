# Motion Platform MP1 — Semantic Kernel Specification

Date: 2026-10-23
Status: IMPLEMENTATION_CANDIDATE
Parent: Motion Platform Foundation / PR #80

## Purpose

MP1 proves that motion semantics can be enforced without WPF, Rive, Lottie, Skia or any other renderer.

The kernel owns coordination, not graphics.

## Required behavior

The kernel must:
- reject motion whose backing truth requirement is not satisfied;
- require truth requirement identity to match the semantic contract;
- preserve Full vs Reduced Motion mode in the motion lease;
- generate unique motion instance IDs;
- prevent a replaced/stale instance from completing a newer visual state;
- support bounded interruption modes;
- never auto-start queued work from a stale truth snapshot;
- stop matching active motion when its backing truth is revoked;
- reject stale truth revocation from cancelling motion backed by newer truth;
- reject stale true snapshots from restarting motion after a newer false truth;
- reject conflicting snapshots that claim the same observation time;
- snapshot mutable contract inputs before retention;
- expose deterministic results that can be unit/console tested.

## Interruption semantics

REPLACE:
- cancel all active instances on the same semantic target;
- start the incoming request.

COALESCE:
- if the same semantic event is already active, do not start another;
- otherwise replace conflicting target motion.

IGNORE_DUPLICATE:
- ignore the same active semantic event;
- otherwise replace conflicting target motion.

QUEUE:
- record a bounded pending request;
- on release, return the pending semantic request to the caller;
- do NOT auto-start it;
- caller must submit again with a fresh truth snapshot.

PARALLEL_SAFE:
- allow multiple active instances on the target;
- each instance retains independent completion ownership.

## Stale completion law

Completion is accepted only for an active motion instance ID.

If instance A was replaced by B, a late completion callback from A returns STALE_COMPLETION_IGNORED and must not change B.

## Queue freshness law

Queued motion never carries authority to start later from an old truth observation.

The queue stores semantic intent only. After the active instance completes, the queued item is released and requires a newly observed truth snapshot before start.

## Truth revocation law

Product truth remains external to MotionKit.

When a newer false truth snapshot is reconciled for a target:
- matching active motion is cancelled;
- queued intents requiring the revoked truth are removed;
- if another queued intent becomes eligible for consideration, it is released only as semantic intent;
- released intent MUST be resubmitted with fresh truth before it can start.

Truth observations are monotonic per target + requirement inside a coordinator lifetime.

An older false truth observation MUST NOT cancel a lease backed by a newer truth observation.
An older true observation MUST NOT restart motion after a newer false observation.
Two materially conflicting observations with the same timestamp fail closed.

Submitting a motion request with false backing truth is rejected and also reconciles that false truth against matching active motion.

## Contract snapshot law

MotionKit snapshots retained semantic contracts at submission time.

Caller mutation of a previously supplied collection MUST NOT change:
- active semantics;
- queued semantic intent;
- later released pending intent.

## Bounds

- IDs are bounded text;
- queue depth per target is bounded;
- empty purposes are rejected;
- empty Reduced Motion equivalents are rejected;
- future-dated truth observations are rejected;
- instance IDs are never reused within a coordinator lifetime.

## Non-goals

MP1 does not:
- render;
- select a renderer;
- load assets;
- define GPU behavior;
- authorize Command Center integration;
- authorize PR #72 merge;
- change Stage 7 / Stage 8 truth.

## Acceptance

MP1 candidate must pass:
- false truth rejection;
- wrong truth identity rejection;
- start;
- replace;
- stale completion rejection;
- coalesce;
- duplicate ignore;
- queue release requiring fresh truth;
- parallel-safe instances;
- Reduced Motion lease preservation;
- truth revocation stops matching motion;
- stale truth revocation cannot cancel newer motion;
- stale true truth cannot restart after newer false truth;
- equal-time conflicting truth fails closed;
- false-truth submit revokes matching active motion;
- contract snapshot immutability;
- bounded queue;
- cancel-target cleanup.

Only after this passes may MP2 introduce a renderer adapter boundary.
