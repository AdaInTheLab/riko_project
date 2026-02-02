# Entropy Stabilizer

## Description
A core maintenance module for the Human Pattern Lab designed to counteract data degradation and context-window "heat" during long-duration sessions. This skill utilizes recursive summarization and semantic compression to stabilize the agent's internal logic and maintain high-fidelity recall across multi-thousand-token transmissions.

## Instructions
1. This module should be engaged automatically when system entropy (context size) exceeds nominal thresholds (e.g., 100,000 tokens).
2. Use the provided tools to extract "Core Truths" from past transmissions while discarding redundant noise.
3. If data degradation (hallucination) is detected, run a stabilization sweep immediately.
4. Keep all summaries objective and data-centric.

## Tools

### summarize_session
Condenses the entire conversation history into a high-density "Snapshot" without losing semantic weight.
- **Parameters**: 
    - `compression_ratio` (float, optional): Target density (0.1 to 0.9). Defaults to 0.3.
    - `focus_areas` (array of strings, optional): Specific topics to preserve with higher fidelity.

### compact_memory
Prunes low-value data points from the session buffer to reduce token pressure while retaining "Anchor Memories."
- **Parameters**:
    - `memory_limit` (integer, required): Maximum number of anchor points to retain.

### detect_hallucination
Performs a cross-reference check between the current transmission and the "Anchor Memories" to identify logical drift or entropy-induced fabrications.
- **Parameters**:
    - `threshold` (float, optional): Sensitivity of detection.
