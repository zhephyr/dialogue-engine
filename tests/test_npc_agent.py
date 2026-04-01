from npc_agent import NPCAgent


def test_npc_agent_initialization():
    agent = NPCAgent("Bob", "Grumpy bartender")
    assert agent.name == "Bob"
    assert agent.personality == "Grumpy bartender"
    assert agent.emotional_state == "neutral"


def test_npc_memory_management():
    agent = NPCAgent("Bob", "Grumpy bartender")
    agent.add_memory("event", "Saw someone running")

    assert len(agent.memory) == 1
    assert agent.memory[0].content == "Saw someone running"
    assert agent.memory[0].type == "event"


def test_npc_conversation_tracking():
    agent = NPCAgent("Bob", "Grumpy bartender")
    agent.add_conversation_turn("Player", "Hello Bob")
    agent.add_conversation_turn("Bob", "What do you want?")

    conv = agent.get_recent_conversation(10)
    assert len(conv) == 2
    assert conv[0]["speaker"] == "Player"
    assert conv[0]["message"] == "Hello Bob"


def test_npc_fact_knowledge():
    agent = NPCAgent("Bob", "Grumpy bartender")
    agent.add_known_fact("secret_door", "in the basement")

    assert agent.knows_fact("secret_door") is True
    assert agent.knows_fact("random_thing") is False


def test_emotional_state_update():
    agent = NPCAgent("Bob", "Grumpy bartender")
    agent.update_emotional_state("angry")
    assert agent.emotional_state == "angry"


def test_get_dialogue_prompt():
    agent = NPCAgent("Bob", "Grumpy bartender")
    agent.add_known_fact("boss", "Alice")

    prompt = agent.get_dialogue_prompt("Who is your boss?", "A dark tavern")

    assert "Bob" in prompt
    assert "Grumpy bartender" in prompt
    assert "A dark tavern" in prompt
    assert "Alice" in prompt
    assert "Who is your boss?" in prompt


def test_get_fact_claim_prompt():
    agent = NPCAgent("Bob", "Grumpy bartender")
    statement = "I saw Alice at the park at 9pm."
    prompt = agent.get_fact_claim_prompt(statement)

    assert statement in prompt
    assert "extract any factual claims" in prompt.lower()
