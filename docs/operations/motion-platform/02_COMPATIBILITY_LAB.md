# Motion Platform — Compatibility Lab

Date: 2026-10-23
Status: LAB_SPEC_APPROVED_FOR_RESEARCH_ONLY

## Purpose

Choose renderer roles by evidence instead of preference.

No candidate is a platform dependency during this lab.

## Candidates

### Native Windows / Windows Composition
Role hypothesis:
- low-overhead micro-interaction;
- focus/selection;
- simple geometry and route movement;
- Windows-first integration.

Reference:
- Microsoft Windows App SDK samples;
- Windows Composition architecture.

### Rive
Role hypothesis:
- interactive vector objects;
- state machines;
- sigils/characters;
- complex reusable animated components.

Current public evidence reviewed 2026-10-23:
- open-source runtimes;
- MIT license for official runtimes;
- C++ runtime advances state machines and animations;
- renderer backends include D3D11/D3D12, Metal, Vulkan and OpenGL/WebGL;
- official Android runtime exists.

Status: LAB_ONLY.

### Lottie
Role hypothesis:
- finite pre-authored animations;
- After Effects-to-product handoff;
- non-authoritative illustration sequences.

Current public evidence reviewed 2026-10-23:
- Airbnb Lottie Android;
- Apache-2.0;
- After Effects JSON workflow;
- Android and Compose ecosystem.

Status: LAB_ONLY.

### SkiaSharp
Role hypothesis:
- dynamic custom 2D routes;
- diagrams;
- data-driven shapes;
- renderer-owned vector drawing.

Current public evidence reviewed 2026-10-23:
- MIT;
- cross-platform .NET 2D API;
- supports Windows classic desktop/WPF and Android among other targets.

Status: LAB_ONLY.

### Avalonia Composition — architecture reference
Role hypothesis:
- study render-thread composition architecture;
- not a Command Center migration decision.

Current public evidence reviewed 2026-10-23:
- MIT framework;
- composition animations run on the render thread;
- useful reference for programmatic high-performance animation.

Status: REFERENCE_ONLY.

### FlaUI
Role hypothesis:
- WPF/UIA semantic interaction verification;
- keyboard/pointer parity;
- actual-window behavior.

Current public evidence reviewed 2026-10-23:
- MIT;
- UIA3 works well with WPF/Windows Store apps.

Status: QA_CANDIDATE.

### BenchmarkDotNet
Role hypothesis:
- repeatable .NET microbenchmarks for orchestration/adapters;
- process-isolated measurement.

Current public evidence reviewed 2026-10-23:
- MIT;
- isolated benchmark process model.

Status: QA_CANDIDATE.

## Five mandatory reference scenarios

Every renderer candidate claiming a relevant capability must implement the same scenario contract.

### S1 — Interactive Icon
Trigger:
hover/focus -> press -> selected -> deselected.

Measure:
latency, interruption, keyboard parity, Reduced Motion.

### S2 — Stateful Sigil
States:
IDLE -> ACTIVE -> WAITING -> BLOCKED -> COMPLETE.

Rule:
UNKNOWN has no fake forward progress.

Measure:
state switching, stale callback prevention, asset overhead.

### S3 — Route Transfer
source -> route -> destination -> settle.

Interrupt:
RETURN occurs mid-transfer.

Measure:
cancel/reverse behavior, identity preservation, Reduced Motion.

### S4 — Semantic Object Handoff
artifact detaches, moves, destination acknowledges.

Interrupt:
destination becomes unavailable.

Measure:
deterministic final state and fallback.

### S5 — Dense Screen Stress
multiple independent semantic objects with user interaction.

Measure:
frame stability, CPU, allocations, memory, input responsiveness.

## Acceptance dimensions

Each candidate is scored on:
1. semantic fit;
2. interruption/cancellation;
3. state-machine support;
4. WPF integration cost;
5. Android parity;
6. authoring workflow;
7. asset versioning;
8. package/version risk;
9. accessibility;
10. Reduced Motion;
11. performance;
12. testability;
13. licensing/redistribution;
14. failure behavior.

## Hard rejection conditions

Reject candidate for foundational use if any are true:
- cannot deterministically cancel/settle;
- requires product truth inside the renderer;
- Reduced Motion cannot preserve semantics;
- unacceptable license for intended distribution;
- direct product coupling cannot be isolated behind an adapter;
- weak hardware fallback is undefined;
- repeated play leaks materially;
- keyboard/accessibility behavior regresses;
- requires redesign of locked product identity.

## Decision rule

There may be multiple winners.

The goal is NOT "pick one animation engine".

The goal is to assign the smallest reliable renderer to each motion family while preserving one semantic API.

## Evidence output

For every run retain:
- candidate version;
- commit/package version;
- OS/runtime;
- hardware class;
- scenario;
- Full Motion result;
- Reduced Motion result;
- latency/performance metrics;
- observed defects;
- recommendation: REJECT / REFERENCE_ONLY / SPECIALIST_ADAPTER / GENERAL_ADAPTER.

No adoption decision is valid without reproducible evidence.
