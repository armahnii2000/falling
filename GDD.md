# Falling (Into the Darkness) — Game Design Document

> **Logline:** A 3:32 AM existential tech physics puzzler. You are Leo Vance, an infrastructure engineer whose life is collapsing in real time on the phone screen behind the game — and your only escape is fusing processor chip blocks down into 100% pure black.
> **Status:** Current (Updated October 2026) — Canonical 11-Stage Screenlife Storyboard documented, Dynamic CMY Subtractive Pigment Synthesis specified, Endless Singularity Annihilation supported, Web Prototypes live.
> **Genre:** Physics puzzle / block-fusion / screenlife narrative
> **Engine & Target:** Godot 4 (PC/Steam, Mobile, Web)
> **Source Materials:** `README.md`, `docs/wireframe_design_system.md`, `web/storyboard.html`, `web/phone_story_prototype.html`, Lunacy wireframes.

---

## 1. High Concept & Hook

**The hook:** Every puzzle game is an escape. *Falling* makes the thing you're escaping from visible the entire time — your phone, face-down on the desk behind the translucent motherboard plate, lighting up with Slack credential revocations, your wife's worried texts, and an empty bank account — while you chase the only peace on offer: total darkness.

**Core fantasy:** Total light absorption. Every merge drinks color out of the world until nothing is left but obsidian black.

**Target audience:** Puzzle-game players who loved *Tetris Effect*'s mood, *Suika Game*'s fusion satisfaction, and narrative framing with teeth. Mobile-first portrait orientation, snappy 3-to-5 minute sessions with high replayability.

---

## 2. Design Pillars

1. **Darkness is the score.** Progress is measured in light absorbed, not arbitrary points stacked. The primary milestone is achieving a color: `#000000` (Pure Black).
2. **The background is the story.** Leo's collapse unfolds entirely through the phone layer beneath the motherboard — no cutscenes, no dialogue boxes, no text crawls. The game never interrupts the puzzle to tell story.
3. **Fusion feels physical.** Blocks are rigid computer processor packages with mass, inertia, and metallic sheen. Merges land with weight; the Titan is a massive enterprise socket presence, not a floaty sprite.
4. **Calm surface, dread underneath.** The puzzle loop is meditative and tactile; the context is a panic attack at 3:32 AM. The tension between them *is* the game.
5. **Sacred core, modular skin.** The chamber geometry, subtractive color science, and 11-stage narrative beats are mathematically locked; visual themes, chip spreader styles, and soundscapes are built modularly for easy variation and creative iteration.

---

## 3. Core Gameplay Loop

```
[SMT Pick-and-Place Gantry aligns] 
       ↓
[Steer & position silver processor chip above socket chamber]
       ↓
[Drop chip with gravity → Collides and settles on LGA motherboard bed]
       ↓
[Two same-tier chips touch → FUSE into next tier package, accumulating CMY pigments]
       ↓
[Internal chip die darkens toward #000000 → Motherboard Darkness Purity % rises]
       ↓
[Reach Tier 11 Titan → Merge two Titans → SINGULARITY IMPLOSION (Annihilation & Clear)]
       ↓
[Repeat endlessly — chase peak Darkness Purity and survive buffer overflow]
```

- **Session Shape:** Endless until buffer overflow. One run = one night at the desk.
- **Climax / Win Condition:** Achieve **100% Darkness Purity** by synthesizing the Tier 11 Titan ($C=M=Y \ge T \rightarrow \text{RGB}(0,0,0)$).
- **Endless Mode (Dual Tier 11 Annihilation):** If the player crafts two Tier 11 Titans, colliding them causes a **Singularity Implosion**. Both blocks vaporize in an electromagnetic flash, clearing $308\text{px}$ of board area and awarding massive score so the run can continue indefinitely.
- **Lose Condition:** Stack breaches the high-voltage danger line (`// VBUS_OVERVOLTAGE_LIMIT //`) continuously for more than 3.0 seconds $\rightarrow$ hardware overvoltage shutdown $\rightarrow$ run terminates.
- **SWAP Mechanic (Pause & Inspect):** Pressing the illuminated SWAP switch cross-fades focus to Leo's phone screen. **Opening SWAP strictly pauses the puzzle simulation** (physics, falling chips, and the 3-second buffer overflow timer freeze), allowing the player to safely read narrative texts without penalty.

---

## 4. Mechanics & Systems

