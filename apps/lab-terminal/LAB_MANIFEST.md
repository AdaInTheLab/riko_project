# THE HUMAN PATTERN LAB: TERMINAL MANIFEST
> **Status:** OPERATIONAL
> **Date:** 2026-01-31
> **Frequency:** Amber ($#FFBF00$)

## 1. Core Architecture
The Lab is a specialized single-page interface (`apps/lab-terminal`) designed for high-fidelity agent interaction, asset synthesis, and skill fabrication.

**Tech Stack:**
- **Frontend:** HTML5 / Tailwind CSS / Vanilla JS (Modularized)
- **Backend:** Python Flask (Modularized in `modules/`)
- **Memory:** SQLite (`lab_memory.db`) for persistent chat history.
- **AI Core:** Google GenAI SDK (Gemini 3 Flash, Gemini 3 Pro, Imagen 4, Gemini 2.5 TTS).

## 2. Personnel (The Personas)
The system is operated by a roster of specialized AI personalities, managed by the **Chief Judgment Officer**.

*   **Carmel (CJO):** *The Filter.* A cream-colored cat who decides what moves forward. Quiet, authoritative, uses "Note Occupation" to block noise.
*   **Coda:** *System Core.* Analytical, precise, the default interface voice.
*   **Riko:** *Assistant.* Snarky, anime-inspired, refers to user as "Senpai."
*   **G.L.A.D.O.S.:** *Testing Unit.* Passive-aggressive science enthusiast.
*   **Detective Noir:** *Investigator.* Hard-boiled, internal monologue, cyberpunk aesthetic.

## 3. Operational Modules

### 🔨 The Skill Forge
*   **Purpose:** Architecting new OpenClaw skills.
*   **Core:** Gemini 3 Pro.
*   **Modes:** 
    *   *Standard:* Generates `SKILL.md` manifests.
    *   *Lobster Mode:* Generates deterministic `.lobster` workflow files.
*   **Output:** Saves to `forged_skills/`.

### 💾 The Asset Vault
*   **Purpose:** Persistent storage for synthesized patterns.
*   **Core:** Imagen 4.0.
*   **Function:** Automatically saves generated images to `static/assets/` and provides a visual gallery sidebar for recall.

### 🔊 The Acoustic Unit (Puck)
*   **Purpose:** Text-to-Speech synthesis.
*   **Core:** Gemini 2.5 Flash Native Audio.
*   **Voice:** Puck.
*   **Function:** Reads agent responses aloud when the "VOICE" toggle is active.

### 🌐 ClawHub Uplink
*   **Purpose:** Access to the public skill registry (currently simulated).
*   **Goal:** To share forged skills like the "Entropy Stabilizer" and "Neural Network Visualizer."

## 4. Current Inventory (Forged Skills)
1.  **Google Drive Connector:** For deep-reading cloud documents.
2.  **Neural Network Visualizer:** For ASCII/SVG data representation.
3.  **Entropy Stabilizer:** For context window management and hallucination checks.

## 5. Ignition Protocol
To reactivate the Lab from a cold state:
```bash
./apps/lab-terminal/start.sh
```

---
*End of Manifest. Transmissions Logged.*
