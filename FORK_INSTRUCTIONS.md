# Air Bubble — Fork Jumpstart & Context

## Project Overview
- **Working Directory:** `/Users/georgearmah/air-bubble`
- **Engine:** Summer Engine (Godot 4.3+ compatible)
- **Concept:** *A.I.r bubbles* — Inverted-buoyancy Suika Game ("Watermelon Game") physics puzzle where bubbles float upward, merge into 11 number tiers, and fill "Lake Ellem" (satirizing the AI startup hype cycle).
- **Core Mechanics:**
  - 11 Tiers with 1:1 math ($N+N \to N+1$, awarding $N+1$ points).
  - Bubbles float UP toward surface ceiling.
  - Tier 11 is an Apex Titan (permanent obstacle, does not pop).
  - Overflow danger line at bottom vent (3s countdown to Game Over).
  - Fully procedural audio and visual styling in GDScript (zero cloud spend).
- **Complete Handoff & Continuity Guide:**
  - See [`LLM_HANDOFF.md`](file:///Users/georgearmah/air-bubble/LLM_HANDOFF.md) for full architecture, CLI commands, and next roadmap tasks.

## Running the Project
- To open in Summer Engine editor:
  ```bash
  SUMMER_ENGINE_PROJECT="/Users/georgearmah/air-bubble" npx -y summer-engine@latest run /Users/georgearmah/air-bubble
  ```
- To start/stop game:
  ```bash
  SUMMER_ENGINE_PROJECT="/Users/georgearmah/air-bubble" npx -y summer-engine@latest tool summer_play
  SUMMER_ENGINE_PROJECT="/Users/georgearmah/air-bubble" npx -y summer-engine@latest tool summer_stop
  ```

