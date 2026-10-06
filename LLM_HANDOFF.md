# A.I.r Bubbles — Project Handoff & Continuity Guide

## 1. Executive Summary & Game State
* **Project Location:** `/Users/georgearmah/air-bubble`
* **Engine:** Summer Engine (Godot 4.3+ 2D compatible)
* **Core Genre:** Inverted-Buoyancy Suika Game ("Watermelon Game") physics puzzle.
* **Core Theme:** Satire of the AI startup bubble, LLM hype ("Lake Ellem"), venture capital mania, and synthetic slop.

### Current Gameplay & Mechanics (Complete & Verified Working)
1. **Inverted Buoyancy Physics:**
   * Bubbles are launched from a hydrothermal vent at the seabed floor (`y = 192.0`) and float **rapidly UPWARD** toward the water surface ceiling (`y = -620.0`).
   * Launch speed: `-820.0 px/s`. Buoyant gravity: `-0.92`. Water drag: `1.15`.
   * Fast, responsive steering (`650.0 px/s`) and rapid-fire input (`0.18s` cooldown).
2. **11-Tier Suika Merge System (Numbers 1 through 11):**
   * Two identical touching bubbles merge into the next rank ($N + N \to N + 1$).
   * Merging awards $N+1$ points ($1+1 \to 2$ gives 2 pts, $2+2 \to 3$ gives 3 pts, ... $10+10 \to 11$ gives 11 pts).
   * **Apex Titan (Tier 11):** Tier 11 does **not** pop or merge! When two Tier 11 bubbles collide, they bounce off each other as solid, massive behemoths ($r = 124\text{px}$, diameter $248\text{px}$ in a $400\text{px}$ chamber), heavily constraining remaining chamber space.
3. **Danger & Game Over:**
   * If bubbles stack down past the dashed danger limit (`DANGER_Y = 80.0`) for longer than 3.0 seconds, the vent overflows and triggers **Game Over**.
4. **Lake Ellem (Score Reservoir):**
   * On the right half of the screen, merges shoot golden A.I.r particle streams into the Lake Ellem reservoir, displaying total A.I.r points with pulsing animations.
5. **Procedural Audio & Game Feel (Zero Cloud Spend):**
   * Launch pop + musical scale merge chimes ($C_4$ to $A_5$) synthesized dynamically via GDScript `AudioStreamWAV` without external asset dependencies.
   * Dynamic camera trauma shake, squash/stretch wobble, scale-pop spawn decay, and floating point popups (`+4`, `COMBO x2!`).
6. **In-Game HUD:**
   * 3-row Evolution Guide displaying all 11 tiers ($1 \to 2 \dots \to 11\text{ APEX}$), Next Bubble preview, real-time score, and danger warning countdown.

---

## 2. Key Codebase Files
* [`main.tscn`](file:///Users/georgearmah/air-bubble/main.tscn): Main scene with Camera2D and Root Node2D attached to `res://scripts/game.gd`.
* [`scripts/game.gd`](file:///Users/georgearmah/air-bubble/scripts/game.gd): The complete, self-contained game script (~42 KB) handling physics bodies, launcher input, procedural audio synthesis, visual rendering via `_draw()`, and HUD.
* [`project.godot`](file:///Users/georgearmah/air-bubble/project.godot): Godot project settings, rendering settings (viewport size: 1280x720, mode: canvas_items).

---

## 3. How to Run, Control & Debug the Game
Summer Engine exposes both an MCP tool interface and a CLI via `npx summer-engine`.

> **IMPORTANT (Multi-Instance Port Management):**
> If multiple Summer Engine editors are running on macOS, always prefix commands with `SUMMER_ENGINE_PROJECT="/Users/georgearmah/air-bubble"` so the CLI targets the correct editor instance!

### Essential CLI Commands
```bash
# 1. Open the project in the Summer Engine Editor:
SUMMER_ENGINE_PROJECT="/Users/georgearmah/air-bubble" npx -y summer-engine@latest run /Users/georgearmah/air-bubble

# 2. Start running the game:
SUMMER_ENGINE_PROJECT="/Users/georgearmah/air-bubble" npx -y summer-engine@latest tool summer_play

# 3. Stop the game:
SUMMER_ENGINE_PROJECT="/Users/georgearmah/air-bubble" npx -y summer-engine@latest tool summer_stop

# 4. Check if game is running:
SUMMER_ENGINE_PROJECT="/Users/georgearmah/air-bubble" npx -y summer-engine@latest tool summer_is_running

# 5. Switch Summer editor to the "Game" tab so the user sees the canvas:
SUMMER_ENGINE_PROJECT="/Users/georgearmah/air-bubble" npx -y summer-engine@latest tool summer_ui_activate --args '{"path":"main_screen","action":"select_tab","value":"Game"}'

# 6. Bring the Summer window to the front on macOS:
osascript -e 'tell application "System Events" to set frontmost of (first process whose name contains "Summer") to true'
```

---

## 4. Strict Constraints & Policies
* **Zero-Spend / Free-Tier Policy (No Summer Cloud Credits):**
  * **DO NOT** call paid cloud tools: `summer_generate_3d`, `summer_generate_audio`, `summer_generate_video`, `summer_generate_motion`.
  * Audio is generated procedurally in GDScript (`AudioStreamWAV`).
  * Visuals are drawn procedurally in GDScript (`_draw()`, `draw_circle`, `draw_polyline`, `ShaderMaterial`).
* **Math Simplicity:**
  * Points on merge must always equal the resulting bubble rank ($N+N \to N+1$ gives $N+1$ points).

---

## 5. Researched 11-Tier Thematic Sets (Ready for Narrative Integration)
The user requested concrete nouns with high satirical value. Choose from or combine these:

### Set 1: "The Compute Arms Race" (Hardware & Scale Infrastructure)
1. **Unchecked Token** — Microscopic word fragment.
2. **Context Window** — Fragile 4k buffer that forgets system prompt.
3. **Colab Notebook** — Free GPU instance that disconnects overnight.
4. **H100 Tensor GPU** — $35k gold silicon slab.
5. **Liquid-Cooled Server Rack** — Monolith drinking water.
6. **Diesel Backup Generator** — Spun up when grid fails.
7. **Dark Fiber Cable** — Transoceanic glass line.
8. **Small Modular Reactor (SMR)** — Leased nuclear fission unit.
9. **Hyperscale Data Center** — Consumes Idaho's electric output.
10. **Stargate Supercluster** — Constellation of 1M nodes.
11. **Dyson Swarm (Lake Ellem Core)** — Encasing a star for next-token prediction.

### Set 2: "The Venture Capital Grift" (The Paper & Valuation Trail)
1. **Napkin Scribble** | 2. **.ai Domain Name** | 3. **Pitch Deck** | 4. **Patagonia Fleece Vest** | 5. **SAFE Note** | 6. **Term Sheet** | 7. **Series A Wire** | 8. **Valuation Cap** | 9. **Paper Unicorn** | 10. **S-1 IPO Prospectus** | 11. **Exit Liquidity (Golden Parachute)**

---

## 6. Next Steps & Roadmap Requested by User
1. **Levels & Chamber Progression:**
   * Multiple stages with differing chamber widths, currents, buoyancy modifiers, or point milestones.
2. **Story & Narrative Arc:**
   * Satirical startup dialogue, stage transitions, Lake Ellem lore cards.
3. **Purposeful Bubble Bursting:**
   * Mechanics that allow popping bubbles strategically (e.g. "Short Seller" needle item, market correction shockwaves, or risk/reward popping to avoid overflow).
