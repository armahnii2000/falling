# Vertex Ascent: Stellar Pursuit

**Genre:** Dual-Screen 2D Physics Puzzle & Sci-Fi Pursuit
**Visual Style:** Clean Modern Vector, Neon Avionics HUD, 3D Warp Starfield

A dual-screen design for Falling: the gravity fusion chamber runs on the left
screen while a points-driven starship pursuit runs on the right. Merges on
the left are the only thing that move the chase on the right — the two
screens are one game.

## Core Mechanics & Layout

The game runs on two synchronized parallel screens.

### Left Screen — Gravity Fusion Chamber

- **Drop & Merge:** Aim and drop regular polygons (3 to 16 sides, labeled
  with their side count). Only polygons with the exact same side count can
  merge.
- **Color Alchemy:** The dropper spawns only Red and Blue polygons
  (tiers 3–5). White polygons are never spawned; they are synthesized
  exclusively by merging Red + Blue:
  - Red(N) + Red(N) ➔ Red(N+1) (+Red Score)
  - Blue(N) + Blue(N) ➔ Blue(N+1) (+Blue Score)
  - Red(N) + Blue(N) ➔ White(N+1) (+Total Score)
  - White(N) + Blue(N) ➔ Blue(N+1) | White(N) + Red(N) ➔ Red(N+1) |
    White(N) + White(N) ➔ White(N+1)
- **Dynamic Chamber Tilt:** The container tilts based on score delta
  (Red tilts Right, Blue tilts Left). The left half has a soft blue glow
  (◀ BLUE / TILT LEFT), the right half a red glow (RED / TILT RIGHT ▶).
  Shapes slide naturally on tilted surfaces with solid wall containment.

### Right Screen — Stellar Pursuit Viewport

- **Continuous Deep-Space Chase:** A starship pursues a glowing celestial
  shooting star across streaming starfields and cosmic dust.
- **Strictly Points-Driven Gap:** Idling does not close the gap; the
  distance to the comet decreases exclusively as points are scored from
  polygon merges.
- **Lateral Steering:** Score balance steers the starship laterally:
  - Balanced (tilt near 0°): ship locks into the central slipstream,
    granting 1.25× Closing Speed Efficiency.
  - Blue > Red: ship veers left (port), drifting out of the slipstream.
  - Red > Blue: ship veers right (starboard), drifting out of the
    slipstream.

## Win / Loss Conditions

- **Victory:** Earn enough points to reduce the distance gap to 0m and
  capture the shooting star.
- **Defeat:**
  - **Capsize:** Chamber tilt reaches or exceeds ±45°.
  - **Overflow:** Shapes stay above the top red hazard boundary for
    >3 consecutive seconds.

## Controls

- Mouse/Touch drag along the top rail to aim, release/click to drop.
- Arrow keys / A–D to steer, Space / Down to drop.
- Pause on P.
- Fully responsive desktop and mobile HUD.
