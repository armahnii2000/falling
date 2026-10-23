# Falling — Roadmap

Falling (Into The Darkness) is a 2D physics puzzle game (see `README.md` and
`GDD.md`): drop processor blocks into a chamber, merge matching tiers, and
mix subtractive CMY pigments toward pure black at the top tier, without
letting the stack sit above the hazard line. The core game is built and
playable; the work below is completing it — finishing the remaining gameplay
systems, tuning it across all 11 tiers, and shipping a polished web build.

## Gameplay completion

- [ ] Finish the remaining core-loop systems: merge resolution at high
      tiers, hazard-line pressure rules, and the game-over/restart flow
- [ ] Complete tier progression content: block behaviour and pigment mixing
      verified at every tier from 1 to 11
- [ ] Edge cases: large-stack stability, simultaneous merges, and chamber
      overflow behaviour

## Tuning and feel

- [ ] Difficulty tuning: hazard-line pressure, merge pacing, and the buffer
      overflow window across the 11 tiers
- [ ] Game-feel pass: drop/settle physics, restitution damping, merge
      feedback at high tiers
- [ ] Procedural audio pass: deepen merge chimes at high tiers, balance the
      layer-swap sweep

## Build and release prep

- [ ] Web export build, verified in-browser (desktop + mobile viewport)
- [ ] Performance pass on large stacks (late-game board states)
- [ ] Playtest rounds with fixes; known-issue sweep in the Godot project

## Documentation

- [ ] Controls/how-to-play section in the README
- [ ] Screenshot/GIF refresh for the current build

## Right screen — Stellar Pursuit (Vertex Ascent)

Design: `docs/vertex-ascent-stellar-pursuit.md`. A second, synchronized
screen beside the chamber: a starship chasing a shooting star, where merge
points are the only thing that close the distance gap.

- [ ] Pursuit viewport: streaming starfield, ship, and comet with a live
      distance readout
- [ ] Points-driven gap: merge score feeds the closing speed; balanced
      play holds the slipstream (1.25× closing efficiency)
- [ ] Score-balance steering and chamber tilt (Red right / Blue left,
      capsize at ±45°) wired to the fusion chamber's Red/Blue channels
