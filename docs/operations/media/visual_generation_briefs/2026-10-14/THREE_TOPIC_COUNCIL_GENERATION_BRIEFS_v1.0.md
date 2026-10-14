# Three-Topic Council Visual Concept Arena + Approved Generation Briefs

**Date:** 2026-10-14  
**Branch:** `codex/channel-visual-identity-rebuild-reference-video-20261014`  
**Baseline verified before authoring:** `ad0844bd9ff814137e6776057887f33421f63678`  
**Visual system:** Modern Editorial Surrealism  
**Primary visual authority:** user-provided reference video `1000061003.mp4`  
**Governing template:** `docs/templates/media/VISUAL_GENERATION_BRIEF.md`  
**Execution rule:** NO PROMPT, NO GENERATION. NO ANTI-SLOP APPROVAL, NO EXECUTION.  
**Merge rule:** this artifact does not authorize merging PR #30 into `main`.

## 1. Council concept arena

The Council produced three materially different thumbnail hypotheses for each pilot topic. The Red Team then tested each hypothesis against the visual-bible rejection rules: one clear metaphor, one hero, mobile silhouette, meaningful negative space, no architecture/classical-art default, no blue/gold/marble shortcut, and no “beautiful but reusable” image.

### Topic 1 — كيف وُلدت بغداد؟

#### A — Object Macro — WINNER
**Metaphor:** a precision drafting compass draws one clean circle on ivory paper; exactly where the line passes, the graphite line becomes a minimal urban-plan texture, so geometry visibly turns into a city idea.  
**Hero:** the compass point + the circle line, not a hand and not a rendered city.  
**Why it works:** the frame contains an action, creates a curiosity gap, is readable in under one second, and can drive motion from line → plan. It keeps the strongest logic from the earlier successful test while removing the repeated historical sleeve/hand motif and reducing city detail.  
**Red Team:** PASS — strongest click promise and clearest episode-specific metaphor.

#### B — Editorial Cutout — REJECTED
**Metaphor:** a historical ruler portrait cutout presents a circular city plan against a flat editorial field.  
**Red Team:** REJECTED. It pushes the channel back toward classical/historical portrait language, creates synthetic-evidence risk, and the portrait itself becomes more memorable than the idea of a deliberately planned city. It is too close to a museum/editorial-history default.

#### C — Conceptual Surrealism — RESERVE / NOT FOR EXECUTION
**Metaphor:** one large flat circle is half clean geometry and half abstract aerial street texture, with the transformation occurring inside the same object.  
**Red Team:** PASS AS RESERVE, but HOLD. It is smart and zero-architecture, yet it is slightly more static and less action-driven than A. Keep as an alternate only if the Object Macro execution fails the silhouette/readability test.

**Council selection:** A only.

---

### Topic 2 — كيف تعمل البنوك؟

#### A — Object Macro — WINNER
**Metaphor:** one value token enters a clean transparent routing mechanism; inside, a small portion pauses in a reserve chamber while the main flow is redirected through simple channels toward abstract credit/payment outputs.  
**Hero:** a transparent acrylic mechanism with one clearly traceable input token.  
**Why it works:** it explains banking as routing and balance-sheet intermediation rather than as a vault, building, house, key, or pile of cash. It preserves the useful mechanism idea from the earlier test while explicitly banning steampunk and mortgage-specific imagery.  
**Red Team:** PASS — strongest one-second readability and broadest relevance to “how banks work.”

#### B — Editorial Cutout — REJECTED
**Metaphor:** an archival teller/cashier cutout with modern payment arrows and ledger overlays.  
**Red Team:** REJECTED. It is historically legible but conceptually weak; it could be pasted into many finance episodes, relies on explanatory overlays, and risks becoming a generic “bank history” thumbnail rather than a visual explanation.

