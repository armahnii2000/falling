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
