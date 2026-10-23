# Falling — Roadmap

Falling (Into The Darkness) is a working 2D physics puzzle game with a
screenlife narrative (see `README.md` and `GDD.md`). The work below is the
planned continuation: finish the narrative implementation, tune the game
feel, and get a polished, playable web build in front of testers.

## Narrative implementation

- [ ] Implement the full 11-stage screenlife storyboard from the GDD in the
      phone layer (message sequences, alerts, timing against score)
- [ ] Wire stage transitions to merge milestones so story beats land on
      gameplay events, not timers alone
- [ ] Final pass on message/alert copy for every stage

## Gameplay and feel

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