#### C — Conceptual Surrealism — RESERVE / NOT FOR EXECUTION
**Metaphor:** a clean ledger sheet becomes a three-dimensional switching yard; ink rules lift off the paper into physical tracks that route one brass token through the page and back into the balance sheet.  
**Red Team:** PASS AS RESERVE, but HOLD. Elegant and on-brand, but less instantly understood on mobile than A and more dependent on small ledger detail.

**Council selection:** A only.

---

### Topic 3 — من قرر أن اليوم 24 ساعة؟

#### A — Object Macro — RESERVE / NOT FOR EXECUTION
**Metaphor:** a precision indexing tool is caught in the act of marking divisions around an otherwise blank “day disc,” turning time into an engineered partition rather than a finished clock.  
**Red Team:** PASS AS RESERVE. It avoids the sundial cliché and creates action, but it still visually sits near clockmaking/mechanical time imagery and may narrow the story too early.

#### B — Editorial Cutout — REJECTED
**Metaphor:** an ancient Egyptian timekeeping artifact or star chart is paired with a historical figure or explanatory diagram.  
**Red Team:** REJECTED. It becomes a history-textbook collage, risks implying a disputed or oversimplified causal answer, and returns to literal association rather than curiosity.

#### C — Conceptual Surrealism — WINNER
**Metaphor:** one impossible paper-like disc is half daylight and half night; the single disc is physically segmented into equal radial wedges, as if a whole day were a familiar object deliberately cut into units, with no clock hands and no sundial.  
**Hero:** one day/night disc.  
**Why it works:** it asks “why was one day cut this way?” without giving the historical answer, avoids the sundial association, has a clean mobile silhouette, and can animate through segmentation. Exact segment count can be enforced in vector post rather than trusted to a generative model.  
**Red Team:** PASS — clearest curiosity gap and most memorable non-literal metaphor.

**Council selection:** C only.

---

## 2. Selection summary

Only three concepts are authorized for execution in this pilot:

| Episode | Selected language | Selected concept | Red Team state |
|---|---|---|---|
| كيف وُلدت بغداد؟ | Object Macro | Compass line turns into urban-plan texture | APPROVED FOR BRIEF |
| كيف تعمل البنوك؟ | Object Macro | Clean transparent value-routing mechanism | APPROVED FOR BRIEF |
| من قرر أن اليوم 24 ساعة؟ | Conceptual Surrealism | Day/night disc physically segmented into units | APPROVED FOR BRIEF |

The rejected and reserve concepts are not execution contracts and must not be sent to a generation tool.

---

# BRIEF 01 — بغداد / Object Macro

## 1. Identification
- Episode: كيف وُلدت بغداد؟
- Asset type: YouTube thumbnail / key reference frame
- Prompt version: BAGHDAD-OM-v1.0
- Date: 2026-10-14
- Target tool/model: OpenAI still-image generation for the base visual; typography added deterministically in design/compositing software
- Previous related thumbnail/frame: earlier hand + compass + detailed-city test described in the identity review

## 2. Editorial intent
- Episode topic: the deliberate founding and planned form of Baghdad
- Viewer question: كيف يمكن لمدينة أن تبدأ كفكرة هندسية قبل أن تصبح مدينة؟
- Click promise: you will see the design logic behind Baghdad’s birth, not merely a pretty reconstruction of the city
- Answer promise: the episode will explain the planning logic and historical context with evidence
- One-sentence visual metaphor: a drafting compass draws a circle, and the drawn line itself begins turning into a minimal city-plan texture
- Why this metaphor is the right one: it turns “a planned city is born from geometry” into one readable action while avoiding monumental historical scenery

## 3. Hero system
- Hero object/figure: precision drafting compass point and one emerging circular line
- Why this hero is episode-specific: the round-plan logic is central to the episode and cannot be reused unchanged for banking or time
- Image language: Object Macro
- Layout family: L2 — Object Macro
- Primary focal point: the exact contact point where compass/graphite meets paper and the line begins transforming
- Secondary focal points allowed: none

