"""
World State Management System

Manages all facts, locations, events, relationships, and timeline in the game world.
NPCs can query this to verify their claims and maintain consistency.
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from pydantic import BaseModel, Field


class Fact(BaseModel):
    """Represents a fact in the game world"""
    key: str
    value: Any
    category: str = "general"  # e.g., "location", "event", "relationship", "item"
    timestamp: Optional[str] = None
    source: str = "world"  # Who established this fact
    is_public: bool = True  # Whether this fact is common knowledge
    witnesses: List[str] = Field(default_factory=list)  # Who knows this fact
    # NEW: Link to events and schedule
    event_id: Optional[str] = None  # Which event does this fact relate to?
    schedule_day: Optional[int] = None  # Which day on schedule?
    schedule_period: Optional[str] = None  # Which time period?


class Event(BaseModel):
    """Represents an event that occurred in the game world"""
    event_id: str
    description: str
    timestamp: str
    location: str
    participants: List[str] = Field(default_factory=list)
    witnesses: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)
    # NEW: Event sequencing
    sequence_order: int = 0  # Order within the same time period (0 = first, 1 = second, etc.)
    caused_by: Optional[str] = None  # event_id that caused this event


class Relationship(BaseModel):
    """Represents a relationship between two characters"""
    character_a: str
    character_b: str
    relationship_type: str  # e.g., "employer", "friend", "enemy", "family"
    description: str
    strength: int = 5  # 1-10 scale
    is_public: bool = True


class TimeBlock(BaseModel):
    """Represents a specific time period in the game"""
    day: int  # Day number (1, 2, 3, etc.)
    period: str  # "early_morning", "morning", "noon", "afternoon", "evening", "late_night", "overnight"
    
    def __str__(self) -> str:
        return f"Day {self.day} - {self.period.replace('_', ' ').title()}"
    
    def __hash__(self) -> int:
        return hash((self.day, self.period))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, TimeBlock):
            return False
        return self.day == other.day and self.period == other.period


class NPCScheduleEntry(BaseModel):
    """Represents what an NPC was doing during a specific time block"""
    character: str
    time_block: TimeBlock
    location: str
    activity: str
    with_characters: List[str] = Field(default_factory=list)  # Who else was present
    is_public: bool = True  # Whether this information is commonly known
    witnesses: List[str] = Field(default_factory=list)  # Who can verify this
    notes: str = ""  # Additional context


class WorldState:
    """
    Manages the state of the game world including all facts, events, and relationships.
    This serves as the ground truth that NPCs must respect when making claims.
    """
    
    def __init__(self):
        self.facts: Dict[str, Fact] = {}
        self.events: Dict[str, Event] = {}
        self.relationships: List[Relationship] = []
        self.locations: Set[str] = set()
        self.characters: Set[str] = set()
        
        # Timeline and schedule tracking
        self.npc_schedules: Dict[str, List[NPCScheduleEntry]] = {}  # character -> list of schedule entries
        self.time_periods = ["early_morning", "morning", "noon", "afternoon", "evening", "late_night", "overnight"]
        self.current_day = 1
        self.current_period = "afternoon"
        
    def add_fact(self, key: str, value: Any, category: str = "general", 
                 is_public: bool = True, witnesses: Optional[List[str]] = None,
                 source: str = "world", timestamp: Optional[str] = None,
                 event_id: Optional[str] = None,
                 schedule_day: Optional[int] = None,
                 schedule_period: Optional[str] = None) -> None:
        """Add or update a fact in the world state"""
        self.facts[key] = Fact(
            key=key,
            value=value,
            category=category,
            is_public=is_public,
            witnesses=witnesses or [],
            source=source,
            timestamp=timestamp,
            event_id=event_id,
            schedule_day=schedule_day,
            schedule_period=schedule_period
        )
        
    def get_fact(self, key: str) -> Optional[Any]:
        """Retrieve a fact value by key"""
        fact = self.facts.get(key)
        return fact.value if fact else None
    
    def get_fact_details(self, key: str) -> Optional[Fact]:
        """Retrieve full fact details"""
        return self.facts.get(key)
    
    def query_facts(self, category: Optional[str] = None, 
                   is_public: Optional[bool] = None) -> List[Fact]:
        """Query facts by category and/or visibility"""
        results = list(self.facts.values())
        
        if category:
            results = [f for f in results if f.category == category]
        
        if is_public is not None:
            results = [f for f in results if f.is_public == is_public]
            
        return results
    
    def character_knows_fact(self, character: str, fact_key: str) -> bool:
        """Check if a character should know a particular fact"""
        fact = self.facts.get(fact_key)
        if not fact:
            return False
        
        # Public facts are known to all
        if fact.is_public:
            return True
        
        # Check if character is a witness
        if character in fact.witnesses:
            return True
            
        return False
    
    def add_event(self, event_id: str, description: str, timestamp: str,
                 location: str, participants: Optional[List[str]] = None,
                 witnesses: Optional[List[str]] = None,
                 details: Optional[Dict[str, Any]] = None,
                 sequence_order: int = 0,
                 caused_by: Optional[str] = None) -> None:
        """Add an event to the timeline"""
        self.events[event_id] = Event(
            event_id=event_id,
            description=description,
            timestamp=timestamp,
            location=location,
            participants=participants or [],
            witnesses=witnesses or [],
            details=details or {},
            sequence_order=sequence_order,
            caused_by=caused_by
        )
        
        # Add location and characters to tracking
        self.locations.add(location)
        for char in (participants or []):
            self.characters.add(char)
        for char in (witnesses or []):
            self.characters.add(char)
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """Retrieve an event by ID"""
        return self.events.get(event_id)
    
    def get_events_at_location(self, location: str) -> List[Event]:
        """Get all events that occurred at a specific location"""
        return [e for e in self.events.values() if e.location == location]
    
    def get_events_with_character(self, character: str) -> List[Event]:
        """Get all events involving a character (as participant or witness)"""
        return [
            e for e in self.events.values() 
            if character in e.participants or character in e.witnesses
        ]
    
    def add_relationship(self, char_a: str, char_b: str, rel_type: str,
                        description: str, strength: int = 5, 
                        is_public: bool = True) -> None:
        """Add a relationship between two characters"""
        self.relationships.append(Relationship(
            character_a=char_a,
            character_b=char_b,
            relationship_type=rel_type,
            description=description,
            strength=strength,
            is_public=is_public
        ))
        
        # Add characters to tracking
        self.characters.add(char_a)
        self.characters.add(char_b)
    
    def get_relationships(self, character: str) -> List[Relationship]:
        """Get all relationships involving a character"""
        return [
            r for r in self.relationships 
            if r.character_a == character or r.character_b == character
        ]
    
    def get_relationship_between(self, char_a: str, char_b: str) -> List[Relationship]:
        """Get relationships between two specific characters"""
        return [
            r for r in self.relationships
            if (r.character_a == char_a and r.character_b == char_b) or
               (r.character_a == char_b and r.character_b == char_a)
        ]
    
    def add_location(self, location: str) -> None:
        """Add a location to the world"""
        self.locations.add(location)
    
    def add_character(self, character: str) -> None:
        """Register a character in the world"""
        self.characters.add(character)
        if character not in self.npc_schedules:
            self.npc_schedules[character] = []
    
    def add_schedule_entry(
        self,
        character: str,
        day: int,
        period: str,
        location: str,
        activity: str,
        with_characters: Optional[List[str]] = None,
        is_public: bool = True,
        witnesses: Optional[List[str]] = None,
        notes: str = ""
    ) -> None:
        """
        Add a schedule entry for what an NPC was doing during a specific time period.
        
        Args:
            character: Name of the character
            day: Day number (1, 2, 3, etc.)
            period: Time period ("early_morning", "morning", "noon", "afternoon", "evening", "late_night", "overnight")
            location: Where the character was
            activity: What they were doing
            with_characters: Who else was present with them
            is_public: Whether this is common knowledge
            witnesses: Who can verify this (includes the character themselves by default)
            notes: Additional context
        """
        if period not in self.time_periods:
            raise ValueError(f"Invalid period '{period}'. Must be one of: {self.time_periods}")
        
        self.add_character(character)
        
        time_block = TimeBlock(day=day, period=period)
        
        # Add character to witnesses if not already there
        all_witnesses = list(witnesses) if witnesses else []
        if character not in all_witnesses:
            all_witnesses.append(character)
        
        # Add companions to witnesses
        for companion in (with_characters or []):
            if companion not in all_witnesses:
                all_witnesses.append(companion)
        
        entry = NPCScheduleEntry(
            character=character,
            time_block=time_block,
            location=location,
            activity=activity,
            with_characters=with_characters or [],
            is_public=is_public,
            witnesses=all_witnesses,
            notes=notes
        )
        
        self.npc_schedules[character].append(entry)
    
    def get_character_schedule(self, character: str, day: Optional[int] = None) -> List[NPCScheduleEntry]:
        """Get schedule entries for a character, optionally filtered by day"""
        if character not in self.npc_schedules:
            return []
        
        entries = self.npc_schedules[character]
        
        if day is not None:
            entries = [e for e in entries if e.time_block.day == day]
        
        return sorted(entries, key=lambda e: (e.time_block.day, self.time_periods.index(e.time_block.period)))
    
    def query_facts_by_event(self, event_id: str) -> List[Fact]:
        """Get all facts associated with a specific event"""
        return [fact for fact in self.facts.values() if fact.event_id == event_id]
    
    def query_facts_by_schedule(self, day: int, period: str) -> List[Fact]:
        """Get all facts from a specific schedule time"""
        return [fact for fact in self.facts.values() 
                if fact.schedule_day == day and fact.schedule_period == period]
    
    def get_events_in_sequence(self, timestamp: str) -> List[Event]:
        """Get all events at a timestamp, ordered by sequence_order"""
        events = [e for e in self.events.values() if e.timestamp == timestamp]
        return sorted(events, key=lambda e: e.sequence_order)
    
    def get_character_location_at_time(self, character: str, day: int, period: str) -> Optional[str]:
        """Get where a character was during a specific time period"""
        entries = self.get_character_schedule(character, day)
        for entry in entries:
            if entry.time_block.period == period:
                return entry.location
        return None
    
    def get_characters_at_location_time(self, location: str, day: int, period: str) -> List[str]:
        """Get all characters who were at a specific location during a time period"""
        characters = []
        for char in self.characters:
            char_location = self.get_character_location_at_time(char, day, period)
            if char_location == location:
                characters.append(char)
        return characters
    
    def verify_character_claim_time_location(
        self,
        character: str,
        claimed_location: str,
        day: int,
        period: str
    ) -> tuple[bool, Optional[str]]:
        """
        Verify if a character's claim about their location at a specific time is accurate.
        
        Returns:
            Tuple of (is_valid, actual_location)
        """
        actual_location = self.get_character_location_at_time(character, day, period)
        
        if actual_location is None:
            return True, None  # No schedule entry, can't contradict
        
        is_valid = actual_location.lower() == claimed_location.lower()
        return is_valid, actual_location
    
    def get_world_summary(self) -> Dict[str, Any]:
        """Get a summary of the current world state"""
        total_schedule_entries = sum(len(entries) for entries in self.npc_schedules.values())
        
        return {
            "total_facts": len(self.facts),
            "total_events": len(self.events),
            "total_relationships": len(self.relationships),
            "total_schedule_entries": total_schedule_entries,
            "locations": list(self.locations),
            "characters": list(self.characters),
            "public_facts": len([f for f in self.facts.values() if f.is_public]),
            "private_facts": len([f for f in self.facts.values() if not f.is_public]),
            "current_time": f"Day {self.current_day} - {self.current_period}"
        }
    
    def export_character_knowledge(self, character: str) -> Dict[str, Any]:
        """
        Export all facts, events, and relationships that a specific character knows.
        This is used to provide context to the AI agent.
        """
        known_facts = [
            f for f in self.facts.values()
            if self.character_knows_fact(character, f.key)
        ]
        
        known_events = self.get_events_with_character(character)
        
        relationships = self.get_relationships(character)
        
        # Get character's schedule
        schedule = self.get_character_schedule(character)
        
        return {
            "character": character,
            "known_facts": [
                {"key": f.key, "value": f.value, "category": f.category}
                for f in known_facts
            ],
            "known_events": [
                {
                    "id": e.event_id,
                    "description": e.description,
                    "timestamp": e.timestamp,
                    "location": e.location
                }
                for e in known_events
            ],
            "relationships": [
                {
                    "with": r.character_b if r.character_a == character else r.character_a,
                    "type": r.relationship_type,
                    "description": r.description
                }
                for r in relationships
            ],
            "schedule": [
                {
                    "time": str(entry.time_block),
                    "location": entry.location,
                    "activity": entry.activity,
                    "with": entry.with_characters,
                    "notes": entry.notes
                }
                for entry in schedule
            ]
        }
