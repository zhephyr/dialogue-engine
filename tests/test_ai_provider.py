import pytest
from unittest.mock import patch, MagicMock
from ai_provider import MockProvider, OpenAIProvider, AnthropicProvider, get_ai_provider
import os

def test_mock_provider_response():
    provider = MockProvider()
    response = provider.generate_response("You are TestChar, what happened here?")
    assert "TestChar responds" in response
    assert "Mock AI" in response

def test_mock_provider_fallback_response():
    provider = MockProvider()
    response = provider.generate_response("Who are you?")
    assert "Mock AI Response" in response

@patch.dict(os.environ, {"AI_PROVIDER": "", "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""}, clear=True)
def test_get_ai_provider_factory_mock():
    provider = get_ai_provider()
    assert isinstance(provider, MockProvider)

@patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": "fake_key"}, clear=True)
def test_get_ai_provider_factory_openai():
    provider = get_ai_provider()
    assert isinstance(provider, OpenAIProvider)
    assert provider.api_key == "fake_key"

@patch.dict(os.environ, {"AI_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "fake_key"}, clear=True)
def test_get_ai_provider_factory_anthropic():
    provider = get_ai_provider()
    assert isinstance(provider, AnthropicProvider)
    assert provider.api_key == "fake_key"

def test_openai_provider_missing_dependency(mocker):
    # Test error handling when the package isn't physically present or API key missing
    provider = OpenAIProvider(api_key=None)
    res = provider.generate_response("test")
    assert "OpenAI not configured" in res

def test_anthropic_provider_missing_dependency(mocker):
    # Test error handling when the package isn't physically present or API key missing
    provider = AnthropicProvider(api_key=None)
    res = provider.generate_response("test")
    assert "Anthropic not configured" in res

def test_openai_provider_generate_response_mocked(mocker):
    # Mocking openai.OpenAI client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "I am a mocked OpenAI response"
    mock_client.chat.completions.create.return_value = mock_response

    provider = OpenAIProvider(api_key="test_key")
    provider.client = mock_client
    
    result = provider.generate_response("Hello")
    assert result == "I am a mocked OpenAI response"
    mock_client.chat.completions.create.assert_called_once()

def test_anthropic_provider_generate_response_mocked(mocker):
    # Mocking anthropic.Anthropic client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_content = MagicMock()
    mock_content.text = "I am a mocked Anthropic response"
    mock_response.content = [mock_content]
    mock_client.messages.create.return_value = mock_response

    provider = AnthropicProvider(api_key="test_key")
    provider.client = mock_client
    
    result = provider.generate_response("Hello")
    assert result == "I am a mocked Anthropic response"
    mock_client.messages.create.assert_called_once()
