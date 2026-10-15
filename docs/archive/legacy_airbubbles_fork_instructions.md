# Air Bubble — Fork Jumpstart & Context

## Project Overview
- **Working Directory:** `/Users/georgearmah/air-bubble-experiment-2`
- **Git Branch:** `experiment/experiment-2` (forked from `experiment/nn-grid-thermal-edition` at `3af19cb`)
- **Parent Conversation Fork:** `a9cc8ba9-a0ae-484e-8f39-dd1eae6e27a6`
- **Engine:** Summer Engine (Godot 4.3+ compatible) & Web Engine / Monte Carlo test harness
- **Web Prototype Port:** `8086` (`python3 web/server.py`)
- **Concept:** *A.I.r bubbles* — Inverted-buoyancy Suika Game physics puzzle + n×n Grid & Thermal Defusal mechanics.

## Running the Web Prototype (Phone & Desktop)
- Start the server:
  ```bash
  python3 /Users/georgearmah/air-bubble-experiment-2/web/server.py
  ```
- **Desktop:** http://localhost:8086
- **Local Wi-Fi (Phone):** http://192.168.1.225:8086

## Running Summer Engine (Godot)
- Open in Summer Engine editor:
  ```bash
  SUMMER_ENGINE_PROJECT="/Users/georgearmah/air-bubble-experiment-2" npx -y summer-engine@latest run /Users/georgearmah/air-bubble-experiment-2
  ```
- Start/stop game:
  ```bash
  SUMMER_ENGINE_PROJECT="/Users/georgearmah/air-bubble-experiment-2" npx -y summer-engine@latest tool summer_play
  SUMMER_ENGINE_PROJECT="/Users/georgearmah/air-bubble-experiment-2" npx -y summer-engine@latest tool summer_stop
  ```

