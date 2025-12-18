"""
NPC Agent

Represents an NPC character with personality, goals, fears, relationships, and memory.
The agent uses AI to generate contextually appropriate dialogue while maintaining
consistency with the world state.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MemoryEntry(BaseModel):
    """Represents a memory in the NPC's mind"""
    timestamp: str
    type: str  # "conversation", "observation", "lie", "omission", "event"
    content: str
    context: Dict[str, Any] = Field(default_factory=dict)
    emotional_impact: int = 0  # -10 to +10


class CharacterTrait(BaseModel):
    """Represents a personality trait or characteristic"""
    name: str
    description: str
    intensity: int = 5  # 1-10 scale


class NPCAgent:
    """
    An AI-powered NPC agent that can engage in dialogue while maintaining
    character consistency and tracking its own lies and omissions.
    """
    
    def __init__(
        self,
        name: str,
        personality: str,
        background: str = "",
        goals: Optional[List[str]] = None,
        fears: Optional[List[str]] = None,
        secrets: Optional[List[str]] = None,
        traits: Optional[List[CharacterTrait]] = None,
        relationships: Optional[Dict[str, str]] = None,
        current_location: str = "unknown",
        emotional_state: str = "neutral"
    ):
        self.name = name
        self.personality = personality
        self.background = background
        self.goals = goals or []
        self.fears = fears or []
        self.secrets = secrets or []
        self.traits = traits or []
        self.relationships = relationships or {}  # character_name: relationship_description
        self.current_location = current_location
        self.emotional_state = emotional_state
        
        # Memory systems
        self.memory: List[MemoryEntry] = []
        self.conversation_history: List[Dict[str, str]] = []
        self.lies_told: List[MemoryEntry] = []
        self.omissions_made: List[MemoryEntry] = []
        
        # Knowledge base
        self.known_facts: Dict[str, Any] = {}
        self.witnessed_events: List[str] = []
        
    def add_memory(self, memory_type: str, content: str, 
                   context: Optional[Dict[str, Any]] = None,
                   emotional_impact: int = 0) -> None:
        """Add a memory entry"""
        memory = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            type=memory_type,
            content=content,
            context=context or {},
            emotional_impact=emotional_impact
        )
        self.memory.append(memory)
        
        # Track lies and omissions separately for easy reference
        if memory_type == "lie":
            self.lies_told.append(memory)
        elif memory_type == "omission":
            self.omissions_made.append(memory)
    
    def add_conversation_turn(self, speaker: str, message: str) -> None:
        """Record a turn in the conversation"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "speaker": speaker,
            "message": message
        })
        
        # Also add to general memory
        self.add_memory(
            "conversation",
            f"{speaker}: {message}",
            {"speaker": speaker}
        )
    
    def get_recent_conversation(self, num_turns: int = 10) -> List[Dict[str, str]]:
        """Get the most recent conversation turns"""
        return self.conversation_history[-num_turns:]
    
    def add_known_fact(self, key: str, value: Any) -> None:
        """Add a fact to the character's knowledge base"""
        self.known_facts[key] = value
    
    def knows_fact(self, key: str) -> bool:
        """Check if the character knows a particular fact"""
        return key in self.known_facts
    
    def add_witnessed_event(self, event_id: str) -> None:
        """Record that the character witnessed an event"""
        if event_id not in self.witnessed_events:
            self.witnessed_events.append(event_id)
    
    def get_character_context(self) -> Dict[str, Any]:
        """
        Generate a complete context dictionary for this character.
        This is used to provide the AI with all necessary information.
        """
        return {
            "name": self.name,
            "personality": self.personality,
            "background": self.background,
            "goals": self.goals,
            "fears": self.fears,
            "secrets": self.secrets,
            "traits": [{"name": t.name, "description": t.description} for t in self.traits],
            "relationships": self.relationships,
            "current_location": self.current_location,
            "emotional_state": self.emotional_state,
            "known_facts": self.known_facts,
            "recent_memories": [
                {"type": m.type, "content": m.content}
                for m in self.memory[-20:]  # Last 20 memories
            ],
            "lies_told": [
                {"content": lie.content, "context": lie.context}
                for lie in self.lies_told
            ],
            "omissions_made": [
                {"content": omit.content, "context": omit.context}
                for omit in self.omissions_made
            ]
        }
    
    def get_dialogue_prompt(self, player_message: str, 
                           scene_description: str = "") -> str:
        """
        Generate a prompt for the AI to produce character-appropriate dialogue.
        This includes all character context and conversation history.
        """
        context = self.get_character_context()
        recent_conv = self.get_recent_conversation()
        
        prompt = f"""You are {self.name}, an NPC in a murder mystery game.

CHARACTER PROFILE:
- Personality: {self.personality}
- Background: {self.background}
- Current Location: {self.current_location}
- Emotional State: {self.emotional_state}

GOALS:
{chr(10).join(f"- {goal}" for goal in self.goals)}

FEARS:
{chr(10).join(f"- {fear}" for fear in self.fears)}

SECRETS (things you want to hide):
{chr(10).join(f"- {secret}" for secret in self.secrets)}

RELATIONSHIPS:
{chr(10).join(f"- {char}: {desc}" for char, desc in self.relationships.items())}

WHAT YOU KNOW (facts you're aware of):
{chr(10).join(f"- {key}: {value}" for key, value in self.known_facts.items())}

LIES YOU'VE TOLD RECENTLY:
{chr(10).join(f"- {lie.content}" for lie in self.lies_told[-5:])}

THINGS YOU'VE DELIBERATELY OMITTED:
{chr(10).join(f"- {omit.content}" for omit in self.omissions_made[-5:])}

RECENT CONVERSATION:
{chr(10).join(f"{turn['speaker']}: {turn['message']}" for turn in recent_conv[-5:])}

CURRENT SCENE:
{scene_description if scene_description else "No specific scene details."}

PLAYER'S QUESTION/STATEMENT:
{player_message}

INSTRUCTIONS:
1. Respond in character as {self.name}
2. Stay true to your personality, goals, and fears
3. You may choose to lie or omit information to protect your secrets or achieve your goals
4. If you make a claim about facts, it should align with what you know OR be a deliberate deception
5. Be natural and conversational
6. Keep responses relatively brief (1-3 sentences typically)

YOUR RESPONSE (as {self.name}):"""

        return prompt
    
    def get_fact_claim_prompt(self, statement: str) -> str:
        """
        Generate a prompt to extract factual claims from a statement.
        This is used by the fact-checker.
        """
        return f"""Analyze this statement and extract any factual claims that can be verified:

Statement: "{statement}"

Extract claims in this format:
CLAIM: <the specific claim>
CATEGORY: <location/event/relationship/item/other>
KEY: <a simple key for this fact>
VALUE: <the claimed value>

If there are no verifiable factual claims, respond with "NO_CLAIMS".

Claims:"""
    
    def update_emotional_state(self, new_state: str) -> None:
        """Update the character's emotional state"""
        self.emotional_state = new_state
        self.add_memory(
            "observation",
            f"Emotional state changed to: {new_state}",
            {"previous_state": self.emotional_state}
        )
    
    def set_location(self, location: str) -> None:
        """Update the character's current location"""
        old_location = self.current_location
        self.current_location = location
        self.add_memory(
            "observation",
            f"Moved from {old_location} to {location}",
            {"from": old_location, "to": location}
        )
    
    def __repr__(self) -> str:
        return f"NPCAgent(name='{self.name}', location='{self.current_location}')"
