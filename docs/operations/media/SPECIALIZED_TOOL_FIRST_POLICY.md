# Specialized Tool First — Media Craft Policy

## Why this exists

The Council developed a bias toward solving any missing capability with Python, JSON, validators or custom scripts.

That is useful for software engineering and governance.
It is harmful when the work is visual design, editing, motion graphics, sound design, dialogue cleanup, mixing or mastering.

## Governing rule

**Creative craft is executed in specialized creative tools. Code coordinates the work; code does not replace the craft tool.**

If a required professional tool is unavailable:
**declare CAPABILITY_GAP**.

Do not silently replace it with:
- Python video editing;
- FFmpeg as a creative editor;
- a custom audio-cleaning script;
- generated HTML/canvas as final art direction;
- a homemade renderer because Premiere/Audition/Resolve is absent.

## Current real environment — 2026-10-12

Verified on YASSIN:
- Adobe After Effects 2026 — installed and runtime verified.
- Adobe Creative Cloud — installed.
- Premiere Pro 2026 — not found in the probed standard location / not runtime verified.
- Adobe Audition 2026 — not found / not runtime verified.
- Adobe Media Encoder 2026 — not found / not runtime verified.

Connected ChatGPT media tools:
- Descript — installed and connected.
- Runway — installed and authenticated; current workspace exposes image models but **no video models**.
- OpenArt — installed.
- Canva — installed.
- Figma — installed.

## Correct production mapping

### Research
Use web/vidIQ/Trends/social sources.
Code may aggregate evidence, never invent market data.

### Frames and art direction
Use Figma / Canva / image generation / OpenArt.
The frame must be visually reviewed.

### Still generation
Use OpenAI Image / OpenArt / available Runway image models.

### Motion
Use After Effects.
JSX or automation may drive After Effects; the animation is still authored/rendered in After Effects.

### Dialogue cleanup
Use Descript today.
Use Audition/Fairlight when available for detailed technical work.

### Picture editing
Use a real NLE.
Descript can be used for rough/text-based editing.
Public high-quality finishing is blocked until a professional NLE path is runtime verified.

### Sound design and final mix
Use a DAW/NLE audio environment such as Audition or Fairlight.
No Python substitute.

### Delivery
Use the professional NLE/export pipeline.
Code may verify checksums, filenames, loudness reports and archives.

## Public-master gate

The channel may continue:
- research;
- writing;
- voice tests;
- reference frames;
- storyboard;
- animatic;
- After Effects motion tests;
- Descript dialogue cleanup.

But the first **public final master** is blocked until a professional finishing path is runtime verified.

Acceptable examples:
- Premiere Pro + Audition (+ Media Encoder where useful); or
- DaVinci Resolve + Fairlight; or
- another professionally justified equivalent approved by the Council.

## Tool scouting rule

When a craft capability is missing:

1. Search existing connected tools.
2. Check installed desktop software.
3. Search Plugin Directory / official options.
4. Prefer a mature specialized tool.
5. Ask Owner only when installation, subscription, credentials or spend is required.
6. Mark capability gap until verified.
7. Do not write a replacement craft engine by default.

## What code is still for

Good uses of code:
- manifests;
- naming;
- versioning;
- cue sheets;
- edit decision interchange;
- tool routing;
- project setup;
- repetitive AE operations;
- render queue control;
- QC reports;
- asset provenance;
- checksums;
- metric logging;
- automation after the creative workflow is proven.

Bad uses:
- “we do not have an NLE, so build one”;
- “we do not have a DAW, so master audio with a Python filter chain”;
- “we do not have a designer, so generate a JSON layout and call it finished”.

## Completion language

The Council may say:
- PROCESS_DEFINED
- TOOL_AVAILABLE
- RUNTIME_VERIFIED
- CAPABILITY_GAP
- PILOT_OUTPUT_VERIFIED
- PUBLIC_MASTER_VERIFIED

It may not say “done” for a creative stage just because code/config exists.