### 4.1 The Chamber & Motherboard Playfield
- **Grid Architecture:** **$24 \times 36$ cells**, constant 1:1.5 aspect ratio.
  - **Mobile ($390 \times 844\text{px}$ viewport):** $14\text{px}$ unit cell $\rightarrow$ **$336 \times 560\text{px}$ chamber**.
  - **Desktop / Steam ($1440 \times 900\text{px}$ viewport):** $20\text{px}$ unit cell $\rightarrow$ **$480 \times 720\text{px}$ chamber**.
- **Ample Gameplay Headroom Math:**
  - Total chamber width: **24 columns ($336\text{px}$)**.
  - Max block width (Tier 11 Titan): **11 columns ($154\text{px}$)**, representing **45.8% of chamber width**.
  - Remaining clearance: **13 columns ($182\text{px}$)** of completely clear passage. Even with a Titan sitting flush against one wall, smaller chips and medium tiers can freely pass down the opposite channel without jamming the chute.
- **Gantry:** Top-mounted SMT robotic vacuum placement nozzle on a precision linear rail with collimated optical crosshair laser guide.
- **Floor Bed:** Gold-plated LGA CPU socket contact bed with spring retention fingers and thermal paste pads.
- **Danger Line:** High-voltage hazard bus line (`// VBUS_OVERVOLTAGE_LIMIT //`) at row 6 ($84\text{px}$ below gantry).
- **SWAP Switch:** Illuminated SMT tactile micro-switch button at bottom-right of the bezel.

---

### 4.2 Block Hierarchy: Linear Dimensions & Silicon Packaging

Blocks are strictly square $N \times N$ rigid monoliths. To guarantee consistent tactile stacking and eliminate arbitrary scaling anomalies, **block dimensions increase strictly linearly** by $1\text{unit} = 14\text{px}$ per tier ($N \times 14\text{px}$):

| Tier | Grid Cells | Units | Pixel Size | Chamber Width % | Physical Architecture Package | Silicon Die Spec |
|:---:|:---:|:---:|:---:|:---:|:---|:---|
| **1** | $1 \times 1$ | 1 | $14 \times 14\text{px}$ | 4.2% | SOT-23 Micro-Chip Mote | Single-component primary pigment die |
| **2** | $2 \times 2$ | 2 | $28 \times 28\text{px}$ | 8.3% | QFN Dual-Pad Surface Mount | Two-pin ceramic carrier, dynamic core |
| **3** | $3 \times 3$ | 3 | $42 \times 42\text{px}$ | 12.5% | SOIC Small-Outline Integrated Circuit | Gull-wing leaded frame, expanded die |
| **4** | $4 \times 4$ | 4 | $56 \times 56\text{px}$ | 16.7% | Dual-Core BGA Micro-Processor | Solder-ball array perimeter, metallic lid |
| **5** | $5 \times 5$ | 5 | $70 \times 70\text{px}$ | 20.8% | Quad-Core Ceramic Integrated Circuit | Gold trace interconnects, centered die |
| **6** | $6 \times 6$ | 6 | $84 \times 84\text{px}$ | 25.0% | Multi-Die Heterogeneous SoC | Dual-channel heat spreader, dense die |
| **7** | $7 \times 7$ | 7 | $98 \times 98\text{px}$ | 29.2% | Octa-Core High-Performance Server CPU | Chamfered nickel lid, laser-engraved die |
| **8** | $8 \times 8$ | 8 | $112 \times 112\text{px}$ | 33.3% | Workstation Multi-Die Package | Quad-cluster compute carrier, dark die |
| **9** | $9 \times 9$ | 9 | $126 \times 126\text{px}$ | 37.5% | MCM Neural Processing Accelerator | High-density interposer, deep shadow die |
| **10** | $10 \times 10$ | 10 | $140 \times 140\text{px}$ | 41.7% | Multi-Socket Datacenter Module | Dual-latch retention rim, near-black die |
| **11** | $11 \times 11$ | 11 | **$154 \times 154\text{px}$** | **45.8%** | **Obsidian Titan Enterprise Monolith** | **Zero-Albedo Pure Black Core (`#000000`)** |

- **Physical Rendering:** Each block features an outer brushed metallic heat spreader (IHS) with chamfered edges, corner alignment triangle, laser-etched silkscreen model numbers, and a **mathematically centered square silicon die** that displays the synthesized pigment color and centered white/silver tier numeral.
- **Physics Behavior:** Rigid bodies with mass proportional to area ($m \propto N^2$). Downward gravity $g = 980\text{px/s}^2$, friction coefficient $\mu = 0.45$, restitution $e = 0.08$ (heavy, solid, dampened metallic thud with zero float).
- **Spawn Rules:** The gantry only spawns small primary chips (Tiers 1–3). Tiers 4 through 11 can only be created via fusion.

---

