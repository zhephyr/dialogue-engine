"""
Tests for the FactChecker module.

This module validates:
- Claim extraction from NPC statements (with and without AI)
- Claim validation against world truth (true, false-unintentional, false-intentional)
- IntentionAnalyzer's deception detection via mocking

The `populated_world` fixture is defined in conftest.py.
"""

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
    Here we mock the method to simulate an AI-detected lie about a secret meeting.
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
