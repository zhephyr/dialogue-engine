# Murder Mystery Dialogue Engine

A drop-in dialogue engine that uses AI agents to represent NPCs in a murder mystery game. Supports free-form conversations with fact-checking against a world state. Created completely with AI (Claude Sonnet 4.5 mainly).

## Features

- **AI-Powered NPCs**: Each NPC is an intelligent agent with personality, goals, fears, and relationships
- **Fact-Checking**: Claims made by NPCs are validated against the world state
- **Memory System**: NPCs track their lies, omissions, and conversation history
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

The project includes "The Harrow Estate Incident" - a complete murder mystery scenario for testing and demonstration.

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
/talk Edmund Vale

# Ask questions
Where were you during the evening?
Did you see anyone near the study?

# Check NPC status and lies
/status Edmund Vale
/lies Edmund Vale

# View conversation history
/history Edmund Vale

# Get world state information
/world

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

# Create NPC
butler = NPCAgent(
    name="James the Butler",
    personality="Formal, observant, loyal",
    goals=["Protect the family reputation"],
    fears=["Being blamed for the murder"],
    secrets=["Saw the murderer enter the library"]
)

# Initialize engine
engine = DialogueEngine(world)
engine.add_npc(butler)

# Start conversation
response = engine.converse("butler", "Where were you last night?")
print(response)
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