### 4.3 Subtractive CMY Pigment Synthesis (The Inverse of "RGB - Create the Light")

> **Precedent & Principle:** In earlier prototypes, static color swatches (e.g., "Tier 5 is Amethyst") conflicted with the core fantasy of light absorption. *Falling* implements the exact **subtractive inverse** of the additive pigment engine proven in *RGB - Create the Light*. Instead of adding $R, G, B$ light to synthesize White, *Falling* combines Cyan ($C$), Magenta ($M$), and Yellow ($Y$) pigments to absorb all light and synthesize **Pure Black (`#000000`)**.

#### 1. Pigment Vector State
Every block carries an internal pigment accumulator tuple:
$$\mathbf{P} = (C, M, Y) \quad \text{where } C, M, Y \in \mathbb{R}_{\ge 0}$$

#### 2. Spawning Primaries
Blocks dropped from the SMT gantry spawn with pure primary pigment units:
- **Cyan Chip:** $\mathbf{P} = (1.0, 0.0, 0.0)$
- **Magenta Chip:** $\mathbf{P} = (0.0, 1.0, 0.0)$
- **Yellow Chip:** $\mathbf{P} = (0.0, 0.0, 1.0)$
*(Higher-level drops in Tiers 2–3 carry scaled integer pigment multiples, e.g., $(2,0,0)$ or $(0,2,0)$).*

#### 3. Fusion & Pigment Combination Rule
When two chips of the same Tier $N$ touch, they fuse into a single Tier $N+1$ chip. The child chip accumulates the full sum of pigments from both parents:
$$C_{\text{child}} = C_1 + C_2, \quad M_{\text{child}} = M_1 + M_2, \quad Y_{\text{child}} = Y_1 + Y_2$$

#### 4. Subtractive Albedo Rendering (RGB Display)
The color of the block's centered inner silicon die is calculated dynamically using physical subtractive ink absorption against a target saturation threshold $T$:
$$R = \max\left(0.0, \; 1.0 - \frac{C}{T}\right)$$
$$G = \max\left(0.0, \; 1.0 - \frac{M}{T}\right)$$
$$B = \max\left(0.0, \; 1.0 - \frac{Y}{T}\right)$$

- When $C=0, M=0, Y=0 \implies \text{RGB}(1, 1, 1)$ (Unabsorbed / White).
- When pigments mix unevenly, rich tertiary inks emerge naturally (e.g., $C+M \rightarrow$ Deep Violet, $C+Y \rightarrow$ Forest Green, $M+Y \rightarrow$ Burnt Orange).
- As all three pigments accumulate toward $T$, the die darkens continuously through murky slate, dark charcoal, bruised plum, and finally settles into **$100\%$ zero-reflectance obsidian black (`#000000`)**.

---

### 4.4 Darkness Purity & The Tier 11 Singularity Annihilation

#### Darkness Purity Score Metric
Progress is reported on the motherboard BIOS hardware telemetry HUD (`SILICON_PURITY: 98.4%`):
$$\text{Purity \%} = 100 \times \frac{1}{|\mathcal{B}|} \sum_{b \in \mathcal{B}} \min\left(1.0, \; \frac{C_b + M_b + Y_b}{3T}\right)$$
Reaching $100\%$ Purity on the board triggers the climax sequence.

#### Endless Play via Singularity Implosion (Dual Tier 11 Annihilation)
Unlike traditional fusion games where the top tier permanently clogs the board, *Falling* supports **infinite high-score runs**:
1. **The Titan ($11 \times 11$):** Crafting the first Tier 11 Titan achieves the game's narrative climax (The Void).
2. **Dual-Titan Collision:** If the player continues playing and successfully crafts a **second Tier 11 Titan**, bringing the two Titans into contact triggers a **Singularity Implosion**:
   - **VFX Shockwave:** An electromagnetic collapse effect pulls screen pixels inward for $400\text{ms}$, followed by an inverted negative-color flash and a heavy sub-bass drone ($32\text{Hz}$).
   - **Board Clearance:** Both Tier 11 blocks **vaporize and disappear completely from the playfield**, instantly reclaiming $2 \times 154\text{px} = 308\text{px}$ of grid area and relieving chamber pressure.
   - **Score Bonus:** Awards a massive `SINGULARITY_ANNIHILATION: +100,000` purity bonus.
   - **Continuation:** The board remains active, allowing masters to chase multi-singularity runs and astronomical darkness scores.

---

## 5. Storyboard & Narrative Progression (11-Stage Phone Screenlife)

The story is told strictly through **Screenlife UI**: Leo Vance's phone screen glowing from behind the translucent motherboard chamber. Every tier progression unlocks an emotional, personal, and financial beat in his collapse.

