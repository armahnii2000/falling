# Falling — Realistic Coding Sessions submission scope

Prepared for the "Realistic Coding Sessions" evaluation (Labelbox).
This branch scopes Falling to what fits that project's provided desktop.
The game design itself is unchanged — see `GDD.md` and `README.md`.

## The project in one paragraph

Falling is a 2D physics merge puzzle. The player drops square processor
blocks into a chamber; two blocks of the same tier merge into the next
tier up, and each merge mixes subtractive CMY pigment, so blocks darken
tier by tier until one reaches pure black at tier 11. A hazard line near
the top ends the run if the stack sits above it too long. Behind the
chamber, a phone screen receives story messages as the score rises, and
a second screen — Stellar Pursuit — turns merge points into the closing
speed of a starship chasing a shooting star: capture at 0m is the win
that balances the hazard line's loss.

## What this branch includes — and what it leaves out

The evaluation desktop has no internet, no GPU, no Docker and no sound,
and it does not have Godot. Interfaces are local web apps in its browser.

- **In scope:** the web version only — `web/game.js`, `web/physics.js`,
  `web/index.html` and the pages they depend on. Plain HTML/CSS/JavaScript,
  run locally, tested with Node.
- **Out of scope on this branch:** the Godot 4 project (`scripts/`,
  `addons/`, `samples/`, project files), and procedural audio
  (`web/audio.js`). The desktop has no sound, so the workspace build
  ships silent; audio stays on `main` for the Godot/web release builds.
- No accounts, no cloud services, no real data of any kind. All story
  messages and play data are fictional and live in the repo.

## Work plan (the work ahead, in session-sized pieces)

1. **Web engine hardening.** Separate the merge/physics rules from the
   rendering in the web build so the rules run headless under Node.
   Port the existing Godot-side test intent (`tests/test_merge.gd`,
   `test_scoring.gd`, `test_spawn.gd`, `test_state.gd`,
   `test_thresholds.gd`) into a Node test suite for the web rules.
2. **All 11 tiers verified.** Automated drop-and-merge tests for every
   tier 1–11: pigment result, size, scoring, and simultaneous-merge and
   large-stack edge cases. Hazard-line timing, game-over and restart
   covered by tests, not just play.
3. **Stellar Pursuit built in full.** Starfield viewport, starship and
   shooting star, live distance readout. Merge score is the only thing
   that closes the gap (higher tiers close it faster, no passive closing
   while idle). Capture at 0m ends the run as a win. Synced with the
   chamber so both screens always agree on score and run state.
4. **Deterministic runs and replays.** Seeded block dealing so a run can
   be replayed exactly; a replay checker that replays recorded runs and
   compares final state. A simple bot that plays seeded games to catch
   invariant breaks (blocks lost, pigment going backwards, score
   mismatches between the two screens).
5. **Screenlife layer finished for the web build.** The phone screen
   under the chamber: message notifications tied to score thresholds,
   tap-to-tray, and the SWAP focus change that pauses physics while
   reading. Message set is fictional, stored as data files, with tests
   that every threshold fires once and in order.
6. **Tuning pass, measured.** Hazard-line pressure, overflow window and
   merge pacing tuned against bot runs (target run-length distribution),
   then human playtest rounds with fixes.

## Success bar (checkable on the desktop)

- The Node test suite passes: merge, scoring, spawn, state and
  threshold tests for all 11 tiers.
- 1,000 seeded bot games complete with no invariant violations, and
  every recorded replay reproduces its final state exactly.
- A full game can be won (Stellar Pursuit capture at 0m) and lost
  (hazard-line overflow) in the local web build, in the desktop's
  browser, with both screens agreeing on score throughout.
- The message layer fires every story beat once, in order, across a
  full run.

## Stack

HTML, CSS and JavaScript (Canvas) for the game; Node for the headless
test suite. Nothing else is required: no build step, no packages beyond
what the desktop's npm mirror carries, no Docker, no GPU, no sound.

## Licence and origin

Original project by George Armah, MIT licence (see `LICENSE`). All art
in the repo is original to the project; no commercial game, film or app
assets are used.

## Submission note

This file is repo prep: scope, plan and success bar. The evaluation
form answers themselves — including the report on how I use AI coding
tools — are written by me, in my own words, when I submit.
