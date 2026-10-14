# Single Thumbnail Visual Generation Brief — 24 Hours

**Status:** APPROVED FOR SINGLE-ASSET EXECUTION  
**Decision date:** 2026-10-14  
**Governing decision:** `docs/decisions/2026-10-14-single-thumbnail-lock.md`

## 1. Identification
- Episode: من قرر أن اليوم 24 ساعة؟
- Asset type: YouTube thumbnail base / key reference frame
- Prompt version: DAY24-CS-v1.1-SINGLE
- Target tool/model: isolated text-to-image job
- Official thumbnail concept count: 1
- Authorized generation jobs for this thumbnail stage: 1
- Authorized generated thumbnail assets: 1
- Execution isolation: ONE_JOB_ONE_PROMPT_VERSION_ONE_ASSET
- Multi-panel output permitted: NO

## 2. Editorial intent
- Viewer question: لماذا قُسّم اليوم إلى هذا العدد من الوحدات تحديدًا؟
- Click promise: يجعل المشاهد يرى «اليوم نفسه» كشيء تم تقسيمه عمدًا، من دون إعطائه الإجابة التاريخية.
- One-sentence visual metaphor: قرص واحد من الورق يمثل يومًا كاملًا، نصفه مادة نهارية دافئة ونصفه مادة ليلية داكنة، وتظهر عليه تقسيمات شعاعية كأن اليوم نفسه قُطّع إلى وحدات.
- Metaphor rationale: السؤال هو فعل التقسيم، لا شكل الساعة ولا أداة قياس تاريخية.

## 3. Hero system
- Hero: one thick tactile paper/card disc only
- Image language: Conceptual Surrealism
- Layout family: L4 — Surreal Stage
- Primary focal point: radial segmentation of the single disc
- Secondary focal points: NONE
- Object budget: 1 hero object only

## 4. Composition
- Aspect ratio: 16:9
- Negative space: 50–55%
- Hero position: center-right
- Text reserve: clean left field; no text generated
- View: near-orthographic front view with subtle physical thickness
- Mobile test: must read instantly as “one whole day being divided”
- Output format: one independent image only; no triptych, diptych, collage, contact sheet, storyboard, panels, or variants

## 5. Color + light
- Dominant field: warm Paper Ivory
- Ink/contrast: charcoal
- Episode accent: deep plum / mineral red, tiny only
- Day material: warm cream/golden paper, abstract — no landscape
- Night material: deep blue-charcoal paper, abstract — no moon, stars, galaxy, or scenery
- Lighting: soft upper-left studio light
- Shadow: one restrained contact/floating shadow
- No dominant cobalt field
- No gold-luxury treatment

## 6. Surface + texture
- premium thick paper/card
- subtle paper grain
- tactile cut grooves
- extremely restrained print texture
- no cinematic atmosphere

## 7. Typography
- No text rendered by the image model.
- Arabic headline will be added later deterministically.
- Preserve clean negative space on the left.

## 8. Allowed elements
- one circular paper/card disc
- two abstract material states: daylight-paper / night-paper
- radial cut/groove logic
- subtle deep-plum/mineral-red registration accent
- soft shadow

## 9. Forbidden elements
- hands
- people
- sundial
- clock hands
- clock face
- hourglass
- numeral 24
- Arabic or Latin text
- moon
- sun as a literal object
- stars
- clouds
- landscapes
- ancient Egyptian imagery
- pyramid
- astrolabe
- zodiac
- cosmic scene
- neon
- architecture
- gold/brass luxury
- extra objects
- triptych/diptych/collage/contact sheet/storyboard/multi-panel result

## 10. Differentiation
- No city, mechanism, compass, historical figure, architecture, or archival cutout.
- Zero architecture: YES.
- The image is intentionally quieter and more abstract than the rejected pilot output.

## 11. Reference fidelity
Preserve from `1000061003.mp4`: clean editorial field, one conceptual object, bold negative space, controlled surrealism, tactile print/material treatment. Do not copy the pear, portrait, curtain, or exact cobalt layouts.

## 12. Anti-Slop test
- One hero only: PASS
- One metaphor only: PASS
- Beauty-without-meaning risk: controlled by making segmentation the dominant event
- Literal clock/sundial association: FORBIDDEN
- AI cosmic poster risk: FORBIDDEN
- Multi-panel/composite risk: FORBIDDEN
- One-second readability target: PASS BY DESIGN

## 13. Documentary boundary
- Purpose: EXPLANATION
- Synthetic realism: clearly conceptual editorial object
- Archival-evidence confusion: NO
- Historical claim is not depicted in the thumbnail

## 14. Final generation instruction
Create ONE SINGLE independent 16:9 editorial thumbnail image only. Do not create a triptych, diptych, collage, contact sheet, storyboard, split screen, multi-panel layout, variations, or multiple concepts.

Use a clean warm paper-ivory background with approximately 55% empty negative space on the LEFT. Place ONE hero object only at center-right: a thick tactile circular paper/card disc representing one complete day. The disc is split materially into two abstract halves: one warm cream/golden daylight-paper surface and one deep blue-charcoal night-paper surface. These are abstract paper materials only — NO literal sun, moon, stars, clouds, landscape, sky scene, or cosmic imagery.

Across the same single disc, show clean radial cut grooves/segment boundaries so it looks as if the whole day has been deliberately divided into units. The segmentation must be the dominant visual idea. Do not display or imply a count with numerals; exact 24 geometry will be handled later in deterministic vector post.

Use near-orthographic frontal composition with subtle disc thickness, soft upper-left studio light, one restrained soft shadow, subtle premium paper grain, charcoal edge definition, and a tiny deep-plum/mineral-red registration accent. The result should feel intelligent, calm, graphic, premium, slightly strange, and immediately readable on a phone.

No text. No people. No hand. No clock. No sundial. No hourglass. No architecture. No historical artifacts. No extra object.

## 15. Negative constraints
Reject any output with multiple panels, multiple hero objects, hand, person, moon, sun, stars, clouds, scenic wedges, landscapes, clock face, hands, sundial, hourglass, numeral 24, text, Egyptian imagery, pyramid, astrolabe, zodiac, cosmic fantasy, neon, gold/brass luxury, architectural imagery, or dominant blue background. Reject if it reads as a decorative celestial poster instead of “one day being divided.”

## 16. Approval
- Visual Art Director: APPROVE
- Thumbnail & Packaging Designer: APPROVE
- Synthesis: APPROVE
- Red Team / Anti-Slop: APPROVED_BY_ANTI_SLOP
- Material deviations permitted: NONE
