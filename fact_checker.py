"""
Fact Checker

Validates claims made by NPCs against the world state and tracks lies and omissions.
This ensures NPCs can't make up facts that contradict the established world.
"""

from typing import Dict, List, Any, Optional, Tuple
from world_state import WorldState
from npc_agent import NPCAgent
import re
import uuid
import json


class Claim(Dict):
    """Represents a factual claim extracted from dialogue"""
    def __init__(self, claim_text: str, category: str, key: str, value: Any):
        super().__init__()
        self['claim_text'] = claim_text
        self['category'] = category
        self['key'] = key
        self['value'] = value


class ValidationResult:
    """Result of validating a claim against world state"""
    def __init__(
        self,
        is_valid: bool,
        claim: Claim,
        reason: str,
        world_truth: Optional[Any] = None,
        is_lie: bool = False,
        is_omission: bool = False
    ):
        self.is_valid = is_valid
        self.claim = claim
        self.reason = reason
        self.world_truth = world_truth
        self.is_lie = is_lie
        self.is_omission = is_omission
    
    def __repr__(self) -> str:
        status = "VALID" if self.is_valid else ("LIE" if self.is_lie else "INVALID")
        return f"ValidationResult({status}: {self.claim['claim_text']})"


class FactChecker:
    """
    Validates NPC statements against the world state to ensure consistency.
    Tracks intentional lies and omissions.
    """
    
    def __init__(self, world_state: WorldState, ai_provider: Optional[Any] = None):
        self.world_state = world_state
        self.ai_provider = ai_provider
        self.validation_history: List[ValidationResult] = []
    
    def extract_claims_from_statement(self, statement: str) -> List[Claim]:
        """
        Extract factual claims from a statement.
        Uses an AIProvider if configured (and not mock), otherwise falls back 
        to pattern matching heuristics.
        """
        claims = []
        
        # Check if we should attempt AI-based extraction
        if self.ai_provider and self.ai_provider.__class__.__name__ not in ["MockProvider", "CustomMockProvider"]:
            prompt = f"""Extract standalone factual claims from this statement: "{statement}"
Return ONLY a valid JSON list of objects. Each object should have:
- claim_text: The exact string representing the claim
- category: 'location', 'time', 'person', 'event', or 'other'
- key: A simple snake_case key categorizing this fact (e.g., 'mentioned_location')
- value: The exact target of the claim
If no facts, return an empty list [].
JSON:"""
            try:
                ai_result = self.ai_provider.generate_response(prompt, max_tokens=300)
                # Cleanup potential markdown ticks
                content = ai_result.replace("```json", "").replace("```", "").strip()
                data = json.loads(content)
                if isinstance(data, list):
                    for item in data:
                        claims.append(Claim(
                            claim_text=item.get("claim_text", statement),
                            category=item.get("category", "other"),
                            key=item.get("key", "unknown"),
                            value=item.get("value", "")
                        ))
                    return claims
            except Exception as e:
                # Fall back to heuristic pattern matching if AI fails or returns invalid format
                pass
        
        # Pattern matching for common claim types
        # Location claims: "I was in the library", "I saw him in the garden"
        location_patterns = [
            r"(?:I (?:was|am)|he (?:was|is)|she (?:was|is)|they (?:were|are)) (?:in|at) (?:the )?(\w+)",
            r"(?:saw|found|met) (?:\w+ )?(?:in|at) (?:the )?(\w+)",
        ]
        
        for pattern in location_patterns:
            matches = re.finditer(pattern, statement, re.IGNORECASE)
            for match in matches:
                location = match.group(1)
                claims.append(Claim(
                    claim_text=match.group(0),
                    category="location",
                    key=f"mentioned_location",
                    value=location
                ))
        
        # Time claims: "at 9pm", "last night", "this morning"
        time_patterns = [
            r"at (\d{1,2}(?::\d{2})?\s*(?:am|pm))",
            r"(last night|this morning|yesterday|tonight)",
        ]
        
        for pattern in time_patterns:
            matches = re.finditer(pattern, statement, re.IGNORECASE)
            for match in matches:
                time_ref = match.group(1)
                claims.append(Claim(
                    claim_text=match.group(0),
                    category="time",
                    key=f"mentioned_time",
                    value=time_ref
                ))
        
        # Person mentions: "I saw John", "spoke with Mary"
        person_patterns = [
            r"(?:saw|met|spoke with|talked to) (\w+)",
            r"(\w+) (?:was|is) (?:there|here|present)",
        ]
        
        for pattern in person_patterns:
            matches = re.finditer(pattern, statement, re.IGNORECASE)
            for match in matches:
                person = match.group(1)
                # Only track if it's a known character
                if person in self.world_state.characters:
                    claims.append(Claim(
                        claim_text=match.group(0),
                        category="person",
                        key=f"mentioned_person",
                        value=person
                    ))
        
        return claims
    
    def validate_claim(
        self,
        claim: Claim,
        character: NPCAgent,
        is_intentional_lie: bool = False,
        is_intentional_omission: bool = False
    ) -> ValidationResult:
        """
        Validate a single claim against the world state.
        
        Args:
            claim: The claim to validate
            character: The NPC making the claim
            is_intentional_lie: Whether the character intends to lie
            is_intentional_omission: Whether the character intends to omit info
        """
        # Check if the claim matches world state
        category = claim['category']
        key = claim['key']
        claimed_value = claim['value']
        
        is_valid = False
        world_truth = None
        reason = ""
        
        # For location claims, verify the location exists
        if category == "location":
            if claimed_value.lower() in [loc.lower() for loc in self.world_state.locations]:
                is_valid = True
                reason = "Location exists in world"
                world_truth = claimed_value
            else:
                reason = f"Location '{claimed_value}' does not exist in world state"
        
        # For person mentions, verify the person exists
        elif category == "person":
            if claimed_value in self.world_state.characters:
                is_valid = True
                reason = "Character exists in world"
                world_truth = claimed_value
            else:
                reason = f"Character '{claimed_value}' does not exist in world state"
        
        # For specific fact keys, check against world state
        elif key in self.world_state.facts:
            world_truth = self.world_state.get_fact(key)
            if str(world_truth).lower() == str(claimed_value).lower():
                is_valid = True
                reason = "Matches world state fact"
            else:
                reason = f"Contradicts world state. Truth: {world_truth}"
        
        # Unknown claims are allowed (new information). We add these to the timeline.
        else:
            fact_key = key
            # Generate a unique key if it uses a generic key template
            if fact_key in ["mentioned_time", "mentioned_location", "mentioned_person"]:
                fact_key = f"{key}_{str(uuid.uuid4())[:8]}"
                
            self.world_state.add_fact(
                key=fact_key,
                value=claimed_value,
                category=category,
                is_public=True,
                witnesses=[character.name],
                source=f"Statement by {character.name}"
            )
            is_valid = True
            reason = "New information added to world state"
            world_truth = claimed_value
            
        # Check intentional omissions
        if is_intentional_omission:
            reason = "Intentional omission by character"
            
        # Check intentional lies
        if is_intentional_lie:
            reason = "Intentional lie by character"

        result = ValidationResult(
            is_valid=is_valid,
            claim=claim,
            reason=reason,
            world_truth=world_truth,
            is_lie=is_intentional_lie,
            is_omission=is_intentional_omission
        )
        
        self.validation_history.append(result)
        return result
    
    def validate_statement(
        self,
        statement: str,
        character: NPCAgent,
        marked_lies: Optional[List[str]] = None,
        marked_omissions: Optional[List[str]] = None
    ) -> Tuple[bool, List[ValidationResult]]:
        """
        Validate an entire statement from an NPC.
        
        Args:
            statement: The statement to validate
            character: The NPC making the statement
            marked_lies: List of specific claims marked as intentional lies
            marked_omissions: List of specific claims marked as intentional omissions
        
        Returns:
            Tuple of (is_valid, list of validation results)
        """
        marked_lies = marked_lies or []
        marked_omissions = marked_omissions or []
        
        # Extract claims
        claims = self.extract_claims_from_statement(statement)
        
        # Validate each claim
        results = []
        all_valid = True
        
        for claim in claims:
            is_lie = claim['claim_text'] in marked_lies
            is_omission = claim['claim_text'] in marked_omissions
            
            result = self.validate_claim(claim, character, is_lie, is_omission)
            results.append(result)
            
            if not result.is_valid and not result.is_lie:
                all_valid = False
        
        return all_valid, results
    
    def check_knowledge_consistency(self, character: NPCAgent, fact_key: str) -> bool:
        """
        Check if a character should know a particular fact based on world state.
        """
        return self.world_state.character_knows_fact(character.name, fact_key)
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of all validations performed"""
        total = len(self.validation_history)
        valid = len([r for r in self.validation_history if r.is_valid])
        lies = len([r for r in self.validation_history if r.is_lie])
        omissions = len([r for r in self.validation_history if r.is_omission])
        
        return {
            "total_validations": total,
            "valid_claims": valid,
            "invalid_claims": total - valid,
            "intentional_lies": lies,
            "omissions": omissions,
            "accuracy_rate": (valid / total * 100) if total > 0 else 0
        }


class IntentionAnalyzer:
    """
    Helper class to analyze if a statement contains intentional lies or omissions.
    In practice, this would work with the AI to identify deceptions.
    """
    
    @staticmethod
    def analyze_for_deception(
        statement: str,
        character: NPCAgent,
        world_state: WorldState,
        ai_provider: Optional[Any] = None
    ) -> Tuple[List[str], List[str]]:
        """
        Analyze a statement to identify potential lies and omissions.
        
        Returns:
            Tuple of (likely_lies, likely_omissions)
        """
        # Full Implementation Placeholder:
        # 1. Provide Context to AI provider
        # 2. Extract specific deceptive text blocks
        if ai_provider and ai_provider.__class__.__name__ not in ["MockProvider", "CustomMockProvider"]:
            # Setup AI prompt logic here
            pass

        likely_lies = []
        likely_omissions = []
        
        # Simple heuristic: check if character has secrets they might be hiding
        for secret in character.secrets:
            # If the secret is related to the statement topic, flag potential omission
            secret_words = set(secret.lower().split())
            statement_words = set(statement.lower().split())
            
            if len(secret_words & statement_words) > 0:
                # Character is talking about something related to their secret
                # Might be an omission
                likely_omissions.append(f"Potential omission related to: {secret}")
        
        return likely_lies, likely_omissions