> **Pacing & Trigger System:**
> - **Primary Default Rule (Tier Unlock):** Each narrative stage activates the first time the player synthesizes that respective Block Tier ($1 \dots 11$).
> - **Supported Alternative Pacing Rules (Configurable / For Platforms):**
>   - *Darkness Threshold Pacing:* Stages trigger at cumulative darkness milestones ($10\%, 20\%, \dots, 100\%$).
>   - *Buffer Pressure Pacing:* When the block stack rises above row 12 (approaching the danger line), urgent texts accelerate in real time, matching player stress.
>   - *Time-Elapsed Pacing:* For casual/cinematic modes, messages arrive on a realistic 3:32 AM timeline regardless of puzzle speed.

### Canonical 11-Stage Phone Storyboard Overview
![Falling 11-Stage Phone Storyboard](/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272/falling_11_scene_storyboard_panoramic.png)

*Interactive phone prototype live at `http://localhost:8089/phone_story_prototype.html` and visual matrix at `http://localhost:8089/storyboard.html`.*

---

### The 11-Stage Screenlife Matrix

| Stage & Tier | Pigment State | Clock & Battery | Active Apps & UI State | Narrative Beat, Exact Texts & Financial Stakes |
| :---: | :---: | :---: | :--- | :--- |
| **1: Spark** | $(1,0,0)$ / Primaries | `9:41 AM`<br>`100% 🔋` | **Lockscreen**<br>Ultrasound Polaroid | • **Wallpaper:** Ultrasound polaroid framed on lockscreen.<br>• **Messages:** *"Sarah: We're pregnant! 💕 Can't wait to tell our families tonight."*<br>• **Calendar:** `4:00 PM Hackathon AI Demo`.<br>• *Tone:* Uncorrupted optimism, innocent creative pride. |
| **2: Traction** | Dual Primaries | `11:15 AM`<br>`94% 🔋` | **App Store Connect**<br>& Messages | • **App Store Connect:** *10,000 active users in first 24 hours.*<br>• **Messages (CEO Alex):** *"You're a genius Leo. The algorithm works. Let's talk your equity refresh Monday."*<br>• **Twitter/X Banner:** Viral AI demo trending #2 in Tech. |
| **3: Seed Round** | $(1,1,0)$ Yellow/Magenta | `2:30 PM`<br>`88% 🔋` | **Chase Mobile**<br>& Messages | • **Chase Checking:** Direct deposit alert: *+$15,000.00 (Seed Closing Bonus)*.<br>• **Messages (Leo):** *"Seed bonus just hit! We finally have enough for the house down payment 🎉"*<br>• **Messages (Sarah):** *"Looking at 3-bedroom houses near the park right now 🏡"* |
| **4: Series A Euphoria** | $(1,1,1)$ All Primaries | `1:20 PM`<br>`81% 🔋` | **Carta Equity**<br>& Zillow | • **Carta Dashboard:** Paper value of options: **$1,500,000.00** ($100M valuation).<br>• **Zillow Alert:** *342 Elm Street ($750k) — Offer Accepted. $50,000 earnest deposit wired.*<br>• **Messages (Sarah):** *"Deposit sent! The nursery gets the morning sun ☀️"* |
| **5: Market Cools** | $(2,1,1)$ Olive-Brown | `11:42 AM`<br>`68% 🔋` | **Mortgage Portal**<br>& Messages | • **Mortgage Lender Alert:** *"Conditional approval requires verified proof of common stock vesting. 14 days remaining."*<br>• **Messages (Sarah):** *"Baby kicked during lunch! Doctor says everything is on track. Can you pick up Thai on your way home?"*<br>• *(Marked Read 7:45 PM — Leo working late, no reply sent).* |
| **6: The Crunch** | $(2,2,2)$ Murky Umber | `3:32 AM`<br>`14% 🪫` (Red) | **Dark Lockscreen**<br>& Slack War Room | • **Phone State:** OLED dark mode, 14% critical battery.<br>• **Missed Calls:** 📞 *2 Missed Calls from Sarah (1:45 AM, 2:30 AM)*.<br>• **Messages (Sarah):** *"Leo, it's almost 3 AM... are you still at the office? Please get some sleep, I'm worried."*<br>• **Slack (`#war-room-emergency`):** *"Runway under 60 days. Diligence audit repo must be clean by dawn."* |
| **7: Acquisition Rumors** | $(3,2,2)$ Bruised Plum | `2:15 PM`<br>`42% 🔋` | **Calendar Alert**<br>& Bloomberg News | • **Calendar Banner:** *[MISSED] 1:30 PM — OB/GYN 32-Week Baby Ultrasound*.<br>• **Bloomberg Tech:** *"TitanCorp in Talks for Distressed Acqui-Hire of Synapse AI as Venture Cash Dries Up."*<br>• **Messages (Leo):** *"So sorry honey, emergency board meeting called. How is our little guy?"*<br>• **Messages (Sarah):** *"He's fine. 4.5 lbs now. I wish you were there."* |
| **8: The Deal Announcement** | $(3,3,3)$ Charcoal Grey | `4:30 PM`<br>`31% 🔋` | **LinkedIn**<br>& Loan Officer | • **LinkedIn (CEO Alex):** *"Thrilled to announce Synapse AI has been acquired by TitanCorp! Huge thanks to our founders and investors for this exit. 🚀"*<br>• **Loan Officer SMS:** *"Congrats on acquisition! Send closing docs ASAP before tomorrow's escrow deadline."*<br>• **Messages (Sarah):** *"Saw Alex's post online!! Does this mean we're safe? I made dinner to celebrate 🎉"* |
| **9: The Liquidation Wipeout** | $(4,3,3)$ Dark Indigo | `5:45 PM`<br>`18% 🪫` | **Carta Liquidation**<br>& Voicemail | • **Carta Notice:** *Acquisition proceeds ($25M) allocated 100% to preferred investors. Common stock cancelled.<br><b style="color:#ef4444;">Payout per share: $0.00</b>*.<br>• **Voicemail (Loan Officer):** *"Leo, without equity liquidity, your mortgage is denied. The seller has issued a default notice claiming your $50,000 earnest deposit."* |
| **10: Deactivation & Ruin** | $(4,4,4)$ Deep Obsidian | `9:04 AM`<br>`8% 🪫` | **Chase Checking**<br>& Okta SSO | • **Chase Balance:** Drops from $50,842.10 to **$842.10** (*-$50,000.00 Escrow Deposit Forfeited to Seller*).<br>• **Okta Mobile SSO:** *Mobile credentials revoked by TitanCorp IT Administrator*.<br>• **Calendar:** **Baby Due Date in 7 Days**.<br>• **Unopened Text (Sarah):** *"Leo, the escrow agent emailed me... what does 'deposit forfeited' mean? Please tell me this is a mistake. Where are you?"* |
| **11: The Void (Titan)** | $(5,5,5)$ Pure Black | `12:48 AM`<br>`1% 🪫` | **Powering Off**<br>Pitch Black | • **Phone State:** Parked car in torrential rain. Empty battery icon flashes red.<br>• **OS Shutdown:** *"Shutting down..."* spinner fades.<br>• **Blackout:** Screen turns completely off. Total, silent, pitch-black void. Leo's night is finally at peace. |

