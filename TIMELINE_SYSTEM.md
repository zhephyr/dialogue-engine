# Timeline System - Implementation Summary

## Overview

Implemented an explicit timeline/schedule system to eliminate inconsistencies in NPC claims about times and locations.

## Key Components Added

### 1. World State Enhancements (`world_state.py`)

**New Classes:**
- `TimeBlock`: Represents a specific time period (day + period)
  - Supports: early_morning, morning, noon, afternoon, evening, late_night, overnight
  - Designed for multi-day scenarios

- `NPCScheduleEntry`: Tracks what an NPC was doing during a specific time block
  - Location
  - Activity
  - Who they were with
  - Witnesses
  - Public/private visibility
  - Notes

**New Methods:**
- `add_schedule_entry()`: Add a schedule entry for an NPC
- `get_character_schedule()`: Get all schedule entries for a character
- `get_character_location_at_time()`: Get where a character was at a specific time
- `get_characters_at_location_time()`: Find all characters at a location during a time
- `verify_character_claim_time_location()`: Validate location claims against schedule

### 2. NPC Agent Updates (`npc_agent.py`)

**Updated `get_dialogue_prompt()`:**
- Now accepts optional `character_knowledge` parameter
- Includes schedule in the prompt
- Explicitly instructs AI to:
  - Only reference times/locations from their schedule
  - Be specific about times when asked
  - Say they don't recall if asked about unlisted times

### 3. Dialogue Engine Updates (`dialogue_engine.py`)

- Now exports full character knowledge (including schedule) before generating prompts
- Passes schedule information to NPC dialogue generation

### 4. Console Interface (`console_interface.py`)

**New Command: `/timeline [npc]`**
- Without argument: Shows complete timeline for all characters side-by-side
- With NPC name: Shows detailed schedule for that specific NPC
- Displays private notes for debugging purposes

### 5. Example Scenario Updates (`example_scenario.py`)

**Explicit Day 1 Timeline:**
- **Afternoon**: All NPCs have defined locations and activities
- **Evening** (Dinner): Public event, all present, argument witnessed
- **Late Night**: Critical period where murder occurs
  - Edmund alone with Lord Harrow in Study (murder)
  - Clara and Dr. Liu together in Library (alibis)
  - Marian alone in Kitchen (no alibi)
- **Overnight**: Body discovery and alarm

**Each entry includes:**
- Exact location
- Specific activity
- Who else was present
- Witnesses who can verify
- Notes for context

## Benefits

1. **Consistency**: NPCs can only claim to be in locations explicitly listed in their schedule
2. **Verification**: Fact-checker can validate time/location claims against the schedule
3. **Alibi Tracking**: Easy to see who was with whom and when
4. **Scalability**: System designed for multi-day investigations (though MVP uses only Day 1)
5. **Clarity**: Removes ambiguity about "evening", "dinner", "night" etc.

## Time Periods Defined

- `early_morning`: Dawn, very early hours
- `morning`: Morning hours
- `noon`: Midday
- `afternoon`: After noon, pre-dinner
- `evening`: Dinner time and early evening
- `late_night`: Late evening into night (murder period in MVP)
- `overnight`: Night hours, very late

## Usage Examples

### For Developers:
```python
# Add a schedule entry
world.add_schedule_entry(
    character="Edmund Vale",
    day=1,
    period="evening",
    location="Dining Room",
    activity="Attending dinner",
    with_characters=["Lord Harrow", "Clara Harrow"],
    witnesses=["Everyone at dinner"],
    is_public=True
)

# Verify a claim
is_valid, actual = world.verify_character_claim_time_location(
    "Edmund Vale", "Library", day=1, period="evening"
)
```

### For Players:
```bash
# View complete timeline
/timeline

# View specific NPC's schedule
/timeline Edmund Vale
```

## Future Enhancements

- Fact-checker integration to automatically validate time/location claims
- Multi-day support (currently only Day 1 implemented)
- Time period transitions and events
- Movement tracking between locations
- Automatic alibi validation
