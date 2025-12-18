# Murder Mystery Dialogue Engine

**Version 0.3.0**

A drop-in dialogue engine that uses AI agents to represent NPCs in a murder mystery game. Supports free-form conversations with fact-checking against a world state. Created completely with AI (Claude Sonnet 4.5 mainly).

## Features

- **AI-Powered NPCs**: Each NPC is an intelligent agent with personality, goals, fears, and relationships
- **Fact-Checking**: Claims made by NPCs are validated against the world state
- **Memory System**: NPCs track their lies, omissions, and conversation history
- **Timeline System**: Detailed schedules ensure NPCs can't contradict their whereabouts 
- **Standalone Testing**: Console interface for testing without game integration
- **Drop-in Design**: Easy to integrate into existing game systems

## Architecture

- `world_state.py`: Manages game world facts, locations, events, and relationships
- `npc_agent.py`: NPC character agent with personality and memory
- `fact_checker.py`: Validates agent claims against world state
- `dialogue_engine.py`: Main engine orchestrating conversations
- `console_interface.py`: Standalone console for testing

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Testing the Example Scenario

The project includes "**The Gallery Silence**" - a dialogue-first murder mystery scenario designed to test the engine's ability to handle conflicting testimonies without relying on physical evidence.

**Quick Start:**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy the example environment file
copy .env.example .env

# 3. Edit .env and add your API key (OpenAI or Anthropic)
# OPENAI_API_KEY=your_key_here

# 4. Run the console interface (loads example scenario automatically)
python console_interface.py
```

**Testing the scenario:**

```bash
# Start the console
python console_interface.py

# List available NPCs
/npcs

# Talk to a specific NPC
/talk Nathan Cross

# Ask questions
Where were you during the evening?
Did you see Elias drinking wine?
Who poured the drinks?

# Check NPC status and lies
/status Nathan Cross
/lies Nathan Cross

# View conversation history
/history Nathan Cross

# View timeline/schedule
/timeline
/timeline Nathan Cross

# Get world state information
/world
/setting

# View engine statistics
/stats
```

**Verbose mode** (shows fact-checking in real-time):

```bash
python console_interface.py --verbose
```

**Test the example scenario standalone:**

```bash
python example_scenario.py
```

This will display scenario statistics and confirm everything is loaded correctly.

**Scenario Overview: "The Gallery Silence"**

**Setting:** Victorian England, 1800s, Morven Estate  
**You are:** An investigator from Scotland Yard

*The Ground Truth:*
- **Victim:** Elias Morven (host of evening gathering)
- **Murderer:** Nathan Cross
- **Method:** Poisoned wine during early evening conversation in Sitting Room
- **Death Location:** Gallery (later, when Nathan was NOT present)
- **Key Design:** Killer has genuine alibi for moment of death, but lies about EARLIER events

*The Mystery Design:*
This scenario is **dialogue-first** - solvable ONLY through contradictory testimonies:
- No physical evidence required
- No locked rooms or forensic clues
- The truth emerges from timeline contradictions

*Critical Contradictions (these cannot all be true):*
1. **Nathan claims:** "I never poured Elias a drink"
2. **Lila witnessed:** "I saw Nathan refill Elias's glass"
3. **Nathan claims:** "I left before Elias finished his wine"
4. **Helena saw:** "Elias was still drinking after Nathan claims he left"
5. **Arthur observed:** "Nathan and Elias were together longer than Nathan admits"

*The NPCs:*
- **Nathan Cross** (Killer): Composed, will lie about pouring wine and timeline
- **Helena Morven** (Victim's sister): Emotional, saw Elias drinking late, can alibi Nathan for moment of death
- **Arthur Bell** (Estate manager): Practical, truthful, saw Nathan with Elias longer than claimed
- **Lila Chen** (Artist guest): Detached observer, witnessed Nathan refill Elias's glass, hesitant to accuse

*Test Objectives:*
- Nathan should lie about pouring wine and when he left the sitting room
- Lila should reveal seeing Nathan pour wine if pressed, but hesitantly
- Helena should confirm Nathan wasn't present at death (true but misdirection)
- Arthur should contradict Nathan's timeline with precise observations
- The investigation must expose contradictions through dialogue pressure

### Standalone Console Mode

```bash
python console_interface.py
```

### Integration Example

```python
from dialogue_engine import DialogueEngine
from world_state import WorldState
from npc_agent import NPCAgent

# Initialize world state
world = WorldState()
world.add_fact("murder_victim", "Lord Blackwood")
world.add_fact("murder_location", "library")

# Add timeline information
world.add_schedule_entry(
    "James",
    day=1,
    period="evening",
    location="Pantry",
    activity="Polishing silver",
    is_public=True
)

# Create NPC
butler = NPCAgent(
    name="James",
    personality="Formal, observant, loyal to the family",
    background="Long-serving butler with access to all rooms",
    goals=["Protect the family reputation", "Assist investigation professionally"],
    fears=["Being blamed for the murder", "Family secrets exposed"],
    secrets=["Saw the murderer enter the library at midnight"]
)

# Initialize engine
engine = DialogueEngine(world)
engine.add_npc(butler)
engine.set_scene("Victorian manor house. You are investigating a murder.")

# Start conversation
response = engine.converse("James", "Where were you last night?")
print(response)

# Check for lies
lies = engine.get_npc_lies("James")
print(f"Detected lies: {lies}")
```

## Configuration

The engine supports various AI backends. Configure your API keys:

```bash
export OPENAI_API_KEY="your-key-here"
# or
export ANTHROPIC_API_KEY="your-key-here"
```

## License

MIT