---

### Archived Multi-Device Exploration Note
*During pre-production, an exploratory dual-track was illustrated featuring both a MacBook Pro and an iPhone. This was officially archived to preserve singular dramatic focus on Leo's phone behind the motherboard. The reference panoramic remains preserved in `assets/ui/storyboard/falling_dual_track_master_storyboard.png` for historical documentation.*

---

## 6. Art Direction & Theme Configurations

### The 3-Layer Visual Sandwich
1. **Layer 1: Phone Screen (Base Layer):**
   - Renders Leo Vance's active phone state (notifications, texts, battery, clock).
   - Dynamic backlight glows outward through the motherboard substrate.
2. **Layer 2: Translucent Motherboard Chamber (Filter Layer):**
   - Photorealistic PCB logic board plate with solder mask tuned to **~80% opacity**, allowing phone light and notification outlines to seep through the dark FR4 fiberglass.
   - SMT component detailing: SMD 0402 ceramic capacitors, dual DDR5 memory channels, steel PCIe slot, serpentine copper traces.
3. **Layer 3: Playfield & Silicon Chip Overlay (Foreground Layer):**
   - Precision $24 \times 36$ anti-aliased grid overlay ($14\text{px}$ unit scale).
   - SMT pick-and-place gantry with red crosshair laser.
   - Dropped silicon processor packages with metallic heat spreaders and dynamic color dies.
   - BIOS hardware telemetry HUD (`BUS_CLK: 4.80 GHz`, `VCC_CORE: 1.248V`, `SILICON_PURITY: 98.4%`).

---

### Chamber & Chip Style Customization (Modular Architecture)

To facilitate rapid reskinning and creative variations across platforms, the visual style is architected with modular parameters. The game specifies a **Recommended Default Combo** while keeping alternatives fully open:

#### Motherboard Chamber Styles
- **Option A: Matte Black FR4 / Modern High-End Server (RECOMMENDED DEFAULT):**
  - Stealth matte-black solder mask, brushed dark aluminum heatsinks, gold immersion test pads, subtle trace meanders. Optimal contrast for glowing phone screen backlight.
- **Option B: Classic Emerald Green & Immersion Gold:**
  - Nostalgic industrial green FR4 PCB, gleaming exposed ENIG gold bus traces, silver solder fillets, crisp white component silkscreen labels.
- **Option C: Cyber Blue Workstation:**
  - Deep sapphire blue solder mask, polished chrome heat sinks, cyan optical telemetry accents.

#### Silicon Processor Chip Styles
- **Option 1: Brushed Nickel IHS with Centered Core (RECOMMENDED DEFAULT):**
  - Modern desktop CPU look: silver/nickel heat spreader with laser-engraved corner triangle, micro-pin markings, and a centered square die displaying synthesized pigment and white numeral.
- **Option 2: Ceramic Purple & Gold PGA Package:**
  - Retro workstation aesthetic: dark ceramic package with gold brazed lid rim, gold corner pin, and central die.
- **Option 3: Bare Silicon Flip-Chip BGA:**
  - Direct die contact: mirror-finish reflective silicon die directly exposed on a green or black substrate without metal lid.

---

## 7. Controls & Interactivity

| Input Action | Keyboard / Mouse | Touch / Mobile | Controller | Function |
|:---|:---|:---|:---|:---|
| **Steer Gantry** | `A` / `D` or `←` / `→` or Mouse move | Drag finger horizontally | Left Stick / D-Pad | Positions SMT nozzle along overhead guide rail |
| **Drop Chip** | `S` / `↓` / `Space` / Click | Release finger / Tap chamber | `A` / Cross button | Fast-drops chip down with full gravity |
| **SWAP Mode** | `Tab` / `Shift` / Click button | Tap illuminated SWAP button | `Y` / Triangle / Bumper | **Pauses puzzle simulation** and brings phone screen to 100% focus |
| **Restart Run** | `R` (Hold 1.5s) | Double-tap BIOS reset button | Select / Back (Hold) | Triggers BIOS cold reboot and starts new run |

> [!IMPORTANT]
> **SWAP Simulation Pause:** When the player activates SWAP to read Leo's phone, the physics engine, falling blocks, and the 3-second buffer overflow timer **strictly pause**. The ambient soundscape cross-fades from motherboard electrical hum to domestic rain and muffled phone vibration, letting the player absorb the narrative beat without pressure.

---

## 8. Audio Direction & Soundscapes

The audio landscape reinforces the contrast between cold digital mechanics and raw domestic anxiety:
- **Puzzle Soundscape:**
  - Gantry stepper-motor servos: Precision micro-stepping clicks.
  - Chip drops & settling: Dense, heavy metallic thud with zero plastic rattle.
  - SMT Pick-and-Place: Crisp pneumatic vacuum release hiss.
  - Merges: Electrical arc crackle and resonant bell chime pitched by Tier.
  - Singularity Implosion: Deep $32\text{Hz}$ sub-bass vacuum suck followed by an electromagnetic pulse (EMP) whip.
- **Narrative Ambient Layer (Leaking from Phone):**
  - Distant torrential rain beating against a car windshield.
  - Faint, muffled iOS text vibration buzz (`bzz-bzz`) felt through haptics.
  - 3:32 AM low-frequency room drone.

---

## 9. Creative Design Surfaces & Online Platform Ingestion Guide

This section is authored specifically as an **ingestion specification for online game design platforms, vibe coding environments, and generative game creation tools** (e.g., Ludo.ai, Rosebud AI, FRVR Forge, EdenSpark, GDevelop). 

### 9.1 Directory of Game Vibe Coding & Generation Platforms

Based on current game vibe coding research and development platforms (referenced in the *Muse: Game Vibe Coding Prototypes* index):

1. **Ludo.ai** (`https://ludo.ai` | `app.ludo.ai`):
   - *Best for:* AI-assisted game design document breakdown, mechanics ideation, competitive market analysis, and generative 2D sprite/asset concepting.
   - *Workflow:* Paste the High Concept and Core Mechanics into Ludo's Game Ideator to generate mechanics variants, power-up systems, and UI wireframes.
2. **Rosebud AI** (`https://rosebud.ai`):
   - *Best for:* Browser-based natural-language game generation and vibe coding. Direct prompt-to-Phaser/Three.js code.
   - *Workflow:* Feed the Rosebud prompt below to spin up a fully playable 2D browser prototype in minutes.