## 4. Composition
- Aspect ratio: 16:9, composed for YouTube thumbnail crop
- Negative-space target: 45–55%
- Hero position: lower-right to center-right, with the transforming arc moving toward center
- Text position: upper-left / left-center negative space
- Camera/crop: extreme close-up, top-down with a slight 10–15° oblique tilt; no visible hand
- Perspective: shallow physical perspective on compass + paper, otherwise graphic and controlled
- Foreground/background relationship: hero sharply defined against a clean paper field
- Elements crossing frame boundaries: one compass leg may crop out at the lower-right edge
- Mobile-size silhouette test: at phone size the viewer must still read “compass + circle being drawn” before seeing any micro-detail

## 5. Color + light
- Brand anchor colors: Paper Ivory + Ink Charcoal; cobalt allowed only as a tiny editorial registration accent, not the dominant field
- Episode accent color: oxidized green / muted copper
- Dominant field color: warm paper ivory
- Lighting direction: soft directional studio light from upper-left
- Contrast: high around the compass point and line; restrained elsewhere
- Shadow behavior: one crisp but soft-edged contact shadow; no cinematic haze
- Saturation limits: mostly restrained; accent limited to small areas

## 6. Surface + texture
- Background: clean premium paper field
- Material: matte paper + real metal drafting compass
- Texture: subtle paper grain
- Print/halftone/grain treatment: very light halftone only where the line transitions into plan texture
- Historical/archival treatment if relevant: none; this is an explanatory editorial illustration, not archival evidence

## 7. Typography
- Arabic display direction: refined bold editorial Arabic, compact and calm
- Supporting type: none on thumbnail unless later required
- Maximum word count: 4 words
- Relative size: headline large enough to dominate negative space without overpowering the hero
- Placement: upper-left / left-center
- Text hierarchy: single headline block only
- No text rendered by image model unless explicitly approved: YES — leave clean space; add Arabic text after generation

## 8. Allowed elements
- Allowed: precision compass, graphite/ink circular line, minimal urban-plan texture embedded in the line, subtle registration marks
- Optional: one tiny oxidized-green planning annotation mark
- Evidence-backed required elements: no claim-specific historical object is required inside the generated frame; historical specifics belong in the episode evidence layer

## 9. Forbidden elements
- visible hand or historical sleeve
- ancient city skyline
- mosque dome as generic Baghdad shorthand
- arches, columns, marble, monumental gates
- gold fantasy architecture
- aerial cinematic city render
- dramatic sunset
- parchment distress
- excessive map labels
- generic blueprint UI
- multiple focal objects
- rendered Arabic text from the image model
- visual evidence fabrication

## 10. Differentiation contract
- What must differ from previous thumbnail: remove the hand, remove the robe, remove the detailed city render, reduce object count, change to macro crop, use ivory + oxidized green rather than blue/gold
- Structural devices carried over (maximum 2): circular-plan idea; drafting compass
- New visual devices: line-to-plan transformation; macro contact-point focus
- Episode-specific motifs: circle geometry; graphite-to-plan morph; oxidized planning mark
- Zero-architecture requirement satisfied?: YES
- Why this frame could not be reused for another episode: the hero action is specifically the physical emergence of a round city plan from a drafting circle

## 11. Reference fidelity
- Primary reference: `1000061003.mp4`
- Reference traits intentionally preserved: one hero, bold negative space, clean editorial field, conceptual object/process, restrained print touch
- Reference traits intentionally not copied: classical portrait, curtain, pear, identical cobalt field, exact layouts
- Why this still belongs to the channel: it uses the reference’s design grammar rather than its nouns

