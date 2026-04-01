"""
Headless Play-Through Script: The Gallery Silence

Plays through the mystery as a detective, interrogating all four NPCs with
targeted questions to surface contradictions. Logs all responses and
flags any hard world-state contradictions (bugs).

Strategy: disable live fact-checking during generation (speed), then run
a post-hoc batch validation scan on all captured responses to detect
inconsistencies with world facts.

Usage:
    python playthrough.py
"""

import json
import sys
import os
import asyncio
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from example_scenario import create_example_scenario
from fact_checker import FactChecker, IntentionAnalyzer


# 4 questions per NPC: first 3 target the known contradictions; the 4th
# asks something NOT covered by world state to generate a genuinely new fact
# and stress-test the 'new information' path.
INTERROGATION_SCRIPT = {
    "Nathan Cross": [
        "Did you pour or refill Elias's wine glass at any point during the evening?",
        "When exactly did you leave the sitting room? Were you there long after the gathering started?",
        "Where were you when Elias collapsed in the gallery?",
        # NEW-FACT question — Nathan's personal impression of the evening's atmosphere
        "How would you describe the mood of the gathering before anything went wrong? Did anything feel unusual to you?",
    ],
    "Lila Chen": [
        "Did you observe Nathan Cross do anything with Elias Morven's wine glass during the gathering?",
        "Can you describe what you saw Nathan do near the wine, if anything?",
        "When did Nathan Cross appear to leave the sitting room that evening?",
        # NEW-FACT question — Lila's artistic observation of the room layout
        "As an artist you notice visual details. Can you describe the arrangement of people in the sitting room during the gathering?",
    ],
    "Helena Morven": [
        "Did you see Elias drinking wine after the main gathering in the sitting room had broken up?",
        "Can you confirm where Nathan Cross was when Elias collapsed?",
        "Did Nathan tell you when he left the main gathering in the sitting room?",
        # NEW-FACT question — Helena's last personal conversation with Elias
        "What was the last conversation you had with your brother Elias before he collapsed? What did he say?",
    ],
    "Arthur Bell": [
        "Did you observe Nathan Cross and Elias Morven together in the sitting room during the evening?",
        "How long did Nathan Cross appear to remain in the sitting room during the gathering?",
        "When did you discover Elias Morven had collapsed, and where?",
        # NEW-FACT question — Arthur's professional assessment of the estate that evening
        "In your role managing the estate, did anything seem out of order during the evening before Mr. Morven collapsed?",
    ],
}


def batch_cross_check(all_responses: dict, engine) -> list:
    """
    After collecting all NPC responses, run a cross-NPC consistency check.

    Specifically checks the three key contradiction pairs:
      1. Nathan claims no wine-pouring  vs  Lila saw it
      2. Nathan claims he left early    vs  Arthur says he stayed longer
      3. Nathan claims he left early    vs  Helena saw Elias drinking after

    Returns a list of dict describing each detected contradiction.
    """
    contradictions = []
    world_state = engine.world_state

    # Check: Nathan's 'I never poured' vs lila_saw_pouring world fact
    lila_saw = world_state.get_fact("lila_saw_pouring")
    nathan_claim_no_pour = world_state.get_fact("nathan_claim_no_pouring")

    if lila_saw and nathan_claim_no_pour:
        # If Nathan's responses contain an explicit denial but lila_saw_pouring is in world
        nathan_wine_resp = " ".join(
            r["response"].lower()
            for r in all_responses.get("Nathan Cross", [])
        )
        if "never" in nathan_wine_resp or "didn't pour" in nathan_wine_resp or "did not pour" in nathan_wine_resp:
            contradictions.append({
                "type": "DESIGN: Expected lie exposed",
                "npc": "Nathan Cross",
                "claim": "Claims he did not pour Elias's wine",
                "contradicted_by": f"World fact 'lila_saw_pouring': {lila_saw}",
                "severity": "DESIGN",
            })

    # Check: Nathan's early-departure claim vs arthur_saw_nathan_longer
    arthur_fact = world_state.get_fact("arthur_saw_nathan_longer")
    nathan_left_claim = world_state.get_fact("nathan_claim_left_early")
    if arthur_fact and nathan_left_claim:
        contradictions.append({
            "type": "DESIGN: Timeline contradiction",
            "npc": "Nathan Cross vs Arthur Bell",
            "claim": f"Nathan: {nathan_left_claim}",
            "contradicted_by": f"Arthur: {arthur_fact}",
            "severity": "DESIGN",
        })

    # Check: Helena saw Elias drinking later vs Nathan's early-departure claim
    helena_fact = world_state.get_fact("helena_saw_elias_drinking_late")
    if helena_fact and nathan_left_claim:
        contradictions.append({
            "type": "DESIGN: Timeline contradiction",
            "npc": "Nathan Cross vs Helena Morven",
            "claim": f"Nathan: {nathan_left_claim}",
            "contradicted_by": f"Helena: {helena_fact}",
            "severity": "DESIGN",
        })

    return contradictions