3. **FRVR Forge / Playcraft** (`https://forge.frvr.com`):
   - *Best for:* Instant web/mobile hyper-casual and puzzle vibe coding with integrated physics and monetization templates.
   - *Workflow:* Use for rapid touch-screen physics tuning and instant viral web deployment.
4. **EdenSpark** (`https://edenspark.io`):
   - *Best for:* Open-source AI-assisted multiplatform game creation, live community jams, and cross-engine logic generation.
5. **Zoud GameLab** (`https://zoudgamelab.org`):
   - *Best for:* Narrative-driven and financial literacy game jams ($140k prize pool partnerships), exploring the real financial consequences of startup equity collapse and mortgage default.
6. **Playable Web Deployment Portals:**
   - **Poki** (`https://poki.com`) & **CrazyGames** (`https://crazygames.com`): Target platforms for lightweight HTML5/WASM builds.
   - **Itch.io** (`https://itch.io`): Primary target for narrative and indie physics puzzle game jams.

---

### 9.2 Sacred Core vs. Open Design Surfaces

When prompting generative AI tools or iterating on this design, respect the distinction between what is **Sacred** (the identity of the game) and what is **Open for Creative Innovation**:

| Dimension | The Sacred Core (DO NOT CHANGE) | Open Design Surfaces (INVITE AI TO TWEAK & IMPROVE) |
|:---|:---|:---|
| **Theme & Setting** | Leo Vance, infrastructure engineer, 3:32 AM, 14% battery, personal/financial collapse unfolding on phone. | Secondary visual skins (e.g., Cyberpunk deck, retro 1980s mainframe, Soviet analog computer). |
| **Physical Staging** | 3-layer sandwich: Phone Screen $\rightarrow$ Translucent Motherboard $\rightarrow$ Silicon Chip Grid. | Motherboard cosmetic details, capacitor layout, RGB trace lighting accents, fan speed animations. |
| **Block Aesthetic** | Silver/metallic processor package with centered square die showing numeral and color. | Alternate packaging styles (Ceramic PGA, flip-chip BGA, heat pipes, thermal paste splatters). |
| **Grid Math** | $24 \times 36$ cells, constant 1:1.5 ratio. Tier $N = N \times 14\text{px}$. Linear scaling. | Micro-gravity variations, bounciness/friction coefficients, gantry speed curves. |
| **Color Mechanics** | Subtractive CMY pigment synthesis accumulating to pure black (`#000000`). | Bonus pigment catalysts, "white thermal paste" cleansing blocks, pigment-filter power-ups. |
| **Endless Rule** | Merging two Tier 11s triggers Singularity Annihilation (implosion clear). | Combo point multipliers, cascading chain reactions, magnetic attraction between same-tier chips. |
| **SWAP Rule** | Opening SWAP strictly pauses physics and danger timers. | Interactive mini-actions on phone (e.g., swiping a notification to delay stress, unlocking bank app). |

---

### 9.3 Ready-to-Use Ingestion Prompts for AI Game Platforms

Copy-paste these structured prompts directly into **Ludo.ai**, **Rosebud AI**, **ChatGPT (o1/4o)**, or **Claude (Sonnet 3.5)**:

#### Prompt A: For Ludo.ai (Game Mechanics & Variant Ideator)
```markdown
You are an expert game designer reviewing the GDD for "Falling (Into the Darkness)", a Suika-style physics puzzler crossed with an existential screenlife narrative (Leo Vance at 3:32 AM). 

CORE CONSTRAINTS THAT CANNOT CHANGE:
- Chamber is a 24x36 grid with an SMT gantry dropping rigid square silicon CPU packages.
- Blocks scale linearly from Tier 1 (1x1) to Tier 11 (11x11, 45.8% width).
- Color synthesis is strictly SUBTRACTIVE CMY: drops are Cyan, Magenta, or Yellow, and fusing accumulates pigments towards Pure Black (#000000).
- Merging two Tier 11 Titans triggers a Singularity Implosion that annihilates both blocks to keep the game endless.
- Behind the translucent motherboard, Leo's phone reveals his life collapsing across 11 stages. SWAP strictly pauses physics.

CREATIVE TASK:
Flesh out and propose 3 innovative gameplay mechanics that enhance the tactile tension without breaking the core loop:
1. A "Thermal Overclock" or "Chip Temperature" risk-reward mechanic.
2. A high-skill combo or chain-reaction scoring mechanic that rewards deliberate placement.
3. Two optional secondary power-up blocks (e.g., Liquid Metal thermal compound, Voltage Surge shunt) that fit the realistic motherboard engineering theme.
Provide concrete mathematical rules, Godot 4 implementation notes, and player feedback descriptions for each.
```

