"""
AI Provider Interface

Abstraction layer for different AI providers (OpenAI, Anthropic, etc.)
"""

import os
from typing import Optional
from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate a response from the AI"""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI API provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("Warning: openai package not installed. Install with: pip install openai")
    
    def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate a response using OpenAI"""
        if not self.client:
            return "[OpenAI not configured - please set OPENAI_API_KEY and install openai package]"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a character in a murder mystery game. Stay in character and respond naturally."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.8
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[OpenAI API Error: {str(e)}]"


class AnthropicProvider(AIProvider):
    """Anthropic (Claude) API provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
            except ImportError:
                print("Warning: anthropic package not installed. Install with: pip install anthropic")
    
    def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate a response using Anthropic Claude"""
        if not self.client:
            return "[Anthropic not configured - please set ANTHROPIC_API_KEY and install anthropic package]"
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"[Anthropic API Error: {str(e)}]"


class MockProvider(AIProvider):
    """Mock provider for testing without API keys"""
    
    def generate_response(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate a mock response"""
        # Extract character name from prompt
        if "You are " in prompt:
            char_name = prompt.split("You are ")[1].split(",")[0].strip()
            return f"[{char_name} responds - Mock AI: Please configure an AI provider]"
        return "[Mock AI Response - Please configure OPENAI_API_KEY or ANTHROPIC_API_KEY]"


def get_ai_provider(provider_name: Optional[str] = None, model: Optional[str] = None) -> AIProvider:
    """
    Factory function to get the appropriate AI provider.
    
    Args:
        provider_name: 'openai', 'anthropic', or None (auto-detect)
        model: Specific model to use, or None for default
    """
    if provider_name is None:
        provider_name = os.getenv("AI_PROVIDER", "").lower()
    
    # Auto-detect based on available API keys
    if not provider_name:
        if os.getenv("OPENAI_API_KEY"):
            provider_name = "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            provider_name = "anthropic"
        else:
            provider_name = "mock"
    
    # Get default model if not specified
    if model is None:
        model = os.getenv("AI_MODEL", "")
    
    # Create provider
    if provider_name == "openai":
        return OpenAIProvider(model=model or "gpt-4")
    elif provider_name == "anthropic":
        return AnthropicProvider(model=model or "claude-3-sonnet-20240229")
    else:
        return MockProvider()
