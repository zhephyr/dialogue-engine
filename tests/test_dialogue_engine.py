"""
Tests for the DialogueEngine module.

This module tests the main engine's NPC management, scene control, conversation
orchestration, and fact-checking integration — all using MockProvider to avoid
real API calls.
"""

import pytest
from dialogue_engine import DialogueEngine
from world_state import WorldState
from npc_agent import NPCAgent
from ai_provider import MockProvider


# --- Fixtures ---


@pytest.fixture
def engine():
    """Create a DialogueEngine using a MockProvider with fact-checking disabled."""
    ws = WorldState()
    return DialogueEngine(
        world_state=ws, ai_provider=MockProvider(), enable_fact_checking=False
    )


# --- NPC Management Tests ---


def test_add_and_get_npc(engine):
    """Adding an NPC should register it under its lowercase name for case-insensitive lookup."""
    npc = NPCAgent("Alice", "Friendly")
    engine.add_npc(npc)

    retrieved = engine.get_npc("Alice")
    assert retrieved is not None
    assert retrieved.name == "Alice"
    # Internal storage uses lowercase key
    assert "alice" in engine.npcs


def test_set_scene(engine):
    """Setting the scene should update the engine's current_scene property."""
    engine.set_scene("A sunny park")
    assert engine.current_scene == "A sunny park"


# --- Conversation Tests ---


@pytest.mark.asyncio
async def test_converse_basic(engine):
    """
    Basic conversation should:
    - Yield a mock response from the AI provider in chunks
    - Record the response in the NPC's conversation history
    - Yield metadata indicating validation is disabled
    """
    npc = NPCAgent("Alice", "Friendly")
    engine.add_npc(npc)

    chunks = []
    metadata = {}
    async for event in engine.converse("Alice", "Hello there"):
        if event["type"] == "dialogue_chunk":
            chunks.append(event["chunk"])
        elif event["type"] == "metadata":
            metadata.update(event["data"])

    response = "".join(chunks)

    # MockProvider returns a canned response containing this string
    assert "Mock AI: Please configure an AI provider" in response
    # Last entry in conversation history should match the NPC response
    assert npc.get_recent_conversation(1)[0]["message"] == response
    assert metadata["validation_enabled"] is False


@pytest.mark.asyncio
async def test_converse_with_fact_checking():
    """
    With fact-checking enabled, the engine should:
    - Validate the NPC's response against world state
    - Yield validation_results in the metadata
    - Correctly identify a true location claim as valid
    """
    ws = WorldState()
    engine = DialogueEngine(
        world_state=ws, ai_provider=MockProvider(), enable_fact_checking=True
    )
    npc = NPCAgent("Bob", "Grumpy")
    engine.add_npc(npc)
    # Register the location so the claim validates as true
    ws.add_location("Library")

    # Override the AI provider so the response contains a verifiable location claim
    class CustomMockProvider(MockProvider):
        async def generate_response_stream(self, prompt: str):
            yield "I was at the library."

    engine.ai_provider = CustomMockProvider()

    chunks = []
    metadata = {}
    async for event in engine.converse("Bob", "Where were you?"):
        if event["type"] == "dialogue_chunk":
            chunks.append(event["chunk"])
        elif event["type"] == "metadata":
            metadata.update(event["data"])

    response = "".join(chunks)

    assert "library" in response.lower()
    assert metadata["validation_enabled"] is True
    assert metadata["is_valid"] is True
    assert len(metadata["validation_results"]) > 0
    assert metadata["validation_results"][0]["is_valid"] is True
    # Claim text should match extracted claim (without trailing period)
    assert metadata["validation_results"][0]["claim"] == "I was at the library"


@pytest.mark.asyncio
async def test_converse_npc_not_found(engine):
    """Conversing with a non-existent NPC should yield an error response and metadata."""
    chunks = []
    metadata = {}
    async for event in engine.converse("Ghost", "Hello?"):
        if event["type"] == "dialogue_chunk":
            chunks.append(event["chunk"])
        elif event["type"] == "metadata":
            metadata.update(event["data"])

    response = "".join(chunks)
    assert "Error" in response
    assert "error" in metadata


# --- Status & History Tests ---


def test_get_npc_status(engine):
    """NPC status should include name, location, and other tracked attributes."""
    npc = NPCAgent("Alice", "Friendly", current_location="Kitchen")
    engine.add_npc(npc)

    status = engine.get_npc_status("Alice")
    assert status is not None
    assert status["name"] == "Alice"
    assert status["location"] == "Kitchen"


@pytest.mark.asyncio
async def test_reset_conversation(engine):
    """Resetting a conversation should clear all recorded turns for the NPC."""
    npc = NPCAgent("Alice", "Friendly")
    engine.add_npc(npc)
    # Establish at least one turn
    async for _ in engine.converse("Alice", "Hello"):
        pass

    assert len(engine.get_conversation_history("Alice")) > 0
    engine.reset_conversation("Alice")
    assert len(engine.get_conversation_history("Alice")) == 0