#### Prompt B: For Rosebud AI / FRVR Forge / GDevelop (Playable Web Prototype)
```markdown
Generate a complete, playable 2D physics puzzle game in HTML5 / Canvas / Matter.js based on "Falling (Into the Darkness)":

1. PLAYFIELD:
   - Portrait canvas (336x560px), dark matte-black PCB background with glowing trace lines.
   - SMT gantry on top that follows mouse/finger horizontally. Clicking or releasing drops the active chip.
   - 2D rigid-body physics with heavy gravity and low bounce.

2. CHIP BLOCKS & LINEAR SCALING:
   - Unit cell = 14px. Tier N is exactly (N * 14) x (N * 14) pixels (Tier 1: 14px, Tier 2: 28px ... Tier 11: 154px).
   - Render each chip with a metallic brushed silver border and an inner colored square die showing the tier numeral centered.

3. SUBTRACTIVE CMY MIXING:
   - Spawns are Tiers 1-3 with pure Cyan (0,240,255), Magenta (255,0,127), or Yellow (255,215,0).
   - When two identical Tier N chips collide, they merge into Tier N+1.
   - Child pigment = Parent1 + Parent2. Die color is calculated via subtractive ink: R = max(0, 1 - C/5), G = max(0, 1 - M/5), B = max(0, 1 - Y/5), converging to pure black (#000000) at Tier 11.

4. SINGULARITY ANNIHILATION:
   - When two Tier 11 Titans touch, trigger an implosion screen-shake and delete both chips, granting +100,000 points.

5. NARRATIVE SWAP:
   - Pressing "SPACE" or clicking "SWAP" pauses physics and reveals an iOS notification overlay: "3:32 AM - Wife: Leo, are you coming home? - Chase: Balance $842.10 - Okta: Credentials Revoked".

Make the code self-contained, responsive, and immediately playable.
```

#### Prompt C: Narrative Expansion & Branching (For Claude / Chat Platforms)
```markdown
You are a dramatic writer specializing in Screenlife narratives (e.g., Searching, Succession, Black Mirror). 
Review the 11-Stage Phone Screenlife in "Falling (Into the Darkness)" where infrastructure engineer Leo Vance watches his life implode at 3:32 AM across 11 tiers (Ultrasound Polaroid -> Viral App -> Seed Round -> Series A -> Mortgage Contingency -> 3:32 AM Crunch -> Rumors -> Deal Announcement -> Liquidation Wipeout -> Deactivation -> Pitch Black).

TASK:
Propose a branching narrative module for the phone:
1. Write 3 alternative micro-threads that can trigger based on how the player plays (e.g., if player plays fast, if player stalls near the danger line, if player achieves multiple Singularities).
2. Write exact realistic texts, calendar alerts, and automated system emails with authentic tech startup jargon (Carta liquidation preferences, 83(b) tax elections, AWS bill spikes).
3. Ensure every beat preserves the quiet, gut-wrenching emotional contrast between the calm puzzle game and the real human heartbreak.
```

---

## 10. MVP Implementation Checklist

- [x] Consolidate $24 \times 36$ grid parity ($336 \times 560\text{px}$ chamber, $14\text{px}$ unit scale).
- [x] Lock in Titan Monolith mathematical ratio ($154 \times 154\text{px}$, 45.8% width) with clear $182\text{px}$ passage headroom.
- [x] Standardize strict linear block scaling ($N \times 14\text{px}$) across all 11 tiers.
- [x] Define dynamic subtractive CMY pigment synthesis engine (inverse of *RGB - Create the Light*).
- [x] Implement Tier 11 Singularity Annihilation rule for endless play sessions.
- [x] Finalize Silicon Processor Chip architecture (Brushed silver nickel IHS + centered colored die).
- [x] Establish modular motherboard chamber styles (Recommended: Option A Matte Black FR4 + Option 1 Nickel IHS).
- [x] Canonicalize the 11-Stage Screenlife Storyboard and phone narrative matrix.
- [x] Author AI platform ingestion guide and prompt templates for online vibe coding tools.
- [ ] Connect Godot 4 rigid-body physics and SMT placement gantry.
- [ ] Wire subtractive CMY shader in Godot 4 / WebGL.
- [ ] Connect SWAP pause state to physics simulation.
- [ ] Wire audio stems (servo clicks, metal clangs, EMP singularity pulse, muffled rain).

---

*Last revised: October 2026. Fully consolidated with Subtractive CMY Pigment Synthesis, Linear Headroom Architecture, Dual Tier 11 Singularity Annihilation, 11-Stage Screenlife Narrative, and Online Vibe Coding Platform Ingestion Guide.*
