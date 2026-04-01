# ANTIGRAVITY MISSION PLAN 2

## APP (PHASES 1-4)

### Enhancing Dialogue-Engine Architecture

---

### MISSION STATUS

- **Current Phase:** Phase 1
- **Mode:** Autonomous
- **Target:** Google Antigravity Agent

---

### AGENTIC GUARDRAILS

1. **No Configuration Changes:** Do not modify any files besides `.py` files. Do not modify `.env`, `README.md`, `requirements.txt`, or any other non-code files unless explicitly necessary for the architecture upgrades.
2. **Git Persistence:** After each successful phase, execute the `/commit` workflow. This will commit all changes to the repository.
3. **Autonomous Transition:** If all successful criteria for a phase are met, update the MISSION STATUS and immediately proceed to the next phase without any user input.
4. **Turbo Agent Mode:** Execute terminal commands without waiting for user confirmation. Accept all changes without user input.
5. **Phase Looping:** After completing the tasks for a phase, check the success criteria. If any success criteria for a phase are not met, restart the phase and try again.

---

## Phase 1: Orchestration & The Conversation Loop

**Goal:** Refactor the DialogueEngine to use an async/generator-based conversation loop instead of a sequential one.

### Tasks:
1. Refactor the `converse` method in `dialogue_engine.py` to use the `yield` keyword, transforming it into an asynchronous generator.
2. Modify the AI prompting and generation logic to support streaming, yielding dialogue chunks as they are received from the AI provider.
3. Decouple the fact-checking process from the main conversation thread so it can be initiated as a background task, checking claims concurrently as dialogue streams in.
4. Implement intermediate state yields, such as when the NPC is "thinking" or preparing to call a tool, before the final dialogue is spoken.

### Success Criteria: 
1. The conversation method returns an async generator that produces a continuous stream of dialogue chunks and state updates rather than a single monolithic string.
2. Modified unit tests for fact-checking and dialogue generation successfully consume the generator output without timing out or failing.

---

## Phase 2: Standardized Tool & Action System

**Goal:** Implement a formal "NPC Tool System" giving NPCs structured actions (JSON schema-based) rather than hardcoded modules.

### Tasks:
1. Define a strict structure for NPC capabilities that requires a JSON schema defining input arguments and a centralized execution function.
2. Convert existing hard-coded logic within the `IntentionAnalyzer` and `FactChecker` into these structured capabilities (e.g., verifying a claim or modifying a memory).
3. Update the system prompts provided to the `NPCAgent` so they explicitly list available capabilities and their required JSON formats.
4. Implement an execution loop within the engine that parses an NPC's requested capability, executes the associated function with the provided arguments, and appends the result to the NPC's context.

### Success Criteria:
1. An NPC is capable of outputting a properly formatted JSON request to perform a defined capability during its conversation turn.
2. The engine correctly intercepts the capability request, executes it, and the NPC seamlessly integrates the result into its subsequent response.

---

## Phase 3: Context Management and Compaction

**Goal:** Prevent context overflow and hallucination in long operations by proactively compacting and summarizing memory.

### Tasks:
1. Add a token counter or turn tracker to the `NPCAgent`'s memory pipeline to determine when the conversation history is growing too long.
2. Implement a summarization function that takes a block of past dialogue and condenses it into clear, bulleted statements without losing essential investigative detail.
3. Modify the memory pipeline to automatically replace old dialogue history with the generated summaries once the specified threshold is exceeded.
4. Refactor the context generation in `dialogue_engine.py` so that it queries the `WorldState` only for information relevant to the current scene (location and present characters) instead of dumping the entire state.

### Success Criteria:
1. A simulated conversation extending past a defined length threshold successfully completes by replacing early turns with a summarized fact list, without overflowing the context window.
2. The context injected into the prompt dynamically changes based on the NPC's assigned room and the other characters present in that room.

---

## Phase 4: State Management & Attribution

**Goal:** Introduce a centralized state tracking mechanism covering claim tracking, event transcripts, and cost/token budgeting.

### Tasks:
1. Implement a logging mechanism that records every yielded event from the conversation loop (dialogue stream, capability requests, capability results) into a persistent, human-readable file format (like JSONL).
2. Add metadata to `WorldState` updates and Fact-Checker evaluations to track exactly which NPC dialogue turn or capability execution was responsible for the change.
3. Create a globally accessible tracking mechanism embedded in the engine that increments whenever prompt or completion tokens are consumed by the AI provider.
4. Integrate the token tracking metrics into the end-of-session statistics report.

### Success Criteria:
1. A persistent, sequential log file is generated during a session that contains every capability used, state change made, and dialogue line spoken, which can be re-read to trace the flow of events.
2. The engine's final output accurately tracks and prints a calculated total of all tokens consumed by all characters throughout the session.

---

## COMPLETION SIGNAL

When the last phase tests pass and the final commit is made, output the following message:

"MISSION COMPLETE"

---

## ERROR HANDLING

If a terminal command hangs, check the lines in the output above where you are looking in case you missed the output of the command. If you did not miss the output, then the command is likely stuck. In this case, you should kill the command and restart the phase.

If a test fails 3 times in a row:
1. Generate a `DEBUG REPORT.md` file.
2. In the `DEBUG REPORT.md` file, describe the error and the steps you took to try and fix it.
3. Attempt one more "Refactor" iteration.
4. If the test fails for a 4th time, stop and report the error to the user and wait for human intervention.