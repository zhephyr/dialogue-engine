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


class Event(BaseModel):
    """Represents an event that occurred in the game world"""
    event_id: str
    description: str
    timestamp: str
    location: str
    participants: List[str] = Field(default_factory=list)
    witnesses: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)


class Relationship(BaseModel):
    """Represents a relationship between two characters"""
    character_a: str
    character_b: str
    relationship_type: str  # e.g., "employer", "friend", "enemy", "family"
    description: str
    strength: int = 5  # 1-10 scale
    is_public: bool = True


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
        
    def add_fact(self, key: str, value: Any, category: str = "general", 
                 is_public: bool = True, witnesses: Optional[List[str]] = None,
                 source: str = "world", timestamp: Optional[str] = None) -> None:
        """Add or update a fact in the world state"""
        self.facts[key] = Fact(
            key=key,
            value=value,
            category=category,
            is_public=is_public,
            witnesses=witnesses or [],
            source=source,
            timestamp=timestamp
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
                 details: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to the timeline"""
        self.events[event_id] = Event(
            event_id=event_id,
            description=description,
            timestamp=timestamp,
            location=location,
            participants=participants or [],
            witnesses=witnesses or [],
            details=details or {}
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
    
    def get_world_summary(self) -> Dict[str, Any]:
        """Get a summary of the current world state"""
        return {
            "total_facts": len(self.facts),
            "total_events": len(self.events),
            "total_relationships": len(self.relationships),
            "locations": list(self.locations),
            "characters": list(self.characters),
            "public_facts": len([f for f in self.facts.values() if f.is_public]),
            "private_facts": len([f for f in self.facts.values() if not f.is_public])
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
            ]
        }