## 12. Anti-AI-Slop constraints
- Generic template risks: “ancient Baghdad” fantasy scene; map pasted over city render
- AI-default risks: ornate compass, steampunk instrument, gold filigree, overly cinematic macro
- Over-decoration risks: blueprint labels, decorative borders, multiple map layers
- Literal-association risks: turning the frame into a tourism poster of Baghdad
- How the visual metaphor avoids them: the only story is the act of geometry becoming a plan
- One-second readability test: viewer reads compass + emerging circle instantly
- Beauty-without-meaning test: FAIL the asset if it remains attractive after removing the line-to-plan transformation

## 13. Documentary boundary
- EVIDENCE / EXPLANATION / ATMOSPHERE / TRANSITION: EXPLANATION
- Synthetic realism present?: stylized object realism only
- Could viewer mistake it for archival evidence?: NO, if kept clearly editorial
- Disclosure/label requirement: none for the thumbnail if kept visibly conceptual; do not present it as historical photograph
- Source/rights dependency: none for generated base; factual claims handled elsewhere

## 14. Final generation instruction
Create a premium editorial YouTube-thumbnail base in the Modern Editorial Surrealism style. Use a warm paper-ivory background with roughly half the frame as clean negative space. In an extreme macro view, show a real precision drafting compass touching the paper near the lower-right/center-right. Do not show any hand. The compass is drawing one clean charcoal circular line. At the exact contact point, the newly drawn line begins to transform seamlessly into a minimal, abstract urban-plan texture made from tiny disciplined street/block marks, as though geometry is becoming a city plan while it is being drawn. Keep the transformation concentrated and readable; do not render a full city. Use soft upper-left studio light, a subtle real paper grain, matte metal, and a small oxidized-green or muted-copper editorial accent. Preserve a large uncluttered area on the left for later Arabic typography. The visual must feel intelligent, calm, designed, slightly strange, and immediately legible on a phone. No architecture, no skyline, no historical costume, no cinematic ancient-city atmosphere, no generated text.

## 15. Negative constraints
Reject any output containing a visible hand, sleeve, mosque skyline, city panorama, arches, columns, marble, gold ornament, ancient ruins, blue/gold default palette, steampunk detailing, fantasy haze, dramatic sunset, multiple hero objects, excessive blueprint graphics, illegible micro-city detail, or image-model-generated Arabic text. Reject if the circle/plan transformation is not the dominant idea.

## 16. Approval
- Visual Art Director: APPROVE
- Thumbnail & Packaging Designer: APPROVE
- Synthesis: APPROVE
- Red Team / Anti-Slop: APPROVED_BY_ANTI_SLOP
- Approval notes: strongest Baghdad hypothesis; preserves the earlier successful idea while removing the repeated hand/robe and pretty-city failure modes
- Material deviations permitted: NONE unless returned to Council

## 17. Execution receipt
- Prompt version executed: NOT_EXECUTED
- Tool/model: NOT_EXECUTED
- Generation ID/job ID: NOT_EXECUTED
- Any deviation: none
- If deviation exists, returned to Council?: n/a
- Output artifact: NOT_EXECUTED

---

# BRIEF 02 — البنوك / Object Macro

## 1. Identification
- Episode: كيف تعمل البنوك؟
- Asset type: YouTube thumbnail / key reference frame
- Prompt version: BANKS-OM-v1.0
- Date: 2026-10-14
- Target tool/model: OpenAI still-image generation for the base visual; typography added deterministically after generation
- Previous related thumbnail/frame: earlier mechanism test that drifted toward steampunk + house/key mortgage symbolism

## 2. Editorial intent
- Episode topic: what a bank actually does with deposits, credit, payments, and balance-sheet flows
- Viewer question: ماذا يحدث فعليًا للقيمة عندما تضع أموالك في بنك؟
- Click promise: see banking as a visible flow rather than a vault or building
- Answer promise: the episode will distinguish deposits, reserves, lending/credit, and payment functions without pretending the thumbnail is a literal bank diagram
- One-sentence visual metaphor: one value token enters a transparent routing mechanism where a visible portion pauses while the remaining flow is redirected into broader credit/payment paths
- Why this metaphor is the right one: it communicates routing/intermediation and controlled allocation without collapsing “banking” into a mortgage, vault, or pile of cash

