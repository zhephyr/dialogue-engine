import pytest
from world_state import WorldState, TimeBlock

@pytest.fixture
def empty_world():
    return WorldState()

@pytest.fixture
def populated_world():
    ws = WorldState()
    ws.add_character("Alice")
    ws.add_character("Bob")
    ws.add_location("Library")
    ws.add_location("Park")
    ws.add_fact("the_weather", "sunny")
    return ws
