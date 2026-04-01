"""
Dialogue Engine

Main engine that orchestrates conversations between the player and NPCs.
Handles AI generation, fact-checking, and memory management.
"""

import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
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
        verbose: bool = False,
        log_file: Optional[str] = None,
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
        self.ai_provider = ai_provider or get_ai_provider()
        self.fact_checker = (
            FactChecker(self.world_state, self.ai_provider)
            if enable_fact_checking
            else None
        )
        self.verbose = verbose
        self.log_file = log_file
        self.current_scene = ""

        # Token metrics
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0

        if self.log_file and not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("")

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
        for fact in knowledge["known_facts"]:
            npc.add_known_fact(fact["key"], fact["value"])

        # Update witnessed events
        for event in knowledge["known_events"]:
            npc.add_witnessed_event(event["id"])

    async def converse(
        self, npc_name: str, player_message: str, player_name: str = "Player"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Have a conversation turn with an NPC.

        Args:
            npc_name: Name of the NPC to talk to
            player_message: What the player said
            player_name: Name to use for the player

        Yields:
            Dicts representing status updates, dialogue chunks, and metadata.
        """
        npc = self.get_npc(npc_name)
        if not npc:
            yield {
                "type": "dialogue_chunk",
                "chunk": f"[Error: NPC '{npc_name}' not found]",
            }
            yield {"type": "metadata", "data": {"error": "NPC not found"}}
            return

        # Sync NPC knowledge with world state
        self.sync_npc_knowledge(npc)

        # Get character knowledge, filtered to just the current scene to save tokens
        character_knowledge = self.world_state.export_character_knowledge(
            npc.name, self.current_scene
        )

        # Record player's message
        npc.add_conversation_turn(player_name, player_message)

        # Generate AI prompt with character knowledge
        prompt = npc.get_dialogue_prompt(
            player_message, self.current_scene, character_knowledge
        )

        if self.verbose:
            print(f"\n[Engine] Generating response for {npc.name}")
            print(f"[Engine] Player said: {player_message}")

        yield {"type": "status", "status": "thinking"}

        # Get AI response via stream
        npc_response_chunks = []
        MAX_TURNS = 3
        turn_count = 0

        while turn_count < MAX_TURNS:
            turn_count += 1
            buffer = ""
            in_tool_tag = False
            tool_json_str = ""
            tool_executed = False

            async for chunk in self.ai_provider.generate_response_stream(prompt):
                buffer += chunk
                while buffer:
                    if not in_tool_tag:
                        tool_start = buffer.find("<tool>")
                        if tool_start != -1:
                            if tool_start > 0:
                                safe_chunk = buffer[:tool_start]
                                npc_response_chunks.append(safe_chunk)
                                yield {"type": "dialogue_chunk", "chunk": safe_chunk}
                                prompt += safe_chunk
                            buffer = buffer[tool_start + 6 :]
                            in_tool_tag = True
                        else:
                            potential_start = buffer.rfind("<")
                            if potential_start != -1 and "<tool>".startswith(
                                buffer[potential_start:]
                            ):
                                if potential_start > 0:
                                    safe_chunk = buffer[:potential_start]
                                    npc_response_chunks.append(safe_chunk)
                                    self._log_event(
                                        {
                                            "type": "dialogue_chunk",
                                            "chunk": safe_chunk,
                                            "speaker": npc.name,
                                        }
                                    )
                                    yield {
                                        "type": "dialogue_chunk",
                                        "chunk": safe_chunk,
                                    }
                                    prompt += safe_chunk
                                buffer = buffer[potential_start:]
                                break
                            else:
                                npc_response_chunks.append(buffer)
                                self._log_event(
                                    {
                                        "type": "dialogue_chunk",
                                        "chunk": buffer,
                                        "speaker": npc.name,
                                    }
                                )
                                yield {"type": "dialogue_chunk", "chunk": buffer}
                                prompt += buffer
                                buffer = ""
                    else:
                        tool_end = buffer.find("</tool>")
                        if tool_end != -1:
                            tool_json_str += buffer[:tool_end]
                            try:
                                import json
                                from npc_tools import execute_tool

                                tool_data = json.loads(tool_json_str)
                                tool_name = tool_data.get("capability")
                                kwargs = tool_data.get("kwargs", {})
                                # Injects responsible_npc dynamically into kwargs
                                kwargs["responsible_npc"] = npc.name
                                result = execute_tool(
                                    tool_name, npc, self.world_state, kwargs
                                )
                                event = {
                                    "type": "tool_execution",
                                    "tool_name": tool_name,
                                    "kwargs": kwargs,
                                    "result": result,
                                    "speaker": npc.name,
                                }
                                self._log_event(event)
                                yield event
                                prompt += f"\\n\\n[System: Tool '{tool_name}' returned: {result}]\\nContinue your response naturally:\\n"
                            except Exception as e:
                                prompt += f"\\n\\n[System: Tool Error: {e}]\\nContinue your response naturally:\\n"

                            buffer = buffer[tool_end + 7 :]
                            in_tool_tag = False
                            tool_json_str = ""
                            tool_executed = True
                            break
                        else:
                            tool_json_str += buffer
                            buffer = ""

                if tool_executed:
                    break

            # If we didn't execute a tool, we finished generating
            if not tool_executed:
                if buffer and not in_tool_tag:
                    npc_response_chunks.append(buffer)
                    self._log_event(
                        {"type": "dialogue_chunk", "chunk": buffer, "speaker": npc.name}
                    )
                    yield {"type": "dialogue_chunk", "chunk": buffer}
                break

        npc_response = "".join(npc_response_chunks)

        # Track Tokens
        if hasattr(self.ai_provider, "get_token_usage"):
            tu = self.ai_provider.get_token_usage()
            self.total_prompt_tokens = tu.get("prompt_tokens", 0)
            self.total_completion_tokens = tu.get("completion_tokens", 0)

        if self.verbose:
            print(f"\n[Engine] {npc.name} responded: {npc_response}")

        # Record NPC's response
        npc.add_conversation_turn(npc.name, npc_response)

        # Fact-check the response if enabled
        metadata = {
            "npc_name": npc.name,
            "validation_enabled": self.fact_checker is not None,
        }

        if self.fact_checker:
            # For phase 1, we run fact checking concurrently but yield the result at the end.
            # IntentionAnalyzer is synchronous, let's run it in a thread
            def run_fact_checking():
                likely_lies, likely_omissions = IntentionAnalyzer.analyze_for_deception(
                    npc_response, npc, self.world_state, self.ai_provider
                )

                is_valid, validation_results = self.fact_checker.validate_statement(
                    npc_response,
                    npc,
                    marked_lies=likely_lies,
                    marked_omissions=likely_omissions,
                )
                return likely_lies, likely_omissions, is_valid, validation_results

            (
                likely_lies,
                likely_omissions,
                is_valid,
                validation_results,
            ) = await asyncio.to_thread(run_fact_checking)

            # Track lies and omissions in NPC memory
            for result in validation_results:
                if result.is_lie:
                    npc.add_memory(
                        "lie",
                        f"Lied: {result.claim['claim_text']}",
                        {"player_message": player_message, "reason": result.reason},
                    )
                elif result.is_omission:
                    npc.add_memory(
                        "omission",
                        f"Omitted information related to: {result.claim['claim_text']}",
                        {"player_message": player_message},
                    )

            metadata.update(
                {
                    "is_valid": is_valid,
                    "validation_results": [
                        {
                            "claim": r.claim["claim_text"],
                            "is_valid": r.is_valid,
                            "is_lie": r.is_lie,
                            "is_omission": r.is_omission,
                            "reason": r.reason,
                        }
                        for r in validation_results
                    ],
                    "likely_lies": likely_lies,
                    "likely_omissions": likely_omissions,
                }
            )

            if self.verbose and validation_results:
                print("[Engine] Validation results:")
                for result in validation_results:
                    status = "✓" if result.is_valid else "✗"
                    flag = (
                        " [LIE]"
                        if result.is_lie
                        else (" [OMISSION]" if result.is_omission else "")
                    )
                    print(f"  {status} {result.claim['claim_text']}{flag}")

        self._log_event({"type": "metadata", "data": metadata})
        yield {"type": "metadata", "data": metadata}

        # After conversation turn, conditionally compact memory to save context limits
        await self.compact_conversation_if_needed(npc)

    async def compact_conversation_if_needed(
        self, npc: NPCAgent, max_turns=30, condense_amount=16
    ) -> None:
        """
        Background task to condense conversation history if it exceeds max_turns.
        """
        # Note: conversation_history stores individual entries (both player and NPC turns)
        if len(npc.conversation_history) > max_turns:
            turns_to_condense = npc.conversation_history[:condense_amount]
            npc.conversation_history = npc.conversation_history[condense_amount:]

            transcript = "\\n".join(
                [f"{t['speaker']}: {t['message']}" for t in turns_to_condense]
            )
            prompt = f"Summarize the following conversation segment concisely in 1-3 bullet points. Focus purely on facts discussed, claims made, and important conclusions.\\n\\n{transcript}\\n\\nSummary:"

            # Since mock provider doesn't really summarize, we just get some output stream
            chunks = []
            async for chunk in self.ai_provider.generate_response_stream(prompt):
                chunks.append(chunk)

            summary_text = "".join(chunks).strip()

            npc.add_memory(
                "dialogue_summary",
                summary_text,
                {"condensed_turns": len(turns_to_condense)},
            )

            if self.verbose:
                print(
                    f"[Engine] Compacted {len(turns_to_condense)} turns of conversation for {npc.name}."
                )

    def _log_event(self, event: Dict[str, Any]) -> None:
        """Internal helper to log engine streams to jsonl."""
        if not self.log_file:
            return
        try:
            import json

            # Append local time
            from datetime import datetime

            event_copy = dict(event)
            event_copy["timestamp"] = datetime.now().isoformat()
            with open(self.log_file, "a") as f:
                f.write(json.dumps(event_copy) + "\n")
        except Exception as e:
            if self.verbose:
                print(f"[Engine] Failed to log event: {e}")

    def get_conversation_history(
        self, npc_name: str, num_turns: int = 10
    ) -> List[Dict[str, str]]:
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
            {"timestamp": lie.timestamp, "content": lie.content, "context": lie.context}
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
                "context": omit.context,
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
            "goals": npc.goals,
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
            "ai_provider": self.ai_provider.__class__.__name__,
            "token_usage": {
                "prompt_tokens": self.total_prompt_tokens,
                "completion_tokens": self.total_completion_tokens,
                "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            },
        }

        if self.fact_checker:
            stats["fact_checking"] = self.fact_checker.get_validation_summary()

        return stats
