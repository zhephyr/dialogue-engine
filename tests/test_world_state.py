import pytest
from world_state import Fact, Event, Relationship, TimeBlock, NPCScheduleEntry

def test_add_and_get_fact(empty_world):
    """Test adding a fact and retrieving it to ensure correct properties are set."""
    empty_world.add_fact("mayor_corrupt", True, category="secret", is_public=False)
    
    fact = empty_world.get_fact_details("mayor_corrupt")
    assert fact is not None
    assert fact.key == "mayor_corrupt"
    assert fact.value is True
    assert fact.category == "secret"
    assert fact.is_public is False
    assert fact.source == "world"

def test_get_nonexistent_fact(empty_world):
    assert empty_world.get_fact("doesntexist") is None
    assert empty_world.get_fact_details("doesntexist") is None

def test_character_knows_public_fact(populated_world):
    populated_world.add_fact("festival_today", True, is_public=True)
    assert populated_world.character_knows_fact("Alice", "festival_today")

def test_character_knows_private_fact_if_witnessed(populated_world):
    populated_world.add_fact("secret_meeting", True, is_public=False, witnesses=["Alice"])
    assert populated_world.character_knows_fact("Alice", "secret_meeting")
    assert not populated_world.character_knows_fact("Bob", "secret_meeting")

def test_add_event(populated_world):
    populated_world.add_event(
        event_id="murder_1",
        description="The mayor was found dead",
        timestamp="2024-01-01 22:00",
        location="Library",
        participants=["Mayor"],
        witnesses=["Bob"]
    )
    
    event = populated_world.get_event("murder_1")
    assert event is not None
    assert event.location == "Library"
    assert "Bob" in event.witnesses
    assert "Alice" not in event.witnesses

def test_get_events_with_character(populated_world):
    populated_world.add_event("e1", "Desc", "10:00", "Park", participants=["Alice"])
    populated_world.add_event("e2", "Desc", "11:00", "Library", witnesses=["Alice"])
    populated_world.add_event("e3", "Desc", "12:00", "Park", participants=["Bob"])
    
    events = populated_world.get_events_with_character("Alice")
    assert len(events) == 2
    event_ids = [e.event_id for e in events]
    assert "e1" in event_ids
    assert "e2" in event_ids
    assert "e3" not in event_ids

def test_add_and_get_relationships(populated_world):
    populated_world.add_relationship("Alice", "Bob", "friends", "They have been friends since kids", strength=8)
    populated_world.add_relationship("Alice", "Charlie", "enemies", "Rivals", strength=2)
    
    rels = populated_world.get_relationships("Alice")
    assert len(rels) == 2
    
    rel_list = populated_world.get_relationship_between("Alice", "Bob")
    assert len(rel_list) == 1
    rel = rel_list[0]
    assert rel.relationship_type == "friends"
    assert rel.strength == 8
    
    # Check directionality logic
    rel_list2 = populated_world.get_relationship_between("Bob", "Alice")
    assert len(rel_list2) == 1

def test_set_and_query_npc_schedule(populated_world):
    populated_world.add_schedule_entry("Alice", 1, "morning", "Park", "reading", is_public=True)
    populated_world.add_schedule_entry("Alice", 1, "afternoon", "Library", "studying", is_public=False)
    
    schedule = populated_world.get_character_schedule("Alice", day=1)
    assert len(schedule) == 2
    
    # Query specific block location
    location = populated_world.get_character_location_at_time("Alice", 1, "morning")
    assert location == "Park"

def test_verify_character_claim_time_location(populated_world):
    populated_world.add_schedule_entry("Bob", 1, "morning", "Library", "reading")
    
    is_valid, actual_loc = populated_world.verify_character_claim_time_location("Bob", "Library", 1, "morning")
    assert is_valid is True
    
    is_valid, actual_loc = populated_world.verify_character_claim_time_location("Bob", "Park", 1, "morning")
    assert is_valid is False
    assert actual_loc == "Library"

def test_character_knows_schedule_of_others_if_public(populated_world):
    # The world state logic currently doesn't automatically create facts for schedules out of the box inside add_schedule_entry
    # We test that the schedule works as designed, but the facts need to be explicitly added for the `character_knows_fact` test.
    populated_world.add_schedule_entry("Bob", 1, "morning", "Library", "reading", is_public=True)
    populated_world.add_fact("bob_schedule_d1_morning", True, is_public=True, schedule_day=1, schedule_period="morning")
    
    populated_world.add_schedule_entry("Charlie", 1, "afternoon", "Park", "walking", is_public=False)
    populated_world.add_fact("charlie_schedule_d1_afternoon", True, is_public=False, schedule_day=1, schedule_period="afternoon")
    
    # Alice should know Bob's public schedule
    assert populated_world.character_knows_fact("Alice", "bob_schedule_d1_morning") is True
    # Alice should NOT know Charlie's private schedule
    assert populated_world.character_knows_fact("Alice", "charlie_schedule_d1_afternoon") is False
