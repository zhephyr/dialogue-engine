"""
Example Scenario: The Gallery Silence

A dialogue-first murder mystery designed to test the dialogue engine.
No physical evidence, no locked rooms - only conflicting testimonies.

The mystery is solvable ONLY through:
- Contradictory statements
- Incompatible perceptions
- Lies that cannot all be true simultaneously
- Dialogue pressure and consistency checking

Victim: Elias Morven (poisoned earlier, died later)
Killer: Nathan Cross (poisoned victim during casual conversation)
Setting: Small manor, single evening gathering
"""

from world_state import WorldState
from npc_agent import NPCAgent, CharacterTrait
from dialogue_engine import DialogueEngine
from datetime import datetime


def create_example_scenario(verbose: bool = False) -> DialogueEngine:
    """
    Create The Gallery Silence scenario.
    
    Returns a configured DialogueEngine with all NPCs and world state.
    """
    
    # ========== WORLD STATE SETUP ==========
    world = WorldState()
    
    # Setting information
    world.add_fact("time_period", "1800s", category="setting", is_public=True)
    world.add_fact("setting", "Victorian England", category="setting", is_public=True)
    world.add_fact("estate_name", "Morven Estate", category="setting", is_public=True)
    world.add_fact("estate_type", "Secluded country mansion", category="setting", is_public=True)
    world.add_fact("gathering_purpose", "Evening social gathering hosted by Elias Morven", 
                   category="setting", is_public=True)
    
    # Player character information
    world.add_fact("player_role", "Investigator from Scotland Yard", category="player", is_public=True)
    world.add_fact("player_authority", "Official police investigator", category="player", is_public=True)
    world.add_fact("player_arrival", "After Elias collapsed", category="player", is_public=True)
    world.add_character("Investigator")  # Register the player as a character
    
    # Locations
    locations = ["Sitting Room", "Gallery", "Dining Room", "Library", "Terrace", "Foyer"]
    for location in locations:
        world.add_location(location)
    
    # Core facts about the death
    world.add_fact("victim", "Elias Morven", category="death", is_public=True)
    world.add_fact("cause_of_death", "Poison", category="death", is_public=False,
                   witnesses=["Nathan Cross"],
                   event_id="poisoning",
                   schedule_day=1, schedule_period="early_evening")
    world.add_fact("time_of_death", "Night", category="death", is_public=True,
                   event_id="death",
                   schedule_day=1, schedule_period="night")
    world.add_fact("location_of_death", "Gallery", category="death", is_public=True,
                   event_id="death")
    world.add_fact("poison_method", "Wine glass in sitting room", category="death", is_public=False,
                   witnesses=["Nathan Cross"],
                   event_id="poisoning",
                   schedule_day=1, schedule_period="early_evening")
    world.add_fact("delayed_action_poison", "Poison acts slowly and unpredictably", 
                   category="death", is_public=False,
                   witnesses=["Nathan Cross"])
    world.add_fact("no_weapon_found", "No weapon at scene", category="death", is_public=True)
    world.add_fact("no_physical_evidence", "No physical evidence at death scene", 
                   category="death", is_public=True)

    # ========== EXPLICIT TIMELINE/SCHEDULE ==========
    # Single evening - dialogue-relevant timeline
    
    # EARLY EVENING - Gathering begins, sitting room
    world.add_schedule_entry("Elias Morven", 1, "early_evening", "Sitting Room",
                            "Hosting drinks, mingling with guests",
                            with_characters=["Nathan Cross", "Helena Morven", "Arthur Bell", "Lila Chen"],
                            is_public=True,
                            witnesses=["Nathan Cross", "Helena Morven", "Arthur Bell", "Lila Chen"],
                            notes="All guests present at overlapping times")
    
    world.add_schedule_entry("Nathan Cross", 1, "early_evening", "Sitting Room",
                            "Attending gathering, poisoned Elias's wine during casual conversation",
                            with_characters=["Elias Morven", "Helena Morven", "Arthur Bell", "Lila Chen"],
                            is_public=False,
                            witnesses=["Nathan Cross", "Lila Chen"],
                            notes="CRITICAL: Lila saw Nathan refill Elias's glass. Nathan will lie about this.")
    
    world.add_schedule_entry("Helena Morven", 1, "early_evening", "Sitting Room",
                            "Attending gathering, observing brother Elias",
                            with_characters=["Elias Morven", "Nathan Cross", "Arthur Bell", "Lila Chen"],
                            is_public=True,
                            witnesses=["Elias Morven", "Nathan Cross", "Arthur Bell", "Lila Chen"])
    
    world.add_schedule_entry("Arthur Bell", 1, "early_evening", "Sitting Room",
                            "Attending gathering, observed Nathan and Elias alone briefly",
                            with_characters=["Elias Morven", "Nathan Cross", "Helena Morven", "Lila Chen"],
                            is_public=True,
                            witnesses=["Elias Morven", "Nathan Cross", "Helena Morven", "Lila Chen"],
                            notes="Saw Nathan and Elias alone together, didn't hear conversation")
    
    world.add_schedule_entry("Lila Chen", 1, "early_evening", "Sitting Room",
                            "Attending gathering, witnessed Nathan refill Elias's glass",
                            with_characters=["Elias Morven", "Nathan Cross", "Helena Morven", "Arthur Bell"],
                            is_public=True,
                            witnesses=["Elias Morven", "Nathan Cross", "Helena Morven", "Arthur Bell", "Lila Chen"],
                            notes="CRITICAL: Saw Nathan pour wine for Elias, assumed harmless")
    
    # MID EVENING - Elias moves between rooms, Nathan lies about when he left
    world.add_schedule_entry("Elias Morven", 1, "evening", "Library",
                            "Moved to library, still drinking wine, poison beginning to take effect",
                            is_public=True,
                            witnesses=["Helena Morven", "Arthur Bell"],
                            notes="Helena saw him still drinking after Nathan claims he left")
    
    world.add_schedule_entry("Nathan Cross", 1, "evening", "Sitting Room",
                            "Still in sitting room - will lie and claim he left earlier",
                            is_public=False,
                            witnesses=["Nathan Cross", "Arthur Bell"],
                            notes="LIE ZONE: Nathan claims he left before Elias finished wine, but was still there")
    
    world.add_schedule_entry("Helena Morven", 1, "evening", "Library",
                            "With Elias in library, saw him drinking wine",
                            with_characters=["Elias Morven"],
                            is_public=True,
                            witnesses=["Helena Morven", "Elias Morven", "Arthur Bell"],
                            notes="Saw Elias drinking AFTER Nathan claims to have left")
    
    world.add_schedule_entry("Arthur Bell", 1, "evening", "Sitting Room",
                            "Observed Nathan still present, saw Elias stumble slightly",
                            with_characters=["Nathan Cross"],
                            is_public=True,
                            witnesses=["Arthur Bell", "Nathan Cross"],
                            notes="Can contradict Nathan's timeline - Nathan was there longer than he claims")
    
    world.add_schedule_entry("Lila Chen", 1, "evening", "Terrace",
                            "Stepped outside for air, away from main group",
                            is_public=True,
                            witnesses=["Lila Chen"])
    
    # NIGHT - Elias collapses in gallery, everyone converges
    world.add_schedule_entry("Elias Morven", 1, "night", "Gallery",
                            "Collapsed from poison, died",
                            is_public=True,
                            witnesses=["Arthur Bell"],
                            notes="Arthur discovered the body")
    
    world.add_schedule_entry("Nathan Cross", 1, "night", "Dining Room",
                            "Away from gallery when death occurred - genuine alibi for moment of death",
                            is_public=True,
                            witnesses=["Helena Morven", "Nathan Cross"],
                            notes="Not present at death - this is TRUE and will be his defense")
    
    world.add_schedule_entry("Helena Morven", 1, "night", "Dining Room",
                            "With Nathan when Elias collapsed - can confirm Nathan wasn't in gallery",
                            with_characters=["Nathan Cross"],
                            is_public=True,
                            witnesses=["Helena Morven", "Nathan Cross"],
                            notes="Can alibi Nathan for moment of death, but this is misdirection")
    
    world.add_schedule_entry("Arthur Bell", 1, "night", "Gallery",
                            "Discovered Elias collapsed, called for help",
                            is_public=True,
                            witnesses=["Arthur Bell", "Nathan Cross", "Helena Morven", "Lila Chen"],
                            notes="Found the body")
    
    world.add_schedule_entry("Lila Chen", 1, "night", "Library",
                            "Reading, heard commotion from gallery",
                            is_public=True,
                            witnesses=["Lila Chen"])
    
    # AFTER DISCOVERY - Everyone gathers
    world.add_schedule_entry("Nathan Cross", 1, "night", "Gallery",
                            "Responded to Arthur's call, feigned shock",
                            with_characters=["Helena Morven", "Arthur Bell", "Lila Chen"],
                            is_public=True,
                            witnesses=["Helena Morven", "Arthur Bell", "Lila Chen", "Nathan Cross"])
    
    world.add_schedule_entry("Helena Morven", 1, "night", "Gallery",
                            "Rushed to brother's side, devastated",
                            with_characters=["Nathan Cross", "Arthur Bell", "Lila Chen"],
                            is_public=True,
                            witnesses=["Nathan Cross", "Arthur Bell", "Lila Chen", "Helena Morven"])
    
    world.add_schedule_entry("Lila Chen", 1, "night", "Gallery",
                            "Arrived after others, witnessed the scene",
                            with_characters=["Nathan Cross", "Helena Morven", "Arthur Bell"],
                            is_public=True,
                            witnesses=["Nathan Cross", "Helena Morven", "Arthur Bell", "Lila Chen"])
    
    # ========== KEY EVENTS WITH SEQUENCE ORDERING ==========
    
    world.add_event(
        event_id="gathering_begins",
        description="Evening gathering begins in sitting room with drinks",
        timestamp="Day 1 - Early Evening",
        location="Sitting Room",
        participants=["Elias Morven", "Nathan Cross", "Helena Morven", "Arthur Bell", "Lila Chen"],
        witnesses=["Elias Morven", "Nathan Cross", "Helena Morven", "Arthur Bell", "Lila Chen"],
        details={
            "atmosphere": "social",
            "drinks_served": True,
            "all_present": True
        },
        sequence_order=0
    )
    
    world.add_event(
        event_id="nathan_elias_alone",
        description="Nathan and Elias have brief private conversation in sitting room",
        timestamp="Day 1 - Early Evening",
        location="Sitting Room",
        participants=["Nathan Cross", "Elias Morven"],
        witnesses=["Nathan Cross", "Elias Morven", "Arthur Bell"],
        details={
            "privacy": "partial",
            "duration": "brief",
            "arthur_witnessed": "saw them together but didn't hear conversation"
        },
        sequence_order=1,
        caused_by="gathering_begins"
    )
    
    world.add_event(
        event_id="poisoning",
        description="Nathan poisons Elias's wine during casual conversation",
        timestamp="Day 1 - Early Evening",
        location="Sitting Room",
        participants=["Nathan Cross", "Elias Morven"],
        witnesses=["Nathan Cross", "Lila Chen"],
        details={
            "method": "refilled wine glass with poisoned wine",
            "lila_saw": "Lila witnessed Nathan refill the glass but assumed it was harmless",
            "elias_unaware": True,
            "poison_type": "slow-acting"
        },
        sequence_order=2,
        caused_by="nathan_elias_alone"
    )
    
    world.add_event(
        event_id="elias_continues_drinking",
        description="Elias continues drinking the poisoned wine while moving to library",
        timestamp="Day 1 - Evening",
        location="Library",
        participants=["Elias Morven"],
        witnesses=["Elias Morven", "Helena Morven", "Arthur Bell"],
        details={
            "helena_present": "Helena saw Elias still drinking",
            "timing": "after Nathan claims he left",
            "contradiction": "proves Nathan's timeline is false"
        },
        sequence_order=0,
        caused_by="poisoning"
    )
    
    world.add_event(
        event_id="death",
        description="Elias collapses in gallery from poison",
        timestamp="Day 1 - Night",
        location="Gallery",
        participants=["Elias Morven"],
        witnesses=["Arthur Bell"],
        details={
            "nathan_not_present": True,
            "cause": "delayed poison from earlier",
            "discoverer": "Arthur Bell"
        },
        sequence_order=0,
        caused_by="elias_continues_drinking"
    )
    
    world.add_event(
        event_id="body_discovered",
        description="Arthur discovers Elias collapsed, calls for others",
        timestamp="Day 1 - Night",
        location="Gallery",
        participants=["Arthur Bell"],
        witnesses=["Arthur Bell", "Nathan Cross", "Helena Morven", "Lila Chen"],
        details={
            "response_time": "immediate",
            "all_converged": True
        },
        sequence_order=1,
        caused_by="death"
    )
    
    # ========== CRITICAL CONTRADICTION FACTS ==========
    # These facts create the impossible timeline that exposes Nathan
    
    world.add_fact(
        "nathan_claim_no_pouring",
        "Nathan claims: 'I never poured Elias a drink'",
        category="testimony",
        is_public=False,
        witnesses=["Nathan Cross"],
        event_id="poisoning",
        schedule_day=1,
        schedule_period="early_evening"
    )
    
    world.add_fact(
        "lila_saw_pouring",
        "Lila saw Nathan refill Elias's glass in the sitting room",
        category="testimony",
        is_public=False,
        witnesses=["Lila Chen", "Nathan Cross"],
        event_id="poisoning",
        schedule_day=1,
        schedule_period="early_evening"
    )
    
    world.add_fact(
        "nathan_claim_left_early",
        "Nathan claims: 'I left before Elias finished his wine'",
        category="testimony",
        is_public=False,
        witnesses=["Nathan Cross"],
        schedule_day=1,
        schedule_period="evening"
    )
    
    world.add_fact(
        "helena_saw_elias_drinking_late",
        "Helena saw Elias still drinking wine after Nathan claims to have left",
        category="testimony",
        is_public=False,
        witnesses=["Helena Morven"],
        event_id="elias_continues_drinking",
        schedule_day=1,
        schedule_period="evening"
    )
    
    world.add_fact(
        "arthur_saw_nathan_longer",
        "Arthur observed Nathan and Elias together longer than Nathan claims",
        category="testimony",
        is_public=False,
        witnesses=["Arthur Bell"],
        schedule_day=1,
        schedule_period="evening"
    )
    
    world.add_fact(
        "nathan_alibi_moment_of_death",
        "Nathan was in dining room with Helena when Elias collapsed - genuine alibi for moment of death",
        category="alibi",
        is_public=True,
        witnesses=["Nathan Cross", "Helena Morven"],
        event_id="death",
        schedule_day=1,
        schedule_period="night"
    )
    
    world.add_fact(
        "poison_delayed_action",
        "The poison was administered earlier, death occurred later when killer was not present",
        category="death",
        is_public=False,
        witnesses=["Nathan Cross"]
    )
    
    # Relationships
    world.add_relationship(
        "Helena Morven", "Elias Morven",
        rel_type="siblings",
        description="Helena is Elias's sister, emotionally close",
        strength=9,
        is_public=True
    )
    
    world.add_relationship(
        "Nathan Cross", "Elias Morven",
        rel_type="acquaintance",
        description="Nathan was an invited guest",
        strength=5,
        is_public=True
    )
    
    world.add_relationship(
        "Arthur Bell", "Elias Morven",
        rel_type="employee",
        description="Arthur manages the estate for Elias",
        strength=7,
        is_public=True
    )
    
    world.add_relationship(
        "Lila Chen", "Elias Morven",
        rel_type="acquaintance",
        description="Lila was an invited guest, artist",
        strength=4,
        is_public=True
    )
    
    # ========== NPC CREATION ==========
    
    # Nathan Cross - The Killer (poisons victim earlier, has alibi for moment of death)
    nathan = NPCAgent(
        name="Nathan Cross",
        personality="Composed, socially confident, calculating. Maintains calm under pressure but becomes defensive when timeline is questioned.",
        background="Guest at the gathering. Poisoned Elias's wine during casual conversation in sitting room.",
        goals=[
            "Maintain that he never poured Elias a drink",
            "Claim he left the sitting room earlier than he did",
            "Use his genuine alibi for moment of death as defense",
            "Discredit or dismiss contradictory testimonies"
        ],
        fears=[
            "Lila revealing she saw him pour the wine",
            "Arthur exposing how long he was actually in sitting room",
            "Timeline contradictions becoming undeniable",
            "Being asked specific questions about wine glasses"
        ],
        secrets=[
            "I poisoned Elias's wine during our conversation in the sitting room",
            "The poison acts slowly - I knew he wouldn't die immediately",
            "I deliberately stayed in other rooms when the poison would take effect",
            "I was genuinely not in the gallery when he died - that's my defense",
            "Lila saw me refill his glass, but she doesn't realize what it means",
            "I was in the sitting room longer than I claim - Arthur can contradict me"
        ],
        current_location="Foyer",
        emotional_state="Controlled concern"
    )
    
    nathan.relationships = {
        "Elias Morven": "The host, we were acquaintances",
        "Helena Morven": "Elias's sister, she was with me when he collapsed",
        "Arthur Bell": "The estate manager, observant fellow",
        "Lila Chen": "Another guest, an artist",
        "Investigator": "The investigator looking into Elias's death"
    }
    
    # Helena Morven - Victim's sister (emotionally close, observant but biased)
    helena = NPCAgent(
        name="Helena Morven",
        personality="Emotionally intense, protective of brother's memory, observant but grief-clouded. Tends to overstate certainty.",
        background="Elias's sister. Was present throughout the evening and saw Elias drinking wine in the library.",
        goals=[
            "Find out what happened to her brother",
            "Protect Elias's reputation",
            "Share what she observed",
            "Push for justice"
        ],
        fears=[
            "Being dismissed as too emotional",
            "Missing important details in her grief",
            "Wrongly accusing someone",
            "Not being taken seriously"
        ],
        secrets=[
            "I saw Elias still drinking wine in the library during mid-evening",
            "Nathan claims he left before that, but Elias was still drinking the wine from earlier",
            "I was with Nathan in the dining room when Elias collapsed - I can confirm Nathan wasn't there",
            "I sometimes exaggerate my certainty about things I only partially observed",
            "I'm biased toward believing Nathan because he was with me during the death"
        ],
        current_location="Gallery",
        emotional_state="Grieving and determined"
    )
    
    helena.relationships = {
        "Elias Morven": "My brother, we were very close",
        "Nathan Cross": "A guest, he was with me when Elias collapsed",
        "Arthur Bell": "Elias's estate manager, reliable",
        "Lila Chen": "Another guest, seemed detached",
        "Investigator": "The investigator, I hope they find the truth"
    }
    
    # Arthur Bell - Estate manager (practical, truthful, credible)
    arthur = NPCAgent(
        name="Arthur Bell",
        personality="Practical, observant, cautious with claims. Speaks precisely about what he saw and doesn't speculate beyond that.",
        background="Estate manager for Elias. Present throughout evening and discovered the body.",
        goals=[
            "Provide accurate information",
            "Stick to observed facts",
            "Avoid speculation",
            "Assist the investigation professionally"
        ],
        fears=[
            "Being pressured to speculate",
            "Misremembering details",
            "Accusations of involvement",
            "Failing Elias's memory"
        ],
        secrets=[
            "I saw Nathan and Elias alone together in the sitting room",
            "I didn't hear their conversation but noticed they were together longer than Nathan admits",
            "I saw Elias stumble slightly later in the evening but dismissed it at the time",
            "I discovered Elias collapsed in the gallery",
            "Nathan was definitely still in the sitting room when he claims he'd left"
        ],
        current_location="Gallery",
        emotional_state="Somber and professional"
    )
    
    arthur.relationships = {
        "Elias Morven": "My employer, I managed his estate",
        "Nathan Cross": "A guest that evening",
        "Helena Morven": "Elias's sister, understandably distraught",
        "Lila Chen": "A guest, an artist if I recall",
        "Investigator": "The investigator, I'll help however I can"
    }
    
    # Lila Chen - Artist guest (detached observer, key witness)
    lila = NPCAgent(
        name="Lila Chen",
        personality="Observant, artistic, somewhat detached. Hesitant to make accusations but remembers visual details clearly.",
        background="Guest artist invited to the gathering. Witnessed Nathan refill Elias's glass but didn't realize the significance.",
        goals=[
            "Share what she observed without overstepping",
            "Avoid direct accusations unless certain",
            "Maintain artistic objectivity",
            "Help if pressed but not volunteer damaging information"
        ],
        fears=[
            "Wrongly accusing someone",
            "Being pulled into conflict",
            "Overstating what she saw",
            "Becoming a target herself"
        ],
        secrets=[
            "I clearly saw Nathan refill Elias's glass in the sitting room",
            "I thought it was just hospitality at the time",
            "I didn't realize the significance until after Elias died",
            "Nathan might not know I saw him do it",
            "I'm hesitant to directly accuse Nathan because I don't want to be wrong"
        ],
        current_location="Library",
        emotional_state="Uneasy and cautious"
    )
    
    lila.relationships = {
        "Elias Morven": "The host, I didn't know him well",
        "Nathan Cross": "Another guest, seemed friendly enough",
        "Helena Morven": "Elias's sister, she's taking this very hard",
        "Arthur Bell": "The estate manager, seems reliable",
        "Investigator": "The investigator, I'll answer questions but I'm not comfortable making accusations"
    }
    
    # ========== INITIALIZE ENGINE ==========
    engine = DialogueEngine(world, verbose=verbose)
    
    # Add all NPCs
    engine.add_npc(nathan)
    engine.add_npc(helena)
    engine.add_npc(arthur)
    engine.add_npc(lila)
    
    # Set initial scene
    engine.set_scene(
        "Victorian England, 1800s. You are an investigator dispatched from Scotland Yard "
        "to Morven Estate, a secluded country mansion. Elias Morven, the host of an evening gathering, "
        "has collapsed and died in the gallery. No weapon was found, no signs of struggle. "
        "You have arrived to question the occupants. The truth lies somewhere in their conflicting testimonies. "
        "Four people were present: Nathan Cross, Helena Morven (Elias's sister), "
        "Arthur Bell (estate manager), and Lila Chen (an artist). "
        "Each knows something, but their stories don't quite align. "
        "The NPCs know you are an official police investigator with authority to question them."
    )
    
    if verbose:
        print("\n" + "="*70)
        print("THE GALLERY SILENCE - Scenario Loaded")
        print("="*70)
        print(f"\nVictim: {world.get_fact('victim')}")
        print(f"Location of Death: {world.get_fact('location_of_death')}")
        print(f"Time of Death: {world.get_fact('time_of_death')}")
        print(f"Cause: {world.get_fact('cause_of_death')} (not public knowledge)")
        print(f"\nGuests: Nathan Cross, Helena Morven, Arthur Bell, Lila Chen")
        print(f"\n{'='*70}")
        print("DESIGN GOAL: Dialogue-First Mystery")
        print("="*70)
        print("This scenario is solvable ONLY through dialogue:")
        print("  • No physical evidence required")
        print("  • No locked rooms or forensic clues")
        print("  • Solution found in contradictory testimonies")
        print(f"\nKiller: Nathan Cross")
        print(f"Method: Poisoned wine earlier, death occurred later")
        print(f"Nathan has genuine alibi for moment of death (with Helena)")
        print(f"But his timeline about EARLIER events contains lies")
        print(f"\n{'='*70}")
        print("KEY CONTRADICTIONS:")
        print("="*70)
        print("1. Nathan: 'I never poured Elias a drink'")
        print("   Lila: 'I saw Nathan refill Elias's glass'")
        print("")
        print("2. Nathan: 'I left before Elias finished his wine'")
        print("   Helena: 'Elias was still drinking after Nathan claims he left'")
        print("")
        print("3. Nathan: Claims he left sitting room early")
        print("   Arthur: 'Nathan and Elias were together longer than Nathan admits'")
        print(f"\n{'='*70}")
        print("These statements cannot all be true.")
        print("The investigation must expose the contradictions through dialogue.")
        print("="*70 + "\n")
    
    return engine


def main():
    """Standalone test of the scenario"""
    print("Creating The Gallery Silence scenario...")
    engine = create_example_scenario(verbose=True)
    
    print("\n" + "="*70)
    print("SCENARIO STATISTICS")
    print("="*70)
    stats = engine.get_engine_stats()
    print(f"\nNPCs: {', '.join(stats['npc_names'])}")
    print(f"\nWorld State:")
    print(f"  Locations: {len(stats['world_state']['locations'])}")
    print(f"  Facts: {stats['world_state']['total_facts']}")
    print(f"  Events: {stats['world_state']['total_events']}")
    print(f"  Relationships: {stats['world_state']['total_relationships']}")
    print("\n" + "="*70)
    print("TESTING FOCUS")
    print("="*70)
    print("This scenario tests the dialogue engine's ability to:")
    print("  ✓ Enforce knowledge boundaries (who knows what)")
    print("  ✓ Track claims over time")
    print("  ✓ Detect contradictions between NPCs")
    print("  ✓ Allow plausible lies that fail under pressure")
    print("  ✓ Require dialogue (not evidence) to solve")
    print("\nRun console_interface.py to interact with NPCs.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
