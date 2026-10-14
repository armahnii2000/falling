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

## 5. Storyboard & Narrative Progression (Complete 11-Stage Dual-Track)

The narrative is never told through conventional cutscenes. It is told strictly through **Screenlife** UI states: the phone screen glowing through the semi-translucent motherboard chamber, cross-referenced with the MacBook Pro paper trail. Every gameplay tier corresponds 1-to-1 with an emotional and financial beat in infrastructure engineer Leo Vance's collapse.

### Master Dual-Track Panoramic Storyboard
![Master Dual-Track Storyboard](/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272/falling_dual_track_master_storyboard.png)

*Interactive web viewer available at `http://localhost:8089/storyboard.html` and live phone demo at `http://localhost:8089/phone_story_prototype.html`.*

---

### The 11-Stage Screenlife Matrix

| Tier & Subtractive Ink | 💻 MacBook Pro Track (Corporate & Code Paper Trail) | 📱 iPhone Track (Personal, Family & Financial Reality) |
| :--- | :--- | :--- |
| **Tier 1: Spark**<br>`(0,0,0)` Clean White | **VS Code Clean Prototype:**<br>• `main.py` commit `git commit -m "initial prototype"`<br>• Terminal: 100% test pass. Clean dark editor. | **9:41 AM Lockscreen (100% Battery):**<br>• Wallpaper: First framed baby ultrasound Polaroid.<br>• *Wife text: "We're pregnant! 💕 Can't wait to tell our families tonight."*<br>• Calendar: 4:00 PM Hackathon AI Demo. |
| **Tier 2: Traction**<br>`(1,0,0)` Pure Cyan | **Hacker News #1 & GitHub Star Surge:**<br>• Hacker News front page: *"Show HN: Synapse AI — Distributed Neural Engine"*<br>• Slack: `#general: Traffic spike incoming! 🚀` | **App Store Connect Viral Alert:**<br>• *10,000 active users in 24 hours.*<br>• *CEO Alex: "You're a genius Leo. The algorithm works. Let's talk your equity refresh on Monday."*<br>• Twitter/X trending banner. |
| **Tier 3: Seed Round**<br>`(1,1,0)` Magenta Injected | **Tier-1 VC Pitch & Carta Grant:**<br>• Zoom gallery with VC partners in Patagonia vests.<br>• Carta Equity Dashboard: 1.5% Common Stock (Est. Value: $450,000). | **Chase Direct Deposit (+$15,000.00):**<br>• Seed Closing Bonus clears into checking.<br>• *Leo: "Seed bonus just hit! We finally have enough for the house down payment 🎉"*<br>• *Wife: "I love you so much! Looking at 3-bedroom houses near the park right now 🏡"* |
| **Tier 4: Series A Euphoria**<br>`(1,1,1)` Yellow Flooded | **TechCrunch Feature ($100M Valuation):**<br>• TechCrunch headline: *"Synapse AI Raises $25M Series A at $100M Valuation"*<br>• Carta paper equity: **$1,500,000.00**. | **Zillow Escrow Deposit ($50,000):**<br>• 342 Elm Street ($750k). Offer Accepted.<br>• $50,000 earnest money deposit wired.<br>• *Wife text: "Wire sent! The nursery gets the most beautiful morning sunlight ☀️"* |
| **Tier 5: Market Cools**<br>`(1,1,2)` Sickly Olive | **Board Deck: Burn Rate Warning:**<br>• Q3 Board Deck: *"Revenue: 48% of Target. Burn rate: $1.2M/mo. Runway: 5 months."*<br>• Slack: `#hiring-freeze` created. | **Mortgage Lender Underwriter Condition:**<br>• Alert: *"Loan approval conditional on verified proof of common stock vesting in 14 days."*<br>• *Wife: "Baby kicked during my lunch break! 💕 Doctor says everything is right on track. Pick up Thai on your way home?"* (Marked Read 7:45 PM, no reply). |
| **Tier 6: The Crunch**<br>`(2,2,2)` Murky Brown | **3:30 AM Diligence Audit Terminal:**<br>• Dark-mode terminal with red security audit logs: *"Audit for Acquisition Due Diligence"*. Runway sub-60 days.<br>• Private locked Slack: `#founders-only 🔒`. | **3:32 AM Dark Lockscreen (14% Battery):**<br>• 📞 2 Missed Calls from Wife (1:45 AM, 2:30 AM).<br>• *Wife text: "Leo, it's almost 3 AM... are you still at the office? I left dinner in the fridge. Please get some sleep, I'm worried."*<br>• Slack #war-room: *"Repo must be clean by dawn."* |
| **Tier 7: Acquisition Rumors**<br>`(3,2,2)` Bruised Plum | **Bloomberg Distress Report:**<br>• Bloomberg News: *"TitanCorp in Advanced Talks for Distressed Acqui-Hire of Synapse AI as Runway Vanishes"*<br>• CEO Slack: *"Ignore press rumors. Heads down, keep building!"* | **Calendar Alert: 32-Week Ultrasound [MISSED]:**<br>• Scheduled 1:30 PM today (Marked MISSED).<br>• *Leo text: "So sorry honey, emergency board meeting called. How is our little guy?"*<br>• *Wife: "He's fine. 4.5 lbs now. I wish you were there."* |
| **Tier 8: The Deal Announcement**<br>`(3,3,3)` Dark Charcoal | **Zoom All-Hands: Acqui-Hire Slide:**<br>• CEO Alex and CTO smiling on Zoom beside TitanCorp VP.<br>• Slide: *"Exciting New Chapter: Synapse AI Joins TitanCorp!"* | **LinkedIn CEO Exit Announcement:**<br>• Post: *"Thrilled to announce Synapse AI has been acquired by TitanCorp! Huge thanks to our founders and investors for this exit. 🚀"*<br>• *Wife: "Saw Alex's post online!! Does this mean we're safe? I made dinner to celebrate 🎉"*<br>• Loan Officer: *"Send closing docs ASAP before tomorrow's escrow deadline."* |
| **Tier 9: The Liquidation Wipeout**<br>`(4,3,3)` Violet-Black | **DocuSign Shareholder Liquidation Waterfall:**<br>• Series A Preferred: $25M (100% to VCs)<br>• Founder Retention Pool: $8M<br>• <b style="color:#ef4444;">Common Stock Payout Per Share: $0.00</b> | **Carta Cancellation & Mortgage Default:**<br>• Carta Alert: *"Acquisition proceeds allocated 100% to preferred. Options cancelled. Payout: $0.00"*<br>• Loan Officer Voicemail: *"Leo, without equity liquidity, your mortgage is denied. The seller has issued a default notice claiming your $50,000 earnest deposit."* |
| **Tier 10: Deactivation & Ruin**<br>`(4,4,4)` Cold Slate | **Okta SSO Authentication Lockout:**<br>• <b style="color:#ef4444;">403 FORBIDDEN: Account disabled by administrator</b><br>• Slack: `Disconnected (Session Terminated)`<br>• Google Workspace: `Access Denied` | **Chase Checking Drops to $842.10:**<br>• -$50,000.00 default deduction (Escrow Forfeited).<br>• TitanCorp People Ops: *"Employment separation notice. Mobile credentials revoked."*<br>• Calendar: **Baby Due Date in 7 Days**.<br>• *Wife panicked text: "Leo, the escrow agent emailed me... what does 'deposit forfeited' mean? Please tell me this is a mistake. Where are you?"* |
| **Tier 11: The Void (Titan)**<br>`(5,5,5)` Pitch Black | **Closed MacBook Pro Lid:**<br>• MacBook lid closed on desk in dark room.<br>• Cold reflection of torrential rain against the window. | **Dead Battery Blackout Void:**<br>• Inside dark car parked in the rain. 1% red empty battery icon flashes.<br>• Phone display shuts off completely.<br>• Total, silent, pitch-black void. Leo's night is finally at peace. |

---

### Track 1: Phone Screen Storyboard Panels
![Phone Screens Tiers 1-11 Panoramic](/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272/falling_11_scene_storyboard_panoramic.png)

### Track 2: MacBook Pro Storyboard Panels
![MacBook Pro Screens Tiers 1-11 Panoramic](/Users/georgearmah/.gemini/antigravity/brain/2c3a64ae-9518-4997-82a0-7008e590a272/falling_macbook_track_panoramic.png)

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
