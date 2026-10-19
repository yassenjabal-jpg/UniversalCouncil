# Android Owner App Screen Map

Product: UniversalCouncil Owner / Command Center Companion  
Status: MOBILE DESIGN CONTRACT

## Purpose

Android is not a miniature Windows Command Center.

Its primary jobs are:
- monitor;
- preview;
- decide;
- respond;
- pause/resume governed Autopilot controls;
- inspect evidence;
- communicate feedback.

It does not become an unrestricted Remote Desktop or execution host.

## Bottom navigation

Recommended:
1. الرئيسية
2. النبض
3. المشاريع
4. القرارات
5. المزيد

## Screen A1 — Home

Top:
- YASSIN/private connection truth;
- Autopilot global summary.

Then:
- Since You Were Away;
- Needs Your Decision;
- active projects;
- latest verified result.

No infrastructure dashboard.

## Screen A2 — Pulse

Story-like but not social.

Each item:
- project/role identity;
- media;
- truth badge;
- What changed;
- Why;
- What next.

Tap opens detail.

Swipe moves between items.

Long press may show quick actions but is never the only path.

## Screen A3 — Project

Compact project state:
- current stage;
- Autopilot;
- last checkpoint;
- current artifact preview;
- current decision/blocker;
- latest Filmstrip frames.

Primary actions:
- View Preview;
- Pause;
- Review Activity;
- Ask.

## Screen A4 — Decision Inbox

Large one-decision-per-card layout.

Show:
- project;
- decision;
- reason;
- recommendation;
- strongest dissent;
- evidence summary;
- consequences.

Actions:
- Approve;
- Request Changes;
- Reject;
- Ask;
- Inspect Evidence.

The server/gateway still performs authorization validation.

## Screen A5 — Media Review

Video:
- mobile proxy player;
- marker timeline;
- comment at timestamp;
- voice feedback;
- approve/request change.

Design:
- before/after;
- pinch for content inspection when safe;
- variant switch.

Software:
- high-level diff summary;
- test/CI status;
- branch comparison;
- deep code work remains desktop-oriented.

## Screen A6 — Autopilot Detail

Show:
- RUNNING / WAITING_OWNER / BLOCKED / RECOVERING / PAUSED / COMPLETE;
- stage;
- elapsed time;
- current model/reasoning;
- active tool;
- last checkpoint;
- recovered issue count;
- fallback usage.

Actions:
- Pause;
- Resume when allowed;
- Stop & Preserve;
- View activity.

## Screen A7 — Evidence

Evidence Peek mobile sheet first.

Full evidence only on request.

Show:
- source;
- timestamp;
- classification;
- minimum provenance.

## Screen A8 — More / System

- device enrollment/session;
- notifications;
- privacy;
- connection;
- YASSIN state;
- app settings;
- Reduce Motion;
- quiet modes;
- notification escalation.

## Notification contract

Push notifications should be concise and privacy-safe.

Examples:
- "مشروع X يحتاج قرارك."
- "Preview جديد جاهز للمراجعة."
- "Autopilot متوقف بأمان ويحتاج اختيارك."

Open action deep-links to the exact object.

Do not put:
- tokens;
- credentials;
- sensitive evidence details;
- private screenshots by default on lock screen.

## Media delivery

Default:
- thumbnails;
- compressed previews;
- 10–30 second clips when useful.

Large source/final files remain on host/storage and stream/download only on explicit request.

## Motion on Android

Use:
- shared thumbnail-to-view transition;
- bottom sheets;
- Pulse swipe;
- restrained state motion;
- limited haptic for material approval/blocker/project complete/handoff accepted.

Reduced Motion replaces travel with direct fade/state change.

## Mobile authority boundary

A mobile action such as Approve is a user intent, not authority by itself.

The gateway must validate:
- Owner;
- device;
- session;
- action;
- project;
- scope;
- nonce/idempotency/current state as applicable.

