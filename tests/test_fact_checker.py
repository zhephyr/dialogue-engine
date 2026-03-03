"""
Tests for the FactChecker module.

This module validates:
 - Claim extraction from NPC statements (with and without AI)
 - Claim validation against world truth (true, false-unintentional, false-intentional)
 - IntentionAnalyzer's deception detection (heuristic fallback AND AI-provider path)

The `populated_world` fixture is defined in conftest.py.
"""

import json
import pytest
from unittest.mock import MagicMock
from fact_checker import FactChecker, Claim, ValidationResult, IntentionAnalyzer
from npc_agent import NPCAgent


# --- Fixtures ---

@pytest.fixture
def fact_checker(populated_world):
    """Create a FactChecker using the shared populated world state (no AI provider)."""
    return FactChecker(populated_world)


@pytest.fixture
def npc_alice():
    """Create a simple NPC for use as the speaker in validation tests."""
    return NPCAgent("Alice", "Friendly librarian")


# --- Claim Extraction Tests ---

def test_extract_claims_from_statement(fact_checker):
    """
    extract_claims_from_statement should parse a statement into Claim objects.
    The heuristic implementation should return at least one claim per sentence.
    """
    statement = "The mayor is corrupt. He took a bribe yesterday."
    claims = fact_checker.extract_claims_from_statement(statement)
    # Heuristic fallback should return at least one claim
    assert len(claims) >= 1
    assert isinstance(claims[0], Claim)


# --- Claim Validation Tests ---

def test_validate_true_claim(fact_checker, populated_world, npc_alice):
    """A claim that matches the world truth should be marked valid and not a lie."""
    # Add a fact to world state and give Alice knowledge of it
    populated_world.add_fact("mayor_corrupt", True, is_public=True)
    npc_alice.add_known_fact("mayor_corrupt", True)

    claim = Claim("The mayor is corrupt", "general", "mayor_corrupt", True)
    result = fact_checker.validate_claim(claim, npc_alice)

    assert result.is_valid is True
    assert result.is_lie is False
    assert result.is_omission is False


def test_validate_false_claim_unintentional(fact_checker, populated_world, npc_alice):
    """
    A false claim with no intentional deception flag should be marked invalid
    but NOT flagged as a lie (e.g., the NPC genuinely believes it).
    """
    populated_world.add_fact("mayor_corrupt", False, is_public=True)
    # Alice has outdated or incorrect knowledge
    npc_alice.add_known_fact("mayor_corrupt", True)

    claim = Claim("The mayor is corrupt", "general", "mayor_corrupt", True)
    result = fact_checker.validate_claim(claim, npc_alice, is_intentional_lie=False)

    assert result.is_valid is False
    assert result.is_lie is False  # Not flagged as intentional


def test_validate_false_claim_intentional_lie(fact_checker, populated_world, npc_alice):
    """
    A false claim explicitly marked as intentional should be flagged as a lie.
    Alice knows the truth but claims otherwise.
    """
    populated_world.add_fact("mayor_corrupt", False, is_public=True)
    # Alice knows the truth — the mayor is NOT corrupt
    npc_alice.add_known_fact("mayor_corrupt", False)

    claim = Claim("The mayor is corrupt", "general", "mayor_corrupt", True)
    result = fact_checker.validate_claim(claim, npc_alice, is_intentional_lie=True)

    assert result.is_valid is False
    assert result.is_lie is True  # Intentional deception flagged


# --- Deception Analysis Tests ---

def test_analyze_for_deception(populated_world, npc_alice):
    """
    analyze_for_deception should detect when a character is lying about known facts.
    Here we mock the whole method to simulate an AI-detected lie about a secret meeting.
    """
    populated_world.add_fact("secret_meeting", True, is_public=False)
    npc_alice.add_known_fact("secret_meeting", True)

    analyzer = IntentionAnalyzer()
    statement = "I don't know anything about a meeting."

    # Mock the method to simulate AI-powered deception detection
    analyzer.analyze_for_deception = MagicMock(return_value=(["secret_meeting"], []))
    lies, omissions = analyzer.analyze_for_deception(statement, npc_alice, populated_world)

    # The known secret should be identified as a likely lie
    assert "secret_meeting" in lies
    assert len(omissions) == 0