## 3. Hero system
- Hero object/figure: a clean transparent acrylic routing mechanism with one brass value token entering it
- Why this hero is episode-specific: it visualizes banking as controlled routing of value through a balance-sheet system
- Image language: Object Macro
- Layout family: L2 — Object Macro
- Primary focal point: the branching junction inside the transparent mechanism
- Secondary focal points allowed: only the single entering token and simple output paths; no secondary object hero

## 4. Composition
- Aspect ratio: 16:9
- Negative-space target: 40–50%
- Hero position: center-left, flowing diagonally toward center
- Text position: right-side negative space
- Camera/crop: close studio macro, 3/4 top view, cropped so the mechanism fills about half the frame
- Perspective: clean product-photography perspective, not industrial/cinematic
- Foreground/background relationship: transparent mechanism sharply separated from a flat muted-green/ivory field
- Elements crossing frame boundaries: input channel may enter from left frame edge
- Mobile-size silhouette test: viewer must read “one token enters a clear mechanism and gets routed” without needing small labels

## 5. Color + light
- Brand anchor colors: Ink Charcoal + Paper Ivory
- Episode accent color: muted banknote green with restrained brass/copper
- Dominant field color: muted banknote green or pale desaturated green
- Lighting direction: soft side/top light from upper-left
- Contrast: crisp edges on acrylic + token; simple background
- Shadow behavior: clean studio contact shadow only
- Saturation limits: no neon; brass subdued rather than luxury gold

## 6. Surface + texture
- Background: flat editorial color field with optional paper grain
- Material: transparent acrylic/glass, matte metal, one brass token
- Texture: clean real surfaces; no grime, gears, pipes, or ornate machine texture
- Print/halftone/grain treatment: minimal, optional micro-halftone around one path only
- Historical/archival treatment if relevant: none

## 7. Typography
- Arabic display direction: modern editorial Arabic, strong compact block
- Supporting type: none
- Maximum word count: 3–4 words
- Relative size: large enough for mobile but subordinate to the mechanism
- Placement: right-side negative space
- Text hierarchy: one headline only
- No text rendered by image model unless explicitly approved: YES

## 8. Allowed elements
- Allowed: one token, transparent branching channel, small clear holding chamber, two or three simple abstract output paths, subtle flow cues
- Optional: one small neutral paper slip/token shape suggesting credit or account claim, without readable text
- Evidence-backed required elements: none; the thumbnail is explanatory metaphor, not a literal accounting diagram

## 9. Forbidden elements
- bank building or façade
- vault door
- house
- key
- mortgage-specific symbols
- stack of cash
- raining coins
- piggy bank
- handshake
- steampunk gears/pipes
- brass ornament
- cinematic smoke
- neon fintech UI
- blockchain imagery
- excessive arrows or labels
- multiple hero objects
- generated Arabic text
- visual evidence fabrication

## 10. Differentiation contract
- What must differ from previous thumbnail: remove house and key, remove steampunk machine language, simplify to transparent acrylic routing, switch to green/ivory, move text to the opposite side, reduce outputs
- Structural devices carried over (maximum 2): “value enters a mechanism”; visible transformation/routing
- New visual devices: transparent clean channels; reserve-like pause chamber; abstract credit/payment exits
- Episode-specific motifs: routing junction; pause chamber; value-token flow
- Zero-architecture requirement satisfied?: YES
- Why this frame could not be reused for another episode: the controlled branching and reserve-like pause are deliberately about the intermediary functions of a bank

## 11. Reference fidelity
- Primary reference: `1000061003.mp4`
- Reference traits intentionally preserved: one object/process, bold empty field, editorial clarity, clean object photography, restrained color
- Reference traits intentionally not copied: cobalt dominance, classical figure, curtain, botanical imagery
- Why this still belongs to the channel: the channel signature is conceptual staging + negative space, not repeated historical decoration

