# Ancient Dash: Rooftop Run

A lightweight Three.js third-person parkour adventure set in a stylized Ancient Egypt cityscape. Play as a 10-year-old kid racing across 45 checkpoints while dodging silly mummies and hazards.

## Run locally
1. Start a simple web server from this folder:
   ```bash
   python -m http.server 8000
   ```
2. Open http://localhost:8000 in Chrome.
3. Click **Play** or **Continue** (progress is saved in localStorage). If you want a fresh run, use **Reset Progress**.

## Controls
- **WASD** – Move
- **Mouse** – Look (click canvas to lock pointer)
- **Space** – Jump
- **Shift** – Sprint (drains stamina bar)
- **E** – Interact (future hooks, e.g., gates)
- **Esc** – Pause menu

## Gameplay notes
- 45 checkpoints: respawn at your last checkpoint instantly.
- Early checkpoints show short tutorial prompts; difficulty ramps gently.
- Checkpoint progress and collectibles save to localStorage.
- Hazards and mummies cause a “trip” and respawn (no damage meter).
- Guidance orb + arrow UI always point to the next checkpoint.

Enjoy the rooftop dash! Hope the wind ambience and soft visuals keep it cozy and exciting.