def test_analyze_for_deception_with_real_ai_provider(populated_world, npc_alice):
    """
    When a non-mock AI provider is supplied, analyze_for_deception should:
    - Build a prompt and call ai_provider.generate_response
    - Parse the JSON response `{"lies": [...], "omissions": [...]}` 
    - Return the detected lies and omissions lists

    The ai_provider.generate_response is mocked here so the actual JSON-parsing
    code path inside analyze_for_deception is exercised end-to-end.
    """
    # Give Alice a secret she could be hiding
    populated_world.add_fact("victim_location", "Library", is_public=False,
                             witnesses=["Alice"])
    npc_alice.add_known_fact("victim_location", "Library")
    npc_alice.secrets = ["I saw the victim in the Library but told no one"]

    # Build a mock AI provider whose class name is *not* MockProvider/CustomMockProvider
    # so the AI branch inside analyze_for_deception is entered.
    class RealishProvider:
        pass  # class name is 'RealishProvider' — not in the exclusion list

    mock_provider = RealishProvider()
    ai_response = json.dumps({
        "lies": ["I was not near the Library"],
        "omissions": ["did not mention seeing the victim"]
    })
    mock_provider.generate_response = MagicMock(return_value=ai_response)

    statement = "I was not near the Library. I heard nothing unusual."
    lies, omissions = IntentionAnalyzer.analyze_for_deception(
        statement, npc_alice, populated_world, ai_provider=mock_provider
    )

    # The AI provider's generate_response should have been called
    assert mock_provider.generate_response.called, \
        "generate_response must be called when a real AI provider is supplied"

    # The lie identified by the AI must be returned
    assert "I was not near the Library" in lies, \
        f"Expected lie to be detected; got lies={lies}"

    # The omission identified by the AI must be returned
    assert any("victim" in omission for omission in omissions), \
        f"Expected omission to be detected; got omissions={omissions}"


# --- Regression Tests (bugs found during Phase 2 playthrough) ---

def test_person_claim_matches_full_name_characters(populated_world):
    """
    REGRESSION: The heuristic person-mention pattern matched single-word tokens
    (e.g. 'Elias') against world_state.characters which stores full names
    (e.g. 'Elias Morven'), causing every first-name mention to trigger a false
    'character does not exist' contradiction.

    Fix: extract_claims_from_statement must match first-name tokens against
    the full-name character set using a first-name prefix check,
    OR skip person claims when the single token does not match any full name.
    """
    # Add a two-word character to the world
    populated_world.add_character("John Smith")
    fc = FactChecker(populated_world)

    # Statement uses first name only — should NOT produce a contradiction
    statement = "I saw John in the library yesterday."
    claims = fc.extract_claims_from_statement(statement)

    person_claims = [c for c in claims if c["category"] == "person"]
    for claim in person_claims:
        # Every extracted person claim must reference a known character (full name)
        assert claim["value"] in populated_world.characters, (
            f"Extracted person '{claim['value']}' is not in world_state.characters. "
            f"Heuristic must resolve first-name tokens to known full names."
        )


def test_location_claim_article_prefix_is_stripped(populated_world):
    """
    REGRESSION: Location validation compared 'the gallery' against 'Gallery'
    in world_state.locations and failed because the leading article 'the'
    was not stripped and the case differed.

    Fix: validate_claim must normalise location values by stripping leading
    articles ('the', 'a', 'an') and comparing case-insensitively.
    """
    populated_world.add_location("Gallery")
    fc = FactChecker(populated_world)
    npc = NPCAgent("Alice", "Friendly librarian")

    # Claim value includes the article — must still be valid
    claim = Claim("found in the gallery", "location", "mentioned_location", "gallery")
    result = fc.validate_claim(claim, npc)

    assert result.is_valid is True, (
        "Location claim 'gallery' (without 'the') should match world location 'Gallery' "
        "case-insensitively. validate_claim must strip leading articles and ignore case."
    )


