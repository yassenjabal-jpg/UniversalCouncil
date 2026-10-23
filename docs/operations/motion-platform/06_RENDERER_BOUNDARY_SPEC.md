# Motion Platform MP2 — Renderer Boundary + Deterministic Test Double

Date: 2026-10-23
Status: IMPLEMENTATION_CANDIDATE
Parent: MP1 exact head `cfd965afca6c12383333c81c15a76ac6376bc05c`

## Purpose

MP2 introduces the boundary between semantic motion and visual rendering without adopting any production renderer.

The renderer is replaceable.
Product truth remains outside the renderer.

## Package boundary

### UniversalCouncil.MotionKit.Core
Owns:
- semantic contracts;
- truth ordering;
- interruption;
- motion instance ownership.

Must not reference renderer packages.

### UniversalCouncil.MotionKit.Runtime
Owns:
- renderer-neutral capabilities;
- visual variants;
- product Motion Profile resolution;
- renderer adapter interface;
- render-command validation.

Must not reference WPF, Rive, Lottie, Skia or Android.

### UniversalCouncil.MotionKit.Testing
Owns:
- deterministic fake renderer;
- renderer-boundary test helpers.

Must never become product truth or production visual evidence.

## Truth firewall

A renderer command receives:
- motion instance ID;
- product Motion Profile ID;
- target ID;
- semantic event ID;
- accessibility mode;
- visual token;
- duration;
- required renderer capabilities.

It does NOT receive:
- MotionTruthSnapshot;
- truth satisfaction;
- product state objects;
- stage authority;
- completion authority.

Renderer success means only that a visual operation was accepted/settled.
It never means the product operation succeeded.

## Capabilities

Initial renderer-neutral capability vocabulary:
- STATIC_SETTLE;
- OPACITY;
- TRANSLATION;
- SCALE;
- ROTATION;
- PATH_GEOMETRY;
- DYNAMIC_DRAWING;
- STATEFUL_VECTOR;
- PREAUTHORED_TIMELINE;
- HIT_TESTING;
- COLOR_BINDING.

Capabilities describe technical needs, not library brands.

## Motion Profile

A product profile maps semantic event ID -> two explicit visual variants:

FULL:
- token;
- duration;
- required capabilities.

REDUCED:
- token;
- duration;
- required capabilities.

Reduced Motion is therefore a first-class variant, not duration=0 applied to Full Motion.

The profile is snapshotted at resolver creation.
Caller mutation after creation must not affect resolved commands.

## Adapter contract

Every adapter exposes:
- stable adapter ID;
- explicit adapter version;
- capability set;
- BeginAsync;
- CancelAsync;
- SettleAsync;
- diagnostics snapshot;
- async disposal.

Required behavior:
- unsupported capabilities => NOT_SUPPORTED;
- invalid command => REJECTED_INVALID;
- duplicate active instance => DUPLICATE_INSTANCE;
- missing instance on cancel/settle => NOT_ACTIVE;
- StaticFallback requires STATIC_SETTLE capability;
- unsupported StaticFallback leaves the active instance intact for an explicit caller decision;
- adapter ID + version are returned in result/diagnostics evidence;
- no silent fallback;
- no product truth mutation.

## Deterministic fake renderer

The MP2 fake renderer:
- uses no timers;
- uses no random completion;
- performs no drawing;
- tracks active instance IDs;
- exposes deterministic counters;
- supports concurrent callers under a lock;
- can prove begin/cancel/settle/not-supported behavior.

It is test infrastructure only.

## Hard bounds

- IDs/tokens <= 256 chars and no control characters;
- duration 0..30 seconds at boundary level;
- unknown capability bits rejected;
- unknown settle mode rejected;
- empty instance GUID rejected;
- profile rule count <= 512.

Product profiles may impose stricter duration bands.

## Failure law

An adapter failure, NOT_SUPPORTED or NOT_ACTIVE result is visual/runtime information only.

It MUST NOT:
- change product truth;
- imply task failure/success;
- open Stage 8;
- authorize fallback silently.

A future runtime dispatcher may choose an authorized fallback, but that policy is outside MP2.

## Acceptance

MP2 must prove:
- Full variant resolution;
- Reduced variant resolution;
- profile snapshot immutability;
- missing-rule fail closed;
- invalid-profile fail closed;
- renderer command contains no truth object;
- renderer command carries Motion Profile identity;
- render results/diagnostics carry adapter version identity;
- supported fake begin;
- unsupported capability rejection;
- duplicate instance rejection;
- settle/cancel/not-active behavior;
- StaticFallback capability enforcement without silent destruction;
- invalid adapter version rejection;
- unknown capability rejection;
- concurrent fake renderer behavior;
- disposal cleanup.

Only after this passes may MP3 test real renderer candidates.
