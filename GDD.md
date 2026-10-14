# Falling (Into the Darkness) — Game Design Document

> **Logline:** A 3:32 AM existential tech physics puzzler. You are Leo Vance, an infrastructure engineer whose life is collapsing in real time on the phone screen behind the game — and your only escape is fusing processor chip blocks down into 100% pure black.
> **Status:** Current (Updated October 2026) — Mechanics spec'd, Silicon Architecture & Motherboard Theme finalized, 6-Beat Storyboard documented, web prototypes live.
> **Genre:** Physics puzzle / block-fusion
> **Engine & Target:** Godot 4 (PC/Steam, Mobile, Web)
> **Source materials:** `README.md`, `docs/wireframe_design_system.md`, web prototypes, Lunacy wireframes.

---

## 1. High Concept & Hook

**The hook:** Every puzzle game is an escape. *Falling* makes the thing you're escaping from visible the entire time — your phone, face-down on the desk behind the translucent motherboard plate, lighting up with Slack credential revocations, your wife's worried texts, and an empty bank account — while you chase the only peace on offer: total darkness.

**Core fantasy:** Total light absorption. Every merge drinks color out of the world until nothing is left but black.

**Target audience:** Puzzle-game players who loved *Tetris Effect*'s mood, *Suika* fusion satisfaction, and narrative framing with teeth. Mobile-first, 3-minute sessions.

---

## 2. Design Pillars

1. **Darkness is the score.** Progress is measured in light absorbed, not points stacked. The win state is a color (`#000000`), not an arbitrary number.
2. **The background is the story.** Leo's collapse unfolds entirely through the phone layer beneath the motherboard — no cutscenes, no dialogue boxes. The game never interrupts the puzzle to tell story.
3. **Fusion feels physical.** Blocks are rigid computer processor packages with mass and metallic sheen. Merges land with weight; the Titan is a massive enterprise socket presence, not a sprite.
4. **Calm surface, dread underneath.** The puzzle loop is meditative; the context is a panic attack at 3:32 AM. The tension between them *is* the game.

---

## 3. Core Gameplay Loop

```
[SMT Pick-and-Place Gantry aligns] → [Steer / position silver processor chip]
  → [Chip drops with gravity, settles among stack on motherboard]
  → [Two same-tier chips touch → FUSE into next tier package, CMY pigments combine]
  → [Board darkens toward #000000 → Darkness Purity % rises]
  → [Repeat — chase 100% Darkness Purity]
```

- **Session shape:** Endless until buffer overflow. One run = one night.
- **Win condition:** Reach **100% Darkness Purity** (all settled ink at $C=M=Y=\max$, culminating in the Tier 11 Titan).
- **Lose condition:** Stack breaches the high-voltage danger line (`// VBUS_OVERVOLTAGE_LIMIT //`) for more than 3 seconds $\rightarrow$ overvoltage shutdown $\rightarrow$ run ends.

---

## 4. Mechanics & Systems

### 4.1 The Chamber & Motherboard Playfield
- Grid: **$24 \times 36$ cells**, constant 1:1.5 aspect ratio.
  - Mobile ($390 \times 844\text{px}$ viewport): $14\text{px}$ unit $\rightarrow$ $336 \times 560\text{px}$ chamber.
  - Desktop Steam ($1440 \times 900\text{px}$ viewport): $20\text{px}$ unit $\rightarrow$ $480 \times 720\text{px}$ chamber.
- Top: SMT robotic vacuum placement gantry with collimated optical crosshair laser guide.
- Floor: Gold-plated LGA CPU socket contact bed with spring retention fingers.
- Danger line: High-voltage red hazard bus line (`// VBUS_OVERVOLTAGE_LIMIT //`) at row 6.
- Bottom: SMT tactile illuminated **SWAP** switch (toggles Game $\leftrightarrow$ Phone focus).

### 4.2 Block Tiers: Silicon Processor Packaging Hierarchy
Strictly square $N \times N$ rigid monoliths. Each block is authored with an **authentic brushed silver / metallic heat spreader backdrop** and an **inset square solid-color die** with a mathematically centered tier numeral:

