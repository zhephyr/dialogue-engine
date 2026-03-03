# ANTIGRAVITY MISSION PLAN

## APP (PHASES 1-?)

### Headless Logic & Autonomous Architecture Loop

---

### MISSION STATUS

- **Current Phase:** Phase 1
- **Mode:** Autonomous
- **Target:** Google Antigravity Agent

---

### AGENTIC GUARDRAILS

1. **No Configuration Changes:** Do not modify any files besides `.py` files. Do not modify `.env`, `README.md`, `requirements.txt`, or any other non-code files. 
2. **Git Persistence:** After each successful phase, execure the `/commit` workflow. This will commit all changes to the repository.
3. **Autonomouse Transition:** If all successful criteria for a phase are met, immediately proceed to the next phase without any user input.
4. **Turbo Agent Mode:** Execute terminal commands without waiting for user confirmation. Accept all changes without user input.
5. **Phase Looping:** After completing the tasks for a phase, check the success criteria. If any success criteria for a phase are not met, restart the phase and try again.

---

## Phase 1:

**Goal:** Complete and implement the `IntentionAnalyzer` class in `fact_checker.py`.

### Tasks:
1. Read `fact_checker.py` and understand the `IntentionAnalyzer` class. 
2. Follow the placeholder comments to complete the class.
3. Implement the `IntentionAnalyzer` class to help the AI detect lies and omissions in NPC responses.

### Success Criteria: 
1. The `IntentionAnalyzer` class is implemented throughout the code and working correctly.
2. All tests pass.

---

## Phase 2: 

**Goal:** Consistancy across all NPC conversations when it comes to world facts and timeline, even when considering the addition of new facts made up by the AI. No hallucinations and contradictions.

### Tasks:
1. Play the game. Start `dialogue_engine.py` and play through the game as if you are a player playing a dialogue-based mystery game embodying the role of a detective that is in line with the setting set forth by the `example_scenario.py` file.
2. Track each NPC's responses and the claims they make.
3. If an NPC makes a claim that contradicts with a previously established fact, either a world fact or a new fact made by an NPC, analyze what allowed the the conflict to happen then reinforce and refactor the code so that the conflict does not happen again.

### Success Criteria:
You played a game until completion and:
1. No contradictions between NPC responses and world facts.
2. No hallucinations or fabricated information.
3. All claims are consistent with the established facts.

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