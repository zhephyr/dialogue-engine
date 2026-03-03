import pytest
from dialogue_engine import DialogueEngine
from world_state import WorldState
from npc_agent import NPCAgent
from ai_provider import MockProvider

@pytest.fixture
def engine():
    ws = WorldState()
    return DialogueEngine(world_state=ws, ai_provider=MockProvider(), enable_fact_checking=False)

def test_add_and_get_npc(engine):
    npc = NPCAgent("Alice", "Friendly")
    engine.add_npc(npc)
    
    retrieved = engine.get_npc("Alice")
    assert retrieved is not None
    assert retrieved.name == "Alice"
    assert "alice" in engine.npcs

def test_set_scene(engine):
    engine.set_scene("A sunny park")
    assert engine.current_scene == "A sunny park"

def test_converse_basic(engine):
    npc = NPCAgent("Alice", "Friendly")
    engine.add_npc(npc)
    
    response, metadata = engine.converse("Alice", "Hello there")
    
    assert "Mock AI: Please configure an AI provider" in response
    assert npc.get_recent_conversation(1)[0]["message"] == response
    assert metadata["validation_enabled"] is False

def test_converse_with_fact_checking():
    ws = WorldState()
    engine = DialogueEngine(world_state=ws, ai_provider=MockProvider(), enable_fact_checking=True)
    npc = NPCAgent("Bob", "Grumpy")
    engine.add_npc(npc)
    ws.add_location("Library")
    
    class CustomMockProvider(MockProvider):
        def generate_response(self, prompt: str) -> str:
            return "I was at the library."
            
    engine.ai_provider = CustomMockProvider()
    
    response, metadata = engine.converse("Bob", "Where were you?")
    
    assert "library" in response.lower()
    assert metadata["validation_enabled"] is True
    assert metadata["is_valid"] is True
    assert len(metadata["validation_results"]) > 0
    assert metadata["validation_results"][0]["is_valid"] is True
    assert metadata["validation_results"][0]["claim"] == "I was at the library"

def test_converse_npc_not_found(engine):
    response, metadata = engine.converse("Ghost", "Hello?")
    assert "Error" in response
    assert "error" in metadata

def test_get_npc_status(engine):
    npc = NPCAgent("Alice", "Friendly", current_location="Kitchen")
    engine.add_npc(npc)
    
    status = engine.get_npc_status("Alice")
    assert status is not None
    assert status["name"] == "Alice"
    assert status["location"] == "Kitchen"
    
def test_reset_conversation(engine):
    npc = NPCAgent("Alice", "Friendly")
    engine.add_npc(npc)
    engine.converse("Alice", "Hello")
    
    assert len(engine.get_conversation_history("Alice")) > 0
    engine.reset_conversation("Alice")
    assert len(engine.get_conversation_history("Alice")) == 0