| Tier | Size | Units | In-Game Pixels | Physical Package Architecture | Ink Color |
|:---:|:---:|:---:|:---:|:---|:---|
| **1** | $1\times 1$ | 1 | $14\text{px}$ | SOT-23 Micro-Chip Mote | Pure Yellow (`#FACC15`) |
| **2** | $2\times 2$ | 2 | $28\text{px}$ | QFN Surface-Mount Package | Pure Magenta (`#EC4899`) |
| **3** | $3\times 3$ | 3 | $42\text{px}$ | Small-Outline IC (SOIC) | Pure Cyan (`#06B6D4`) |
| **4** | $4\times 4$ | 4 | $56\text{px}$ | Dual-Core BGA Package | Cobalt (`#2563EB`) |
| **5** | $5\times 5$ | 5 | $70\text{px}$ | Quad-Core Ceramic IC | Amethyst (`#7C3AED`) |
| **6** | $6\times 6$ | 6 | $84\text{px}$ | Multi-Die Heterogeneous SoC | Ruby (`#BE123C`) |
| **7** | $7\times 7$ | 7 | $80\text{px}$ | Brushed Nickel Server CPU (IHS) | Magenta Core (`#EC2882`) |
| **8** | $8\times 8$ | 8 | $90\text{px}$ | Workstation Processor Package | Amber (`#B45309`) |
| **9** | $9\times 9$ | 9 | $100\text{px}$ | MCM Neural Accelerator | Slate (`#334155`) |
| **10** | $10\times 10$ | 10 | $110\text{px}$ | Multi-Socket High-Compute Module | Midnight Basalt (`#0F172A`) |
| **11** | $11\times 11$ | 11 | **$154\text{px}$** | **Obsidian Titan Enterprise Monolith** | **Pure Black (`#000000`)** |

- **Mass & Gravity:** Downward gravity $g = 980\text{px/s}^2$. Blocks have mass proportional to area ($N^2$); they tumble, collide, and seat into the socket bed.
- **Spawns:** Tiers 1–3 only (pure primary pigments). Higher tiers arise exclusively through fusion.
- **Titan Scale Parity:** Exactly $154 \times 154\text{px}$, occupying **45.8% of the total chamber width**.

### 4.3 Subtractive CMY Ink Synthesis
Unlike additive RGB (which mixes to white), *Falling* uses **subtractive CMY** like physical printing ink: combining pigments absorbs light.

- **Fusion rule:** Two touching blocks of the **same tier** fuse into one block of the **next tier**.
- **Ink synthesis rule:**
  $$C_{\text{child}} = \min(1.0, C_1 + C_2), \quad M_{\text{child}} = \min(1.0, M_1 + M_2), \quad Y_{\text{child}} = \min(1.0, Y_1 + Y_2)$$
- **RGB Output Mapping:**
  $$R = 1 - C, \quad G = 1 - M, \quad B = 1 - Y$$
- **Primary Spawns:**
  - Pure Cyan $(1,0,0) \rightarrow \text{RGB}(0, 240, 255)$
  - Pure Magenta $(0,1,0) \rightarrow \text{RGB}(255, 0, 127)$
  - Pure Yellow $(0,0,1) \rightarrow \text{RGB}(255, 215, 0)$
- **Tier 11 Apex:** $C=M=Y=\max \rightarrow \text{RGB}(0,0,0)$ pure obsidian black. Fusing into the Titan is the moment the board achieves total light absorption.

### 4.4 Darkness Purity (Score Metric)
- $\text{Purity \%} = 100 \times \text{average CMY absorption across all settled blocks}$.
- Displayed in the BIOS hardware telemetry HUD (`SILICON_PURITY: 98.4%`).
- Reaching $100\%$ triggers victory: the entire screen goes black.

---

## 5. Storyboard & Narrative Progression (6 Beats)

The narrative is never told through cutscenes. It lives on Leo Vance's phone behind the motherboard.

![Falling 6-Beat Storyboard](/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272/falling_storyboard_6_panels.png)

### Beat 1: The Frozen Night (03:32 AM, 14% Battery)
- **Scene:** Pitch-black bedroom. Leo sits at his desk illuminated only by the faint OLED glow of his iPhone. The clock is frozen at `3:32 AM`. Battery is at `14%`.
- **Gameplay Action:** The game boots into the BIOS initialization screen.
- **Audio:** Low ambient mains hum (60 Hz room tone). Faint muffled breathing.

### Beat 2: Motherboard Boots & First Chip Drop
- **Scene:** The chamber powers up as a high-end computer motherboard. An SMT robotic vacuum head slides across the top gantry rail with a collimated cyan crosshair laser.
- **Gameplay Action:** The first silver processor chip (Tier 1 Yellow Mote) is aimed and dropped with gravity, landing firmly onto the gold LGA socket pins.
- **Audio:** Mechanical stepper motor whine, vacuum release hiss, tactile metal-on-pin click.

### Beat 3: The Bleed (The Real World Breaks In)
- **Scene:** As blocks stack, the first alert arrives on Leo's phone behind the semi-translucent motherboard:
  > **SLACK • IT Security (3:28 AM):** "Apex Tech Security: Enterprise credentials revoked for user l_vance. VPN Session Terminated: Code 403."
- **Gameplay Action:** The notification card illuminates through the solder mask. Merges continue; ink absorption rises to ~35%.
- **Audio:** Muffled iOS tri-tone notification ping leaking through the board.