## 12. Anti-AI-Slop constraints
- Generic template risks: “bank = vault + cash”; fintech dashboard
- AI-default risks: steampunk machine, many gears, glowing tubes, gold luxury
- Over-decoration risks: too many channels, arrows, coins, labels
- Literal-association risks: house/key implying mortgage only
- How the visual metaphor avoids them: the viewer watches one input being visibly routed through a simple controlled system
- One-second readability test: one token + transparent split must read instantly
- Beauty-without-meaning test: FAIL if the mechanism looks premium but the routing action is unclear

## 13. Documentary boundary
- EVIDENCE / EXPLANATION / ATMOSPHERE / TRANSITION: EXPLANATION
- Synthetic realism present?: object-level conceptual realism
- Could viewer mistake it for archival evidence?: NO
- Disclosure/label requirement: no archival claim; treat as editorial illustration
- Source/rights dependency: none for generated base

## 14. Final generation instruction
Create a premium editorial thumbnail base about how banks work, using Modern Editorial Surrealism. Use a simple muted banknote-green or pale desaturated-green field with about 45% clean negative space on the right for later Arabic typography. On the center-left, show one elegant transparent acrylic routing mechanism in close studio macro view. A single subdued brass value token enters from the left through one clear channel. At one central junction, a small visible portion pauses in a simple transparent holding chamber while the main flow continues into two clean abstract output paths that suggest credit and payment circulation without using text, a house, a key, or a bank building. The mechanism should look like contemporary museum/product design, not a machine from the 19th century: no visible gears, no pipes, no ornament. Use soft upper-left studio light, crisp acrylic edges, restrained charcoal details, and subtle paper grain in the background. Make the branching action obvious at phone size. Keep the image calm, intelligent, and concept-first. No generated text.

## 15. Negative constraints
Reject vaults, bank façades, houses, keys, mortgage imagery, piggy banks, cash stacks, raining coins, handshakes, gold-luxury styling, gears, pipes, steampunk, cyberpunk/neon fintech interfaces, blockchain symbols, excessive arrows, labels, multiple coins, dramatic haze, extra focal points, or generated Arabic text. Reject if the mechanism feels decorative rather than explanatory.

## 16. Approval
- Visual Art Director: APPROVE
- Thumbnail & Packaging Designer: APPROVE
- Synthesis: APPROVE
- Red Team / Anti-Slop: APPROVED_BY_ANTI_SLOP
- Approval notes: retains the useful “mechanism” metaphor but removes the earlier steampunk and mortgage narrowing
- Material deviations permitted: NONE unless returned to Council

## 17. Execution receipt
- Prompt version executed: NOT_EXECUTED
- Tool/model: NOT_EXECUTED
- Generation ID/job ID: NOT_EXECUTED
- Any deviation: none
- If deviation exists, returned to Council?: n/a
- Output artifact: NOT_EXECUTED

---

# BRIEF 03 — 24 ساعة / Conceptual Surrealism

## 1. Identification
- Episode: من قرر أن اليوم 24 ساعة؟
- Asset type: YouTube thumbnail / key reference frame
- Prompt version: DAY24-CS-v1.0
- Date: 2026-10-14
- Target tool/model: OpenAI still-image generation for the base object + deterministic vector/compositing pass if an exact 24-segment count is visible
- Previous related thumbnail/frame: earlier sundial concept with “24” duplicated in text/shadow

## 2. Editorial intent
- Episode topic: why a day is conventionally divided into 24 hours and how that convention emerged
- Viewer question: لماذا قُسّم اليوم إلى هذا العدد من الوحدات تحديدًا؟
- Click promise: the thumbnail creates the mystery of “a whole day deliberately cut into units” without revealing the historical answer
- Answer promise: the episode will explain the historical development and uncertainties accurately
- One-sentence visual metaphor: one impossible day/night disc is physically divided into equal radial wedges as if the day itself were a familiar object being cut into units
- Why this metaphor is the right one: it makes the choice of division—not the clock itself—the visual question, avoiding the obvious sundial association

