import pytest
import os
import json
from dialogue_engine import DialogueEngine
from world_state import WorldState
from ai_provider import MockProvider
from npc_agent import NPCAgent

@pytest.mark.asyncio
async def test_engine_state_and_token_tracking(tmp_path):
    """
    Test that the engine logs all yielded events to a JSONL file,
    and that token usage is tracked globally and reported.
    """
    log_file = tmp_path / "session_transcript.jsonl"
    
    ws = WorldState()
    engine = DialogueEngine(world_state=ws, ai_provider=MockProvider(), log_file=str(log_file))
    agent = NPCAgent("Alice", "Polite")
    engine.add_npc(agent)
    
    # We speak to Alice. Mock provider yields some chunks.
    # The MockProvider doesn't actually cost tokens natively, but engine should
    # track generic "tokens" if the provider reports them, or provider can simulate it.
    
    class TokenMockProvider(MockProvider):
        async def generate_response_stream(self, prompt: str):
            self.total_prompt_tokens = getattr(self, "total_prompt_tokens", 0) + len(prompt) // 4
            self.total_completion_tokens = getattr(self, "total_completion_tokens", 0) + 5

            if "Continue your response" not in prompt:
                yield '<tool>{"capability": "CheckFact", "kwargs": {"topic": "test"}}</tool>'
            else:
                yield " Here is my dialogue chunk response."
            
        def get_token_usage(self):
            return {
                "prompt_tokens": getattr(self, "total_prompt_tokens", 0),
                "completion_tokens": getattr(self, "total_completion_tokens", 0)
            }
            
    engine.ai_provider = TokenMockProvider()
    
    async for event in engine.converse("Alice", "Hello?"):
        pass

    assert engine.ai_provider.get_token_usage()["completion_tokens"] > 0
    
    stats = engine.get_engine_stats()
    assert "token_usage" in stats
    assert stats["token_usage"]["completion_tokens"] > 0
    
    # Check JSONL transcript
    assert os.path.exists(log_file)
    with open(log_file, "r") as f:
        lines = f.readlines()
        
    assert len(lines) > 0
    # There should be events for tool execution and dialogue chunks
    types = [json.loads(l).get("type") for l in lines]
    assert "dialogue_chunk" in types
    assert "tool_execution" in types