### Beat 4: The SWAP (Unfiltered Reality)
- **Scene:** Player clicks/taps the tactile **SWAP** switch. The motherboard cross-fades out; Leo's phone screen comes into sharp focus, exposing the full collapse:
  > **MESSAGES • Sarah (3:30 AM):** "Leo, please come to bed... You haven't slept in two days."
  > **CHASE • Account Alert (3:15 AM):** "COBRA deduction: -$1,842.00. Account balance: $314.12."
  > **CALENDAR (9:00 AM Today):** "Mandatory HR Exit Interview (Portal) — In 5h 28m."
- **Gameplay Action:** Player reads the crisis. *Neglect cost:* In the background, the chip dropper continues to simulate — hesitation risks overflow!
- **Audio:** Phone haptic buzz, muffled hum of the simulated dropper above.

### Beat 5: Buffer Overflow (Critical Density)
- **Scene:** The chip stack rises near the red high-voltage danger limit line (`// VBUS_OVERVOLTAGE_LIMIT //`). The motherboard voltage telemetry spikes (`VCC_CORE: 1.45V OVERVOLT`).
- **Gameplay Action:** The red line strobes. The player has 3 seconds to clear or fuse blocks before overvoltage triggers a kernel panic / run failure.
- **Audio:** High-pitched capacitor coil whine, rapid rhythmic warning pulse.

### Beat 6: 100% Darkness (The Titan Monolith Apex)
- **Scene:** The player executes the final merge. Two Tier 10 processors combine to form the massive **Tier 11 Obsidian Titan Monolith** ($154\text{px}$, pure `#000000`).
- **Gameplay Action:** Total light absorption is achieved. Darkness Purity hits `100.0%`. A gravitational singularity consumes all remaining light. The phone screen turns completely off. All notifications vanish.
- **Audio:** Deep sub-bass implosion bloom, followed by complete, total silence. Leo's night is finally at peace.

---

## 6. Art Direction & Visual Hierarchy

### 3-Layer Visual Architecture
1. **Layer 1: Phone Screen (Base):**
   - iPhone lockscreen, OLED black wallpaper, `3:32` clock, `14% 🪫` battery, Dynamic Island.
   - 4 native iOS notification cards (Slack, Sarah, Chase, Calendar).
2. **Layer 2: Photorealistic Motherboard Chamber (Filter):**
   - High-end computer motherboard plate ($336 \times 560\text{px}$):
     - Black anodized aluminum VRM heatsinks.
     - Dual DDR5 memory channels flanking the playfield.
     - Steel-reinforced PCIe card-edge slot.
     - Solid polymer cylindrical capacitors and serpentine copper bus trace meanders.
   - Solder mask is tuned to ~80% opacity so phone notification text leaks through the dark FR4 substrate like backlighting.
3. **Layer 3: Playfield Overlay (Foreground):**
   - Anti-aliased $24 \times 36$ coordinate grid ($14\text{px}$ unit scale).
   - SMT pick-and-place gantry with precision linear guide rod and crosshair laser.
   - LGA spring-loaded gold contact pins on floor bed.
   - Silver Metallic Processor Chip Blocks with centered square color dies.
   - SMT tactile illuminated SWAP micro-switch button.
   - Motherboard BIOS hardware telemetry HUD (`BUS_CLK: 4.80 GHz`, `VCC_CORE: 1.248V`, `SILICON_PURITY: 98.4%`).

---

## 7. Controls & Interactivity

| Input Action | Keyboard | Touch / Mobile | Function |
|:---|:---|:---|:---|
| **Steer** | `A` / `D` or `←` / `→` | Drag horizontally | Move SMT dropper gantry along linear rail |
| **Fast Drop** | `S` / `↓` / `Space` | Swipe down / Tap | Fast-drop processor chip into socket bed |
| **SWAP** | `Tab` / `Space` / Click | Tap on-screen button | Cross-fade focus between Motherboard and Phone Screen |

---

## 8. MVP Implementation Checklist

- [x] Consolidate $24 \times 36$ grid parity ($336 \times 560\text{px}$ chamber, $14\text{px}$ unit scale).
- [x] Lock in Titan Monolith mathematical ratio ($154 \times 154\text{px}$, 45.8% width).
- [x] Finalize Silicon Processor Chip architecture (Brushed silver nickel IHS + centered colored die).
- [x] Render photorealistic computer motherboard chamber.
- [x] Design and document 6-Beat Narrative Storyboard.
- [ ] Connect Godot 4 rigid-body physics for falling/colliding chip blocks.
- [ ] Wire subtractive CMY ink fusion shader in Godot 4.
- [ ] Implement scheduled arrival of the 4 phone notifications during gameplay.
- [ ] Implement 3-second buffer overflow fail timer.
- [ ] Wire audio stems (coil whine, relay clicks, sub-bass Titan void).

---

*Last revised: October 2026. Consolidated and updated with the Silicon Processor & Motherboard architecture and 6-Beat Storyboard.*