## 3. Hero system
- Hero object/figure: one circular paper-like disc, half daylight and half night
- Why this hero is episode-specific: it literally represents one complete day being divided, not a generic clock
- Image language: Conceptual Surrealism
- Layout family: L4 — Surreal Stage
- Primary focal point: the radial segmentation boundary on the day/night disc
- Secondary focal points allowed: none

## 4. Composition
- Aspect ratio: 16:9
- Negative-space target: 45–55%
- Hero position: center-right, slightly cropped by the right frame edge
- Text position: left-side negative space
- Camera/crop: clean front-facing editorial object view with slight depth; medium close crop
- Perspective: near-orthographic with subtle real-object thickness
- Foreground/background relationship: disc floats slightly above a flat editorial field with one soft shadow
- Elements crossing frame boundaries: outer edge of disc may crop at far right
- Mobile-size silhouette test: viewer must instantly read “one day/night circle split into pieces,” with no need to count wedges

## 5. Color + light
- Brand anchor colors: Paper Ivory + Ink Charcoal
- Episode accent color: deep plum / mineral red
- Dominant field color: warm ivory or very pale neutral
- Lighting direction: soft light from upper-left
- Contrast: bright daylight half vs deep night half, both controlled
- Shadow behavior: a single clean editorial shadow; no cosmic glow
- Saturation limits: night is deep blue-charcoal rather than neon; accent plum/mineral red appears only in cut edges or small editorial mark

## 6. Surface + texture
- Background: clean paper/ivory field
- Material: thick paper/card disc with tactile cut edges
- Texture: subtle paper grain; night half may contain sparse controlled stars, daylight half a soft warm field
- Print/halftone/grain treatment: slight print texture on the two halves
- Historical/archival treatment if relevant: none in the thumbnail; historical evidence belongs inside the episode

## 7. Typography
- Arabic display direction: refined editorial Arabic
- Supporting type: optional small question mark or punctuation added after generation
- Maximum word count: 4 words
- Relative size: large compact headline in left negative space
- Placement: left-center
- Text hierarchy: one block only
- No text rendered by image model unless explicitly approved: YES

## 8. Allowed elements
- Allowed: one day/night disc, equal radial cut/segment logic, tactile paper edges, subtle shadow, sparse star field
- Optional: one tiny editorial registration line in plum/mineral red
- Evidence-backed required elements: none; exact historical causation is intentionally not depicted
- Exact-count handling: if all 24 divisions are visibly exposed, Technical Operator must enforce exactly 24 with vector geometry in deterministic post; do not trust the generative model to count

## 9. Forbidden elements
- sundial
- clock hands
- wall clock face
- giant Arabic or Latin “24” inside the generated image
- “24” repeated in shadows
- hourglass
- ancient Egyptian figure
- pyramid
- history collage
- ornate astronomy instrument
- cosmic fantasy
- neon galaxy
- futuristic HUD
- multiple suns/moons
- explanatory labels
- generated text
- visual evidence fabrication

## 10. Differentiation contract
- What must differ from previous thumbnail: remove sundial, remove explicit “24” visual answer, remove historical artifact association, switch to a single surreal object and stronger negative space
- Structural devices carried over (maximum 2): circular form; topic of division
- New visual devices: day/night material split; physical radial segmentation; tactile paper-object surrealism
- Episode-specific motifs: daylight/night dual surface; radial cut edges; one complete-day object
- Zero-architecture requirement satisfied?: YES
- Why this frame could not be reused for another episode: the central impossible object is literally “one full day” being partitioned

## 11. Reference fidelity
- Primary reference: `1000061003.mp4`
- Reference traits intentionally preserved: clean editorial field, single conceptual object, bold negative space, controlled surrealism, premium tactile surface
- Reference traits intentionally not copied: pear, classical portrait, curtain, blue full-field layout
- Why this still belongs to the channel: the concept follows the reference’s “ordinary object made conceptually strange” logic

