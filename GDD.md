# Falling (Into the Darkness) — Game Design Document

> **Logline:** A 3:32 AM existential physics puzzler. You are Leo Vance, a tech worker whose life is collapsing in real time on the phone screen behind the game — and your only escape is fusing colored monoliths down into 100% pure black.
> **Status:** Design consolidation (Oct 2026) — mechanics spec'd, wireframes + 5 art themes done, web prototypes exist.
> **Genre:** Physics puzzle / block-fusion
> **Engine & Target:** Godot 4 (PC/Steam, Mobile, Web)
> **Source materials:** `README.md`, `docs/wireframe_design_system.md`, `.summer/specs/into-the-darkness-design.md`, web prototypes, Lunacy wireframes.

---

## 1. High Concept & Hook

**The hook:** Every puzzle game is an escape. *Falling* makes the thing you're escaping from visible the entire time — your phone, face-down on the desk behind the frosted glass, lighting up with Slack revocations, a wife's worried texts, and a bank balance in freefall — while you chase the only peace on offer: total darkness.

**Core fantasy:** Total light absorption. Every merge drinks color out of the world until nothing is left but black.

**Target audience:** Puzzle-game players who loved *Tetris Effect*'s mood, *Suika* fusion satisfaction, and narrative framing with teeth. Mobile-first, 3-minute sessions.

---

## 2. Design Pillars