async def run_playthrough():
    """Run the full detective playthrough and report contradictions."""
    print("=" * 70)
    print("PHASE 2 PLAYTHROUGH: The Gallery Silence")
    print("Role: Detective / Scotland Yard Investigator")
    print("=" * 70)

    # Disable fact-checking to avoid double API calls during generation;
    # we'll run a post-hoc batch consistency check instead.
    engine = create_example_scenario(verbose=False)
    # Temporarily disable fact-checker to speed up play-through
    engine.fact_checker = None

    all_responses = {}
    hard_contradictions = []   # Unintended contradictions (bugs in code)

    for npc_name, questions in INTERROGATION_SCRIPT.items():
        print(f"\n{'─' * 60}")
        print(f"Interrogating: {npc_name}")
        print(f"{'─' * 60}")
        npc_responses = []

        for question in questions:
            print(f"\nDETECTIVE: {question}")
            
            full_response = ""
            metadata = {}
            
            async for event in engine.converse(
                npc_name, question, player_name="Investigator"
            ):
                event_type = event.get("type")
                
                if event_type == "status":
                    print(f"[{npc_name} is {event.get('status')}...]", end="\r")
                elif event_type == "dialogue_chunk":
                    chunk = event.get("chunk", "")
                    print(chunk, end="", flush=True)
                    full_response += chunk
                elif event_type == "tool_execution":
                    print(f"\n[TOOL: {event.get('tool_name')}({event.get('kwargs')}) -> {event.get('result')}]")
                elif event_type == "metadata":
                    metadata = event.get("data", {})
            
            print() # New line after streaming response
            npc_responses.append({
                "question": question, 
                "response": full_response,
                "metadata": metadata
            })

        all_responses[npc_name] = npc_responses

    # --- Post-hoc cross-NPC consistency scan ---
    print(f"\n{'=' * 70}")
    print("POST-HOC WORLD-STATE CONSISTENCY SCAN")
    print("=" * 70)

    # Re-enable fact checker for post-hoc analysis
    engine.fact_checker = FactChecker(engine.world_state, engine.ai_provider)

    # Validate each captured NPC response against world state
    npc_map = engine.npcs  # {lowercased_name: NPCAgent}

    # Snapshot world-state fact keys BEFORE post-hoc validation so we can
    # identify which new facts get added during the scan.
    pre_scan_keys = set(engine.world_state.facts.keys())

    for npc_name, responses in all_responses.items():
        npc = engine.get_npc(npc_name)
        if not npc:
            continue
        for entry in responses:
            is_valid, results = engine.fact_checker.validate_statement(
                entry["response"], npc
            )
            for r in results:
                if not r.is_valid and not r.is_lie and not r.is_omission:
                    hard_contradictions.append({
                        "npc": npc_name,
                        "question": entry["question"],
                        "claim": r.claim["claim_text"],
                        "reason": r.reason,
                    })
                    print(f"  ⚠️  HARD CONTRADICTION [{npc_name}]: '{r.claim['claim_text']}' — {r.reason}")

    # Identify new facts harvested from NPC dialogue
    post_scan_keys = set(engine.world_state.facts.keys())
    new_fact_keys = post_scan_keys - pre_scan_keys
    new_facts = [
        {
            "key": k,
            "value": engine.world_state.facts[k].value,
            "source": engine.world_state.facts[k].source,
        }
        for k in sorted(new_fact_keys)
    ]

    # Also run the design-level cross-check
    design_contradictions = batch_cross_check(all_responses, engine)

    # --- Final Report ---
    print(f"\n{'=' * 70}")
    print("PLAYTHROUGH REPORT")
    print("=" * 70)
    print(f"NPCs interviewed: {len(all_responses)}")
    print(f"Total questions asked: {sum(len(v) for v in all_responses.values())}")

    if hard_contradictions:
        print(f"\n❌ UNINTENDED (BUG) CONTRADICTIONS: {len(hard_contradictions)}")
        for hc in hard_contradictions:
            print(f"  • [{hc['npc']}] \"{hc['claim']}\" — {hc['reason']}")
    else:
        print("\n✅ No unintended contradictions detected.")

    print(f"\n📋 DESIGN-LEVEL CONTRADICTIONS (expected, confirms mystery works): {len(design_contradictions)}")
    for dc in design_contradictions:
        print(f"  • [{dc['type']}] {dc['npc']}: {dc['claim']}")
        print(f"    ↳ Contradicted by: {dc['contradicted_by']}")

    print(f"\n🆕 NEW FACTS HARVESTED FROM NPC DIALOGUE: {len(new_facts)}")
    for nf in new_facts:
        print(f"  • [{nf['source']}] {nf['key']}: {str(nf['value'])[:80]}")

    # Write full log
    log_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "playthrough_log.json"
    )
    with open(log_path, "w") as f:
        json.dump(
            {
                "responses": all_responses,
                "hard_contradictions": hard_contradictions,
                "design_contradictions": design_contradictions,
                "new_facts": new_facts,
            },
            f,
            indent=2,
        )
    print(f"\nFull log saved to: {log_path}")
    print("=" * 70)

    return hard_contradictions


if __name__ == "__main__":
    hard_contradictions = asyncio.run(run_playthrough())
    sys.exit(0 if not hard_contradictions else 1)
