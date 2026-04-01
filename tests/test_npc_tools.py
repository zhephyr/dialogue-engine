import pytest
import json
from world_state import WorldState
from npc_agent import NPCAgent
from dialogue_engine import DialogueEngine
from ai_provider import MockProvider


@pytest.mark.asyncio
async def test_engine_executes_tool_request():
    """
    When the AIProvider generates a JSON capability request,
    the DialogueEngine should intercept it, execute the mapped function,
    and update the NPC context seamlessly.
    """
    ws = WorldState()
    engine = DialogueEngine(world_state=ws, ai_provider=MockProvider())
    npc = NPCAgent("Alice", "Friendly")
    engine.add_npc(npc)

    class ToolRequestingMockProvider(MockProvider):
        async def generate_response_stream(self, prompt: str):
            if "[System: Tool" in prompt:
                # We already requested the tool and got a response
                yield "Yes, now I recall."
            else:
                # First pass: request tool
                yield "Wait, let me recall something.\n"
                yield (
                    "<tool>"
                    + json.dumps(
                        {
                            "capability": "CheckFact",
                            "kwargs": {"topic": "The murder weapon"},
                        }
                    )
                    + "</tool>"
                )

    engine.ai_provider = ToolRequestingMockProvider()

    chunks = []
    metadata = {}
    tool_events = []

    async for event in engine.converse("Alice", "Do you remember the weapon?"):
        if event["type"] == "dialogue_chunk":
            chunks.append(event["chunk"])
        elif event["type"] == "metadata":
            metadata.update(event["data"])
        elif event["type"] == "tool_execution":
            tool_events.append(event)

    response = "".join(chunks)

    # We expect the tool JSON string to NOT be shown raw to the user (i.e. stripped from final dialogue)
    assert "{" not in response
    assert "CheckFact" not in response
    assert len(tool_events) == 1
    assert tool_events[0]["tool_name"] == "CheckFact"
    assert "The murder weapon" in str(tool_events[0]["result"])