1. **Darkness is the score.** Progress is measured in light absorbed, not points stacked. The win state is a color (#000000), not a number.
2. **The background is the story.** Leo's collapse unfolds entirely through the phone layer — no cutscenes, no dialogue boxes. The game never interrupts the puzzle to tell story.
3. **Fusion feels physical.** Blocks are rigid monoliths with mass. Merges land with weight; the Titan is a presence, not a sprite.
4. **Calm surface, dread underneath.** The puzzle loop is meditative; the context is a panic attack at 3:32 AM. The tension between them *is* the game.

---

## 3. Core Gameplay Loop

```
[Block drops from rail] → [Steer / position while falling]
  → [Block lands, settles among stack]
  → [Two same-tier blocks touch → FUSE into next tier, inks combine]
  → [Board darkens toward #000000 → Darkness Purity % rises]
  → [Repeat — chase 100%]
```

- **Session shape:** endless until overflow. One run = one night.
- **Win condition:** reach **100% Darkness Purity** (all settled ink at C=M=Y=max).
- **Lose condition (proposed):** stack breaches the danger line for more than 3 seconds → the chamber overflows → run ends. *(Proposed — source docs specify a danger line and critical density limit but not the exact fail rule.)*

---

## 4. Mechanics & Systems

### 4.1 The Chamber
- Grid: **24 × 36 cells**, constant 1:1.5 aspect ratio.
  - Mobile (390×844 viewport): 14px unit → 336×560px chamber.
  - Desktop Steam (1440×900): 20px unit → 480×720px chamber.
- Top: dropper slider rail with glowing cube preview + laser guide line.
- Bottom: circular **SWAP** button (toggles Game ↔ Phone focus).
- Danger line: dashed limit above which overflow is counted.

### 4.2 Block Tiers (11)
Strictly square N×N rigid monoliths. No polyominoes.

| Tier | Size | Pixels | Mass feel |
|------|------|--------|-----------|
| 1 | 1×1 | 24 | mote |
| 2 | 2×2 | 38 | pebble |
| 3 | 3×3 | 52 | stone |
| 4 | 4×4 | 68 | brick |
| 5 | 5×5 | 84 | slab |
| 6 | 6×6 | 102 | boulder |
| 7 | 7×7 | 122 | pillar |
| 8 | 8×8 | 144 | column |
| 9 | 9×9 | 168 | monolith |
| 10 | 10×10 | 194 | great monolith |
| 11 | 11×11 | 224 | **Obsidian Titan** — 45.8% of chamber width |

- Physics: downward gravity **g = 980 px/s²**. Blocks are rigid bodies; they tumble, settle, and stack.
- Spawns: tiers 1–3 only (pure inks — see 4.3). Higher tiers arise only from fusion.

### 4.3 Subtractive CMY Ink Synthesis (the core rule)
Unlike RGB (additive — mixing makes white), *Falling* uses **subtractive CMY** like physical ink: combining pigments absorbs light.

- Fusion rule: two touching blocks of the **same tier** fuse into one block of the **next tier**.
- Ink rule: `C_child = C₁ + C₂`, `M_child = M₁ + M₂`, `Y_child = Y₁ + Y₂` (clamped at max).
- Display: `R = 1−C`, `G = 1−M`, `B = 1−Y`.
- Base spawns:
  - Pure Cyan `(1,0,0)` → RGB(0, 240, 255)
  - Pure Magenta `(0,1,0)` → RGB(255, 0, 127)
  - Pure Yellow `(0,0,1)` → RGB(255, 215, 0)
- Secondary mixes: C+M → cobalt/violet · C+Y → emerald · M+Y → crimson.
- **Tier 11 Apex:** C=M=Y=max → **RGB(0,0,0) pure obsidian black**. Fusing *into* the Titan is the moment the board goes dark.

### 4.4 Darkness Purity (score)
- `Purity % = 100 × (average ink absorption across settled blocks)`.
- Each fusion visibly darkens the board. The HUD purity meter is the score — no separate points.
- 100% = every settled block at full C=M=Y. Run complete.

### 4.5 Dual-Screen Interactivity (SWAP)
- The **SWAP** button (or `S` / Space) cross-fades focus between the game chamber and Leo's phone screen.
- Phone layer is live: notifications arrive on a schedule during the run (Slack revocation → wife's texts escalating → Chase alert → HR exit interview at 9:00 AM "today").
- Gameplay effect (proposed): while phone focus is active, the chamber keeps simulating — neglect has a cost. *(Proposed — spec confirms the SWAP transition; the neglect cost is new.)*

### 4.6 Controls
- **Steer:** A/D or ←/→ (or drag) — move falling block horizontally.
- **Drop:** S / ↓ / Space — fast-drop.
- **SWAP:** Tab or on-screen button — toggle Game/Phone focus.
- Touch: drag to steer, tap SWAP.

---

## 5. Narrative (background layer only)

**Leo Vance**, lead infrastructure engineer at Apex Technologies. 3:32 AM. Phone at 14%.

The four notifications (in arrival order):
1. **Slack:** "Apex Tech Security: Enterprise credentials revoked for user l_vance."
2. **Messages (Sarah Vance, wife):** "Leo, please come to bed... You haven't slept in two days."
3. **Chase:** "COBRA health deduction: −$1,842.00. Account balance: $314.12."
4. **Calendar:** "Mandatory HR Exit Interview (Portal) — 9:00 AM Today."

No cutscenes. The trilogy hook (*Book 1 of an existential tech trilogy*) is noted but out of scope for the prototype.

---

## 6. Art Direction

**3-layer visual architecture:**
1. **Phone screen** (base): realistic dark-mode smartphone, 3:32 clock, 14% battery, Dynamic Island, 4 notifications.
2. **Frosted glass** (filter): beveled crystal chamber plate, smoked diffuse body (~35% alpha, ~6px blur) — phone visible but soft beneath the playfield.
3. **Game board** (overlay): 100% transparent background; glowing dropper rail, laser line, beveled numbered blocks, SWAP button.

**Five production art themes** (all preserve 24×36 proportions + Titan ratio):
1. **Cyber Obsidian** — brushed titanium gantry, cyan laser, beveled polymer cubes.
2. **Sumi Ink & Washi** — mulberry paper lantern, glass ink dropper, red enso danger line, gold-leaf inkstone Titan.
3. **Amber CRT** — curved cathode tube, P3 phosphor bloom, vector wireframe blocks, tachometer density gauge.
4. **Nordic Brutalism** — cast concrete pillars, smoked sapphire plate, basalt Titan with diamond-beveled rims.
5. **Optical Neon Gels** — bioluminescent dye-gel blocks, cyan laser, ink-wash background.

**Prototype default:** Cyber Obsidian (most legible for CMY ink reads).

---

## 7. Audio Direction (TBD)
*Not yet specified in source materials.* Proposed: low synth hum that deepens in pitch as purity rises; soft stone-on-stone thuds for landings; a near-sub-bass bloom on Titan fusion; phone notification pings leak through the glass muffled. Full pass needed.

---

## 8. UI / HUD
- **Purity meter:** dominant HUD element — a darkness gradient bar, 0→100%.
- **Next-block preview** on the dropper rail.
- **Density gauge:** tachometer-style readout of stack height vs. danger line.
- **Phone clock** persistent at 3:32 AM (time does not advance — the night is frozen).

---

## 9. Technical Notes
- Engine: Godot 4. Rigid-body physics for blocks; custom `_draw()` or shader for CMY→RGB ink rendering.
- Viewports: 390×844 mobile primary; 1440×900 desktop.
- Web prototypes exist (`web/index.html` physics prototype, mockups) — reuse for feel validation.

---

## 10. MVP Scope (prototype checklist)
- [ ] 24×36 chamber, dropper rail, laser guide, gravity + settle physics
- [ ] Tiers 1–3 spawn (pure C/M/Y), same-tier fusion → next tier with CMY combine
- [ ] Purity meter 0–100%, Titan fusion = visible board-darkening moment
- [ ] Danger line + overflow lose condition
- [ ] Phone base layer with 4 notifications on schedule + SWAP toggle
- [ ] One art theme (Cyber Obsidian)

## 11. Open Questions
1. Exact overflow rule (proposed: 3s above danger line — confirm).
2. Spawn distribution across C/M/Y tiers (equal? weighted?).
3. Does the Titan (11×11) merge further or is it terminal? (Proposed: terminal — it *is* the darkness.)
4. Phone-neglect cost — real mechanic or pure atmosphere?
5. Audio direction (untouched).

---

*Consolidated 2026-10-12 from README.md, docs/wireframe_design_system.md, .summer/specs/into-the-darkness-design.md, and Lunacy wireframes. Proposals are marked "(proposed)".*
*Note: GAME_RULES.md, LLM_HANDOFF.md, FORK_INSTRUCTIONS.md in this folder previously contained A.I.r Bubbles content (stale copy-paste) — quarantined to *.stale-airbubbles.bak.*
