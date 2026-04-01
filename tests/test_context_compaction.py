import pytest
from npc_agent import NPCAgent


@pytest.mark.asyncio
async def test_agent_compacts_memory():
    """
    When NPCAgent hits max dialogue turns, it should condense the oldest turns
    into a summary and remove the raw dialogue entries to save tokens.
    """
    from dialogue_engine import DialogueEngine
    from world_state import WorldState
    from ai_provider import MockProvider

    ws = WorldState()
    engine = DialogueEngine(world_state=ws, ai_provider=MockProvider())
    agent = NPCAgent("Bob", "Skeptical")
    engine.add_npc(agent)

    # Simulate adding manually, then triggering compaction
    for i in range(20):
        agent.add_conversation_turn("Player", f"Question {i}")
        agent.add_conversation_turn("Bob", f"Answer {i}")

    # Trigger compaction manually for test synchronously
    await engine.compact_conversation_if_needed(agent)

    # max allowed turns before compaction is e.g. 15, we condense 10 down to 1 summary.
    assert (
        len(agent.conversation_history) <= 35
    )  # actually we expect it to drop by at least 10 items.

    summaries = [m for m in agent.memory if m.type == "dialogue_summary"]
    assert len(summaries) > 0