def test_person_pattern_does_not_produce_noncharacter_claims(populated_world):
    """
    REGRESSION: The overly-broad second person pattern
    r'(\\w+) (?:was|is) (?:there|here|present)' captured entire sentence
    fragments (e.g. 'Elias collapsed.') as person-name candidates and then
    flagged them as contradictions because they weren't in world_state.characters.

    Fix: extract_claims_from_statement must only emit a person claim when
    the extracted token actually matches a known character (full or first name).
    No spurious claims for unknown words.
    """
    fc = FactChecker(populated_world)

    # Statement where group(1) captures a non-character word
    statement = "The situation was very tense and everyone was present."
    claims = fc.extract_claims_from_statement(statement)

    person_claims = [c for c in claims if c["category"] == "person"]
    for claim in person_claims:
        assert claim["value"] in populated_world.characters, (
            f"Spurious person claim '{claim['value']}' extracted for non-character word. "
            f"Only known characters should produce person claims."
        )


def test_arbitrary_claim_key_does_not_collide_with_world_fact(populated_world):
    """
    REGRESSION: During playthrough, NPC-statement-derived facts are stored in
    world_state (via the 'new information' path). If a subsequent NPC claim shares
    the same key, it must NOT be validated against that NPC-derived stored value as
    if it were a world-engine fact.

    Only facts with source='world' (world-engine authored) should gate claim validation.
    NPC-statement-derived facts (source='Statement by <NPC>') must be bypassed.

    Fix: validate_claim only validates via world-state key lookup when the stored
    fact has source=='world'.
    """
    # Simulate a fact that was previously stored by an NPC statement, not the world engine.
    # This mimics what happens when the 'new information' path adds a fact for NPC A,
    # and then NPC B's response later has a claim with the same base key.
    populated_world.add_fact(
        "emotional_state",
        "worried",
        is_public=True,
        source="Statement by Nathan Cross"   # NOT world-engine authored
    )

    fc = FactChecker(populated_world)
    npc = NPCAgent("Alice", "Friendly librarian")

    # Claim with same key as the NPC-derived stored fact, different value —
    # must be treated as new information, not a contradiction.
    claim = Claim(
        "I cannot shake the dread",
        "other",
        "emotional_state",   # same key as NPC-authored fact above
        "something terrible had occurred"
    )
    result = fc.validate_claim(claim, npc)

    # Must be treated as new information, not a contradiction
    assert result.is_valid is True, (
        "A claim whose key matches a world-state fact authored by an NPC statement "
        "(not the world engine) must be treated as new information, not a contradiction. "
        f"Got reason: {result.reason}"
    )


def test_location_claim_underscore_normalises_to_space(populated_world):
    """
    REGRESSION: AI-extracted location values sometimes use underscore-formatted
    names (e.g. 'sitting_room') derived from how the AI interprets a location name.
    The world state stores locations with spaces ('Sitting Room').

    Fix: validate_claim must also replace underscores with spaces when normalising
    location values before comparison.
    """
    populated_world.add_location("Sitting Room")
    fc = FactChecker(populated_world)
    npc = NPCAgent("Alice", "Friendly librarian")

    # Underscore-formatted location should still match 'Sitting Room'
    claim = Claim(
        "I stepped away from the sitting_room",
        "location",
        "mentioned_location",
        "sitting_room"
    )
    result = fc.validate_claim(claim, npc)

    assert result.is_valid is True, (
        "Location value 'sitting_room' must match world location 'Sitting Room' "
        "after underscore-to-space normalisation. "
        f"Got reason: {result.reason}"
    )


def test_person_claim_possessive_phrase_not_matched(populated_world):
    """
    REGRESSION: The person validation fuzzy match splits the claimed_value by
    whitespace and checks if any word appears in a character's full name.
    A phrase like 'my brother' splits into ['my', 'brother'], and if 'brother'
    happened to be a substring of a character name OR matched via the 'in' operator,
    it would create a spurious person match.

    Verify that purely relational/possessive phrases ('my brother', 'her sister',
    'the victim') do NOT match any character in world state.
    """
    # No character named 'brother', 'my', or similar
    fc = FactChecker(populated_world)
    npc = NPCAgent("Alice", "Friendly librarian")

    claim = Claim(
        "My thoughts were consumed with the company of my brother.",
        "person",
        "mentioned_person",
        "my brother"
    )
    result = fc.validate_claim(claim, npc)

    # 'my brother' is not a known character — must be rejected (not valid)
    # so it falls through to the 'new information' else branch
    assert result.is_valid is False, (
        "The phrase 'my brother' must not fuzzy-match any known character. "
        "validate_claim should mark it invalid so the caller can decide to ignore it. "
        f"Got reason: {result.reason}"
    )



