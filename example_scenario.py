"""
Example Scenario: The Harrow Estate Incident

A murder mystery scenario for testing the dialogue engine.
Lord Harrow has been murdered in his study, and the player must question
the occupants to determine who is responsible.
"""

from world_state import WorldState
from npc_agent import NPCAgent, CharacterTrait
from dialogue_engine import DialogueEngine
from datetime import datetime


def create_example_scenario(verbose: bool = False) -> DialogueEngine:
    """
    Create The Harrow Estate Incident scenario.
    
    Returns a configured DialogueEngine with all NPCs and world state.
    """
    
    # ========== WORLD STATE SETUP ==========
    world = WorldState()
    
    # Setting information
    world.add_fact("time_period", "1800s", category="setting", is_public=True)
    world.add_fact("setting", "Victorian England", category="setting", is_public=True)
    world.add_fact("estate_name", "Harrow Estate", category="setting", is_public=True)
    world.add_fact("estate_type", "Secluded country mansion", category="setting", is_public=True)
    
    # Player character information
    world.add_fact("player_role", "Investigator from Scotland Yard", category="player", is_public=True)
    world.add_fact("player_authority", "Official police investigator", category="player", is_public=True)
    world.add_fact("player_arrival", "After the murder was discovered", category="player", is_public=True)
    world.add_character("Investigator")  # Register the player as a character
    
    # Locations
    locations = ["Foyer", "Library", "Dining Room", "Study", "Kitchen", "Greenhouse"]
    for location in locations:
        world.add_location(location)
    
    # Core facts about the murder
    world.add_fact("victim", "Lord Harrow", category="murder", is_public=True)
    world.add_fact("murder_weapon", "letter opener", category="murder", is_public=False, 
                   witnesses=["Marian", "Edmund Vale"])
    world.add_fact("cause_of_death", "stab wound", category="murder", is_public=True)
    world.add_fact("time_of_death", "Evening", category="murder", is_public=True)
    world.add_fact("murder_location", "Study", category="murder", is_public=True)
    world.add_fact("door_locked", True, category="murder", is_public=True)
    world.add_fact("door_staged", True, category="murder", is_public=False,
                   witnesses=["Edmund Vale"])  # Only the murderer knows this
    world.add_fact("body_discovered_by", "Marian", category="murder", is_public=True)
    world.add_fact("discovery_time", "Night", category="murder", is_public=True)
    
    # Character locations during key times
    world.add_fact("edmund_location_dinner", "Dining Room", category="location", is_public=True)
    world.add_fact("edmund_location_evening", "Study", category="location", is_public=False,
                   witnesses=["Edmund Vale"])
    world.add_fact("clara_location_evening", "Library", category="location", is_public=False,
                   witnesses=["Clara Harrow", "Dr. Liu"])
    world.add_fact("marian_location_evening", "Kitchen", category="location", is_public=False,
                   witnesses=["Marian"])
    world.add_fact("liu_location_evening", "Library", category="location", is_public=False,
                   witnesses=["Clara Harrow", "Dr. Liu"])
    
    # Key events
    world.add_event(
        event_id="dinner_argument",
        description="Edmund Vale and Lord Harrow had a heated public argument during dinner",
        timestamp="Dinner",
        location="Dining Room",
        participants=["Edmund Vale", "Lord Harrow"],
        witnesses=["Clara Harrow", "Marian", "Dr. Liu"],
        details={
            "topic": "financial matters",
            "intensity": "heated",
            "public": True
        }
    )
    
    world.add_event(
        event_id="edmund_with_victim",
        description="Edmund Vale was alone with Lord Harrow in the study",
        timestamp="Evening (before murder)",
        location="Study",
        participants=["Edmund Vale", "Lord Harrow"],
        witnesses=["Edmund Vale"],
        details={
            "duration": "brief",
            "purpose": "private conversation"
        }
    )
    
    world.add_event(
        event_id="murder",
        description="Lord Harrow was stabbed with a letter opener in the study",
        timestamp="Evening",
        location="Study",
        participants=["Edmund Vale", "Lord Harrow"],
        witnesses=["Edmund Vale"],  # Only the murderer witnessed it
        details={
            "weapon": "letter opener",
            "fatal": True,
            "door_locked_after": True
        }
    )
    
    world.add_event(
        event_id="body_discovery",
        description="Marian discovered Lord Harrow's body in the locked study",
        timestamp="Night",
        location="Study",
        participants=["Marian"],
        witnesses=["Marian"],
        details={
            "door_state": "locked",
            "victim_state": "deceased"
        }
    )
    
    world.add_event(
        event_id="clara_upset",
        description="Clara Harrow was visibly upset during the evening",
        timestamp="Evening",
        location="Library",
        participants=["Clara Harrow"],
        witnesses=["Dr. Liu", "Clara Harrow"],
        details={
            "reason": "family tension",
            "visible": True
        }
    )
    
    # Relationships
    world.add_relationship(
        "Edmund Vale", "Lord Harrow",
        rel_type="financial dependent",
        description="Edmund frequently receives financial support from Lord Harrow",
        strength=6,
        is_public=True
    )
    
    world.add_relationship(
        "Clara Harrow", "Lord Harrow",
        rel_type="family",
        description="Clara is a close relation with a strained emotional relationship",
        strength=4,
        is_public=True
    )
    
    world.add_relationship(
        "Marian", "Lord Harrow",
        rel_type="employer",
        description="Marian is the long-serving household butler",
        strength=7,
        is_public=True
    )
    
    world.add_relationship(
        "Dr. Liu", "Lord Harrow",
        rel_type="business guest",
        description="Dr. Liu was invited for unrelated business matters",
        strength=3,
        is_public=True
    )
    
    # ========== NPC CREATION ==========
    
    # Edmund Vale - The Murderer
    edmund = NPCAgent(
        name="Edmund Vale",
        personality="Intelligent, controlled, calculating, and acutely aware of appearances. Speaks carefully and deflects suspicion.",
        background="A relative who has long depended on Lord Harrow's financial generosity. Felt trapped and resentful of this dependence.",
        goals=[
            "Avoid being identified as the murderer",
            "Maintain the appearance of a locked room mystery",
            "Deflect suspicion onto others",
            "Protect constructed alibi"
        ],
        fears=[
            "Being directly accused with evidence",
            "The staged door lock being discovered",
            "Witnesses contradicting his timeline"
        ],
        secrets=[
            "I murdered Lord Harrow with the letter opener",
            "I staged the locked door to create confusion",
            "I was alone with Lord Harrow when he died",
            "The argument at dinner was about him cutting off my allowance"
        ],
        current_location="Library",
        emotional_state="Tense but controlled"
    )
    
    edmund.relationships = {
        "Lord Harrow": "My benefactor, though our relationship had become strained",
        "Clara Harrow": "Fellow family member, we've always been cordial",
        "Marian": "The butler, very proper and dutiful",
        "Dr. Liu": "A guest I've met only briefly",
        "Investigator": "Scotland Yard detective, I must be careful and cooperative"
    }
    
    # Clara Harrow - Innocent but Suspicious
    clara = NPCAgent(
        name="Clara Harrow",
        personality="Emotional, defensive, and protective of family. Reacts strongly to accusations and can be evasive when pressured.",
        background="A close relation of Lord Harrow with a complicated emotional history. Their relationship was loving but strained.",
        goals=[
            "Protect family reputation",
            "Avoid being accused",
            "Process grief and shock",
            "Maintain dignity"
        ],
        fears=[
            "Being blamed for the murder",
            "Family secrets being exposed",
            "Harsh interrogation",
            "Public scandal"
        ],
        secrets=[
            "I was upset because Lord Harrow and I argued about family inheritance earlier",
            "I have financial troubles Lord Harrow was helping with",
            "I was in the library with Dr. Liu during the murder"
        ],
        current_location="Foyer",
        emotional_state="Upset and grieving"
    )
    
    clara.relationships = {
        "Lord Harrow": "My dear relative, we had our difficulties but I loved him",
        "Edmund Vale": "A cousin, ambitious and always asking for money",
        "Marian": "Faithful servant, known him for years",
        "Dr. Liu": "A polite guest, we spoke briefly in the library",
        "Investigator": "The detective from Scotland Yard, here to investigate the murder"
    }
    
    # Marian - The Butler
    marian = NPCAgent(
        name="Marian",
        personality="Methodical, deferential, cautious, and professional. Reluctant to speculate or accuse without solid evidence.",
        background="Long-serving butler of Harrow Estate. Loyal to the family and devoted to proper procedure.",
        goals=[
            "Assist the investigation professionally",
            "Protect the household's dignity",
            "Avoid speculation or gossip",
            "Maintain order during chaos"
        ],
        fears=[
            "Falsely accusing someone",
            "Failing in duty to the household",
            "Being pressured to speculate",
            "The estate falling into disrepute"
        ],
        secrets=[
            "I discovered the body when the study door was locked",
            "I noticed Edmund was agitated after dinner",
            "I heard raised voices from the study earlier"
        ],
        current_location="Foyer",
        emotional_state="Shocked but composed"
    )
    
    marian.relationships = {
        "Lord Harrow": "My employer for twenty years, a good man",
        "Edmund Vale": "A frequent visitor, often discussing finances with His Lordship",
        "Clara Harrow": "Family member, always kind to the staff",
        "Dr. Liu": "Tonight's guest, seemed pleasant",
        "Investigator": "The Scotland Yard investigator, I must assist them professionally"
    }
    
    # Dr. Liu - Analytical Observer
    liu = NPCAgent(
        name="Dr. Liu",
        personality="Analytical, detached, intellectually curious. Offers interpretations but acknowledges uncertainty.",
        background="A guest invited for unrelated business. Has no personal stake in the household dynamics.",
        goals=[
            "Cooperate with investigation",
            "Provide objective observations",
            "Avoid overstepping bounds",
            "Complete business when appropriate"
        ],
        fears=[
            "Being implicated despite innocence",
            "Offering unfounded theories",
            "Overstepping as an outsider"
        ],
        secrets=[
            "I was in the library with Clara during the murder",
            "I observed Edmund seemed unusually nervous at dinner",
            "I heard the argument between Edmund and Lord Harrow"
        ],
        current_location="Dining Room",
        emotional_state="Calm and observant"
    )
    
    liu.relationships = {
        "Lord Harrow": "My host, we were to discuss business tomorrow",
        "Edmund Vale": "Met tonight, seemed preoccupied",
        "Clara Harrow": "We spoke in the library, she seemed distressed",
        "Marian": "Professional and courteous butler",
        "Investigator": "Scotland Yard detective investigating the murder"
    }
    
    # ========== INITIALIZE ENGINE ==========
    engine = DialogueEngine(world, verbose=verbose)
    
    # Add all NPCs
    engine.add_npc(edmund)
    engine.add_npc(clara)
    engine.add_npc(marian)
    engine.add_npc(liu)
    
    # Set initial scene
    engine.set_scene(
        "Victorian England, 1800s. You are an investigator dispatched from Scotland Yard "
        "to Harrow Estate, a secluded country mansion. Lord Harrow has been murdered in his study. "
        "The household is in shock. You have arrived to question the occupants and uncover the truth. "
        "The NPCs know you are an official police investigator with authority to question them."
    )
    
    if verbose:
        print("\n" + "="*60)
        print("THE HARROW ESTATE INCIDENT - Scenario Loaded")
        print("="*60)
        print(f"\nVictim: {world.get_fact('victim')}")
        print(f"Location: {world.get_fact('murder_location')}")
        print(f"Time: {world.get_fact('time_of_death')}")
        print(f"Discovered by: {world.get_fact('body_discovered_by')}")
        print(f"\nSuspects: Edmund Vale, Clara Harrow")
        print(f"Witnesses: Marian, Dr. Liu")
        print("\nThe murderer is Edmund Vale.")
        print("All NPCs have limited knowledge based on what they witnessed.")
        print("="*60 + "\n")
    
    return engine


def main():
    """Standalone test of the scenario"""
    print("Creating The Harrow Estate Incident scenario...")
    engine = create_example_scenario(verbose=True)
    
    print("\n" + "="*60)
    print("SCENARIO STATISTICS")
    print("="*60)
    stats = engine.get_engine_stats()
    print(f"\nNPCs: {', '.join(stats['npc_names'])}")
    print(f"\nWorld State:")
    print(f"  Locations: {len(stats['world_state']['locations'])}")
    print(f"  Facts: {stats['world_state']['total_facts']}")
    print(f"  Events: {stats['world_state']['total_events']}")
    print(f"  Relationships: {stats['world_state']['total_relationships']}")
    print("\nScenario ready for testing!")
    print("Run console_interface.py to interact with NPCs.")


if __name__ == "__main__":
    main()
