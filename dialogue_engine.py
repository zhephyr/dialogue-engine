"""
Dialogue Engine

Main engine that orchestrates conversations between the player and NPCs.
Handles AI generation, fact-checking, and memory management.
"""

from typing import Dict, List, Optional, Any, Tuple
from world_state import WorldState
from npc_agent import NPCAgent
from fact_checker import FactChecker, IntentionAnalyzer
from ai_provider import AIProvider, get_ai_provider
import os
from dotenv import load_dotenv


class DialogueEngine:
    """
    Main dialogue engine that manages conversations with NPCs.
    Ensures consistency, tracks lies, and maintains immersion.
    """
    
    def __init__(
        self,
        world_state: WorldState,
        ai_provider: Optional[AIProvider] = None,
        enable_fact_checking: bool = True,
        verbose: bool = False
    ):
        """
        Initialize the dialogue engine.
        
        Args:
            world_state: The game world state
            ai_provider: AI provider to use (auto-detected if None)
            enable_fact_checking: Whether to validate NPC claims
            verbose: Print debug information
        """
        load_dotenv()  # Load environment variables
        
        self.world_state = world_state
        self.npcs: Dict[str, NPCAgent] = {}
        self.fact_checker = FactChecker(world_state) if enable_fact_checking else None
        self.ai_provider = ai_provider or get_ai_provider()
        self.verbose = verbose
        self.current_scene = ""
        
        # Conversation state
        self.active_conversations: Dict[str, List[Dict[str, str]]] = {}
        
    def add_npc(self, npc: NPCAgent) -> None:
        """Register an NPC with the dialogue engine"""
        self.npcs[npc.name.lower()] = npc
        self.world_state.add_character(npc.name)
        
        if self.verbose:
            print(f"[Engine] Registered NPC: {npc.name}")
    
    def get_npc(self, npc_name: str) -> Optional[NPCAgent]:
        """Get an NPC by name (case-insensitive)"""
        return self.npcs.get(npc_name.lower())
    
    def set_scene(self, scene_description: str) -> None:
        """Set the current scene description"""
        self.current_scene = scene_description
        if self.verbose:
            print(f"[Engine] Scene updated: {scene_description}")
    
    def sync_npc_knowledge(self, npc: NPCAgent) -> None:
        """
        Synchronize an NPC's knowledge with what they should know from world state.
        """
        knowledge = self.world_state.export_character_knowledge(npc.name)
        
        # Update NPC's known facts
        for fact in knowledge['known_facts']:
            npc.add_known_fact(fact['key'], fact['value'])
        
        # Update witnessed events
        for event in knowledge['known_events']:
            npc.add_witnessed_event(event['id'])
    
    def converse(
        self,
        npc_name: str,
        player_message: str,
        player_name: str = "Player"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Have a conversation turn with an NPC.
        
        Args:
            npc_name: Name of the NPC to talk to
            player_message: What the player said
            player_name: Name to use for the player
        
        Returns:
            Tuple of (npc_response, metadata)
            metadata contains validation results, lies detected, etc.
        """
        npc = self.get_npc(npc_name)
        if not npc:
            return f"[Error: NPC '{npc_name}' not found]", {"error": "NPC not found"}
        
        # Sync NPC knowledge with world state
        self.sync_npc_knowledge(npc)
        
        # Record player's message
        npc.add_conversation_turn(player_name, player_message)
        
        # Generate AI prompt
        prompt = npc.get_dialogue_prompt(player_message, self.current_scene)
        
        if self.verbose:
            print(f"\n[Engine] Generating response for {npc.name}")
            print(f"[Engine] Player said: {player_message}")
        
        # Get AI response
        npc_response = self.ai_provider.generate_response(prompt)
        
        if self.verbose:
            print(f"[Engine] {npc.name} responded: {npc_response}")
        
        # Record NPC's response
        npc.add_conversation_turn(npc.name, npc_response)
        
        # Fact-check the response if enabled
        metadata = {
            "npc_name": npc.name,
            "validation_enabled": self.fact_checker is not None
        }
        
        if self.fact_checker:
            # Check for potential deceptions
            likely_lies, likely_omissions = IntentionAnalyzer.analyze_for_deception(
                npc_response, npc, self.world_state
            )
            
            # Validate the statement
            is_valid, validation_results = self.fact_checker.validate_statement(
                npc_response,
                npc,
                marked_lies=[],  # In a full implementation, these would come from AI
                marked_omissions=[]
            )
            
            # Track lies and omissions in NPC memory
            for result in validation_results:
                if result.is_lie:
                    npc.add_memory(
                        "lie",
                        f"Lied: {result.claim['claim_text']}",
                        {"player_message": player_message, "reason": result.reason}
                    )
                elif result.is_omission:
                    npc.add_memory(
                        "omission",
                        f"Omitted information related to: {result.claim['claim_text']}",
                        {"player_message": player_message}
                    )
            
            metadata.update({
                "is_valid": is_valid,
                "validation_results": [
                    {
                        "claim": r.claim['claim_text'],
                        "is_valid": r.is_valid,
                        "is_lie": r.is_lie,
                        "is_omission": r.is_omission,
                        "reason": r.reason
                    }
                    for r in validation_results
                ],
                "likely_lies": likely_lies,
                "likely_omissions": likely_omissions
            })
            
            if self.verbose and validation_results:
                print(f"[Engine] Validation results:")
                for result in validation_results:
                    status = "✓" if result.is_valid else "✗"
                    flag = " [LIE]" if result.is_lie else (" [OMISSION]" if result.is_omission else "")
                    print(f"  {status} {result.claim['claim_text']}{flag}")
        
        return npc_response, metadata
    
    def get_conversation_history(self, npc_name: str, num_turns: int = 10) -> List[Dict[str, str]]:
        """Get conversation history with an NPC"""
        npc = self.get_npc(npc_name)
        if not npc:
            return []
        return npc.get_recent_conversation(num_turns)
    
    def get_npc_lies(self, npc_name: str) -> List[Dict[str, Any]]:
        """Get all lies told by an NPC"""
        npc = self.get_npc(npc_name)
        if not npc:
            return []
        return [
            {
                "timestamp": lie.timestamp,
                "content": lie.content,
                "context": lie.context
            }
            for lie in npc.lies_told
        ]
    
    def get_npc_omissions(self, npc_name: str) -> List[Dict[str, Any]]:
        """Get all omissions made by an NPC"""
        npc = self.get_npc(npc_name)
        if not npc:
            return []
        return [
            {
                "timestamp": omit.timestamp,
                "content": omit.content,
                "context": omit.context
            }
            for omit in npc.omissions_made
        ]
    
    def get_all_npcs(self) -> List[str]:
        """Get names of all registered NPCs"""
        return [npc.name for npc in self.npcs.values()]
    
    def get_npc_status(self, npc_name: str) -> Optional[Dict[str, Any]]:
        """Get current status of an NPC"""
        npc = self.get_npc(npc_name)
        if not npc:
            return None
        
        return {
            "name": npc.name,
            "location": npc.current_location,
            "emotional_state": npc.emotional_state,
            "conversation_turns": len(npc.conversation_history),
            "memories": len(npc.memory),
            "lies_told": len(npc.lies_told),
            "omissions_made": len(npc.omissions_made),
            "secrets": npc.secrets,
            "goals": npc.goals
        }
    
    def reset_conversation(self, npc_name: str) -> bool:
        """Reset conversation history with an NPC"""
        npc = self.get_npc(npc_name)
        if not npc:
            return False
        
        npc.conversation_history = []
        if self.verbose:
            print(f"[Engine] Reset conversation with {npc.name}")
        return True
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get statistics about the dialogue engine"""
        stats = {
            "total_npcs": len(self.npcs),
            "npc_names": self.get_all_npcs(),
            "world_state": self.world_state.get_world_summary(),
            "ai_provider": self.ai_provider.__class__.__name__
        }
        
        if self.fact_checker:
            stats["fact_checking"] = self.fact_checker.get_validation_summary()
        
        return stats