## 12. Anti-AI-Slop constraints
- Generic template risks: clock face, sundial, hourglass, zodiac
- AI-default risks: cosmic glow, ornate astronomy, over-detailed sky, impossible extra moons
- Over-decoration risks: too many stars, labels, historical props
- Literal-association risks: displaying the answer “24” instead of creating the question
- How the visual metaphor avoids them: it visualizes the act of partitioning a day without naming who/why
- One-second readability test: one circle, half day/half night, visibly segmented
- Beauty-without-meaning test: FAIL if the frame could be read merely as a decorative moon/sun poster

## 13. Documentary boundary
- EVIDENCE / EXPLANATION / ATMOSPHERE / TRANSITION: EXPLANATION
- Synthetic realism present?: clearly surreal editorial object
- Could viewer mistake it for archival evidence?: NO
- Disclosure/label requirement: none if kept obviously conceptual
- Source/rights dependency: none for generated base; historical sources belong in episode research

## 14. Final generation instruction
Create a premium Modern Editorial Surrealism thumbnail base for an Arabic documentary episode asking why a day has 24 hours. Use a warm paper-ivory background with roughly half the frame left as clean negative space for later Arabic typography. Place one hero object at center-right: a thick circular paper/card disc representing one complete day. The disc is physically impossible but immediately understandable: one half carries soft daylight warmth and the other half carries a deep controlled night surface with only a few subtle stars. Across the single disc, clean radial cut lines divide the whole object into equal wedge-like units, as if the day itself has been deliberately partitioned. Do not use clock hands, a clock face, a sundial, an hourglass, historical figures, or the numeral 24. Give the disc slight tactile thickness and one soft upper-left studio shadow. Use paper texture, restrained charcoal, and a small deep-plum or mineral-red accent at the cut edges. The image must be calm, graphic, curious, slightly surreal, and instantly legible on a phone. Do not render any text. If the final production version visibly exposes every segment, exact 24-count geometry must be added later with deterministic vector construction rather than left to the image model.

## 15. Negative constraints
Reject any sundial, clock hands, clock numerals, explicit “24,” hourglass, pyramid, Egyptian figure, star-chart collage, ornate astrolabe, cosmic fantasy, neon galaxy, futuristic interface, multiple celestial bodies, excessive stars, generated labels, decorative-but-meaningless circle, or generated Arabic text. Reject if the scene gives the historical answer instead of creating the question “why was the day divided this way?”

## 16. Approval
- Visual Art Director: APPROVE
- Thumbnail & Packaging Designer: APPROVE
- Synthesis: APPROVE
- Red Team / Anti-Slop: APPROVED_BY_ANTI_SLOP
- Approval notes: strongest replacement for the rejected sundial; it creates the “why this division?” curiosity gap without presenting a false historical answer
- Material deviations permitted: NONE unless returned to Council

## 17. Execution receipt
- Prompt version executed: NOT_EXECUTED
- Tool/model: NOT_EXECUTED
- Generation ID/job ID: NOT_EXECUTED
- Any deviation: none
- If deviation exists, returned to Council?: n/a
- Output artifact: NOT_EXECUTED

---

## 3. Technical Operator handoff

The three approved prompt versions are:
- `BAGHDAD-OM-v1.0`
- `BANKS-OM-v1.0`
- `DAY24-CS-v1.0`

All three have `APPROVED_BY_ANTI_SLOP`.

Execution is now permitted by the visual-generation gate, but **no execution has occurred in this artifact**. The Technical Operator must execute the exact approved brief, record the tool/model and generation/job ID, and return any material deviation to the Council rather than improvising.

After generation, the Council must compare each output against the exact prompt version and complete the execution receipt before the asset can be treated as an approved reference frame.
