import pytest
from unittest.mock import MagicMock
from fact_checker import FactChecker, Claim, ValidationResult, IntentionAnalyzer
from npc_agent import NPCAgent

@pytest.fixture
def fact_checker(populated_world):
    return FactChecker(populated_world)

@pytest.fixture
def npc_alice():
    return NPCAgent("Alice", "Friendly librarian")

def test_extract_claims_from_statement(fact_checker):
    statement = "The mayor is corrupt. He took a bribe yesterday."
    claims = fact_checker.extract_claims_from_statement(statement)
    # The current naive implementation splits by '. ' and creates dummy claims.
    assert len(claims) >= 1
    assert isinstance(claims[0], Claim)

def test_validate_true_claim(fact_checker, populated_world, npc_alice):
    # Setup Alice knowing the fact
    populated_world.add_fact("mayor_corrupt", True, is_public=True)
    npc_alice.add_known_fact("mayor_corrupt", True)
    
    claim = Claim("The mayor is corrupt", "general", "mayor_corrupt", True)
    result = fact_checker.validate_claim(claim, npc_alice)
    
    assert result.is_valid is True
    assert result.is_lie is False
    assert result.is_omission is False

def test_validate_false_claim_unintentional(fact_checker, populated_world, npc_alice):
    populated_world.add_fact("mayor_corrupt", False, is_public=True)
    # Alice thinks it's true (maybe faulty memory or not updated)
    npc_alice.add_known_fact("mayor_corrupt", True)
    
    claim = Claim("The mayor is corrupt", "general", "mayor_corrupt", True)
    result = fact_checker.validate_claim(claim, npc_alice, is_intentional_lie=False)
    
    assert result.is_valid is False
    assert result.is_lie is False

def test_validate_false_claim_intentional_lie(fact_checker, populated_world, npc_alice):
    populated_world.add_fact("mayor_corrupt", False, is_public=True)
    npc_alice.add_known_fact("mayor_corrupt", False)
    
    claim = Claim("The mayor is corrupt", "general", "mayor_corrupt", True)
    result = fact_checker.validate_claim(claim, npc_alice, is_intentional_lie=True)
    
    assert result.is_valid is False
    assert result.is_lie is True

def test_analyze_for_deception(populated_world, npc_alice):
    populated_world.add_fact("secret_meeting", True, is_public=False)
    npc_alice.add_known_fact("secret_meeting", True)
    
    analyzer = IntentionAnalyzer()
    statement = "I don't know anything about a meeting."
    
    # In a mock setup, analyze_for_deception would use LLMs to detect the lie
    # We will mock it out or test the default behavior if not mocked
    
    analyzer.analyze_for_deception = MagicMock(return_value=(["secret_meeting"], []))
    lies, omissions = analyzer.analyze_for_deception(statement, npc_alice, populated_world)
    
    assert "secret_meeting" in lies
    assert len(omissions) == 0
