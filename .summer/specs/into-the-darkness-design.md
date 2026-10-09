# Into the Darkness — Technical & Narrative Specification

## 1. Game Concept & Narrative Soul
* **Title:** *Into the Darkness* (Book 1 of an existential tech trilogy)
* **Protagonist:** Leo Vance, lead infrastructure engineer at Apex Technologies.
* **Premise:** It's 3:32 AM. Leo is at his desk playing an addictive puzzle game while his life collapses in real-time in the background. His Slack access was revoked, his mortgage payment is pending, and his wife is texting him to come to bed.
* **Metaphor:** Leo is seeking "Total Darkness" (100% Black #000000) — an obsession with complete light absorption to escape the relentless corporate burnout, before finding redemption through family.

---

## 2. The 3-Layer Visual Architecture
1. **Layer 1: The Phone Screen (Base Layer)**
   * Realistic smartphone display (iPhone / modern dark mode).
   * 3:32 AM clock, red 14% low battery indicator, dynamic island.
   * Incoming notifications from Wife, Slack, Banking, and News alerts.
2. **Layer 2: Frosted / Translucent Glass (Optical Filter)**
   * Floating beveled crystal glass chamber plate with specular rim highlights.
   * Smoked diffuse body (`alpha ~ 35%`, `blur ~ 6px`).
   * Renders the phone screen softly visible beneath the playfield without distracting from gameplay.
3. **Layer 3: The Game Board (Transparent Overlay)**
   * **100% transparent background** (pure alpha channel).
   * Top horizontal dropper slider rail with glowing 3D cube ready to drop.
   * Laser guide line.
   * Stack of 3D beveled square blocks with sub-grid lines and numbers.
   * Bottom circular glowing "SWAP" button.

---

## 3. Physics & Mechanics
* **Gravity:** Downward standard gravity ($g = +980\text{ px/s}^2$).
* **Block Shapes:** Strictly **square $N \times N$ cubes** (no polyominoes/Tetris shapes):
  * Tier 1: $1 \times 1$ ($24\text{px}$)
  * Tier 2: $2 \times 2$ ($38\text{px}$)
  * Tier 3: $3 \times 3$ ($52\text{px}$)
  * Tier 4: $4 \times 4$ ($68\text{px}$)
  * Tier 5: $5 \times 5$ ($84\text{px}$)
  * Tier 6: $6 \times 6$ ($102\text{px}$)
  * Tier 7: $7 \times 7$ ($122\text{px}$)
  * Tier 8: $8 \times 8$ ($144\text{px}$)
  * Tier 9: $9 \times 9$ ($168\text{px}$)
  * Tier 10: $10 \times 10$ ($194\text{px}$)
  * Tier 11: $11 \times 11$ ($224\text{px}$) — The Obsidian Black Monolith.

---

## 4. Subtractive CMY Ink Synthesis
Unlike additive RGB mixing (which produces White light), *Into the Darkness* uses **subtractive CMY ink synthesis** (like physical paint or printing ink) where combining pigments absorbs light and leads to **100% Black**:

$$\begin{aligned}
C_{\text{child}} &= C_1 + C_2 \\
M_{\text{child}} &= M_1 + M_2 \\
Y_{\text{child}} &= Y_1 + Y_2
\end{aligned}$$

The RGB screen display is rendered as:
$$R = 1.0 - C, \quad G = 1.0 - M, \quad B = 1.0 - Y$$

* **Base Ink Spawns (Tiers 1–3):**
  * Pure Cyan: $(C=1, M=0, Y=0) \to \text{RGB}(0, 240, 255)$
  * Pure Magenta: $(C=0, M=1, Y=0) \to \text{RGB}(255, 0, 127)$
  * Pure Yellow: $(C=0, M=0, Y=1) \to \text{RGB}(255, 215, 0)$
* **Secondary Mixes:**
  * Cyan + Magenta $\to$ Deep Cobalt / Violet
  * Cyan + Yellow $\to$ Emerald Green
  * Magenta + Yellow $\to$ Crimson Red
* **Tertiary & Equilibrium (Tier 11 Apex):**
  * $C = M = Y = \text{Max} \to \text{RGB}(0, 0, 0)$ (Pure Obsidian Black).

---

## 5. Dual-Screen Interactivity
* **Live Focus Swap:**
  * Player taps the "SWAP" button (or presses 'S' / Space).
  * Smooth CSS cross-fade / blur transition shifts focus between Game Chamber and Phone Screen.
* **Sinking Notifications:**
  * At milestone thresholds (Score 1,000, Tier 4, Tier 8, etc.), an urgent notification pops directly onto the Game Screen.
  * Tapping the notification triggers an ink-dissolve animation that "melts/sinks" it down through the translucent glass into the Phone Screen underneath.
