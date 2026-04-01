# Analysis: Applying Claude-Code Patterns to Dialogue-Engine

This document analyzes the architecture and processes of the `claude-code` project and identifies key patterns that could significantly enhance the `dialogue-engine` project.

## 1. Orchestration & The Conversation Loop

### Claude-Code Pattern: Generator-based `query()` Loop
In `claude-code/src/query.ts`, the main conversation logic is implemented as an async generator. This allows it to:
- Yield granular events (streamed content, tool results, usage stats) back to the caller in real-time.
- Maintain a structured `State` object across multiple turns of "thinking" and "tool use".
- Handle interruptions and errors gracefully at each step of the loop.

### Improvement for Dialogue-Engine:
Currently, `dialogue_engine.py` uses a standard sequential `converse()` method. If NPCs need to perform multi-step reasoning (e.g., "Think about the lie" -> "Check the timeline" -> "Formulate response"), refactoring the `DialogueEngine` to use a generator-based loop would allow:
- **Streaming Responses**: Delivering NPC dialogue character-by-character.
- **Background Checks**: Performing fact-checks *while* the NPC is still "thinking", potentially yielding "internal monologue" or "hesitation" cues.

---

## 2. Standardized Tool & Action System

### Claude-Code Pattern: The `Tool` Interface
Every capability in `claude-code` (bash, file read, grep) is a discrete entry in `src/tools/` following a strict interface:
- **`inputSchema`**: A JSON schema ensuring the LLM calls the tool correctly.
- **`call()`**: The actual execution logic, isolated from the core engine.
- **`permission`**: Integration with a central permission system.

### Improvement for Dialogue-Engine:
The `IntentionAnalyzer` and `FactChecker` in `dialogue-engine` are currently hardcoded modules. Implementing a "NPC Tool System" would allow NPCs to perform actions like:
- `search_room(location)`
- `recall_memory(topic)`
- `whisper_to(character, message)`
- `consult_timeline(person, time)`

By giving NPCs a set of tools with clear schemas, they can interact with the game world in a more structured, agentic way.

---

## 3. Context Management and Compaction

### Claude-Code Pattern: Proactive Compaction
Claude-Code uses `autocompact.ts` and `microcompact.ts` to manage the context window. When the conversation history grows too large, it automatically:
1. Summarizes earlier parts of the conversation.
2. Collapses redundant tool results.
3. Maintains a "System Context" (environment info, git status) that is appended to every query.

### Improvement for Dialogue-Engine:
As murder mystery investigations get long, NPCs may exceed context limits or begin to hallucinate history. Implementing a similar strategy would involve:
- **Memory Summarization**: Periodically summarizing old dialogue into the NPC's "Known Facts".
- **Dynamic Context Building**: Instead of passing the entire `WorldState`, generate a "Scene Context" based on the current location and involved characters (similar to Claude-Code's `context.ts`).

---

## 4. State Management & Attribution

### Claude-Code Pattern: Centralized AppState
`claude-code` uses a central `AppState.tsx` (Zustand-style) and specialized stores for `QueryEngine` to track:
- Precisely which tool call caused which change.
- A "Transcript" of every event that can be resumed (`/resume`).
- Token usage and costs per turn.

### Improvement for Dialogue-Engine:
`dialogue-engine` could benefit from an "Evidence & Attribution" system:
- **Claim Tracking**: Use `claude-code`'s `recordTranscript` pattern to save every claim made by every NPC to a persistent log.
- **Cost/Token Budgeting**: Track usage per NPC to prevent runaway costs during long investigations.

---

## 5. Terminal UI & Developer Experience

### Claude-Code Pattern: Ink-based REPL
One of the most impressive parts of `claude-code` is its terminal UI (`src/screens/REPL.tsx`), which uses React/Ink to render:
- Color-coded diffs.
- Progress bars for tool execution.
- Rich interactive prompts for permissions.

### Improvement for Dialogue-Engine:
The `console_interface.py` could be transformed from a basic text prompt into a rich "Investigator's Dashboard" using Python libraries like **Textual** or **Rich**:
- **Timeline Visualization**: Real-time Gantt charts of where everyone was.
- **Consistency Warnings**: Visual indicators (red/green) next to NPC claims as the `FactChecker` validates them.
- **Fact Cards**: Interactive summaries of what the player has learned so far.

---

## Summary of Architectural Recommendations

| Feature Area | Claude-Code Inspiration | Dialogue-Engine Path |
| :--- | :--- | :--- |
| **Logic** | Async Generators / State Machines | Refactor `converse()` into a turn generator. |
| **Actions** | JSON-Schema Tool Registry | Define `CharacterActions` as tools. |
| **Memory** | Compaction & Summarization | Implement `NPCMemoryCompactor`. |
| **UI** | Ink / Component-based UI | Use `Rich` / `Textual` for the console. |
| **Process** | `CLAUDE.md` / Policy Checks | Formalize "NPC Guidelines" as a system prompt generator. |
