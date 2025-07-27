"""
Conversation context and state management module

This module handles conversation state, user preferences, and conversation memory
to maintain context across multiple interactions in the chatbot.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class ConversationContext:
    """
    Stores conversation context and state management

    This class manages the conversation state including user language preferences,
    conversation history, user interests, and memory for maintaining context
    across multiple interactions.
    """
    user_language: str = "en"  # Detected user language (en/bg)
    current_topic: Optional[str] = None  # Current conversation topic
    user_preferences: Dict[str, Any] = field(default_factory=dict)  # User-specific preferences
    conversation_history: List[Dict[str, str]] = field(default_factory=list)  # Full conversation log
    conversation_memory: Dict[str, Any] = field(default_factory=dict)  # Key-value memory store
    last_products_discussed: List[str] = field(default_factory=list)  # Recently mentioned products
    user_interests: List[str] = field(default_factory=list)  # Tracked user interests
    
    def add_to_memory(self, key: str, value: Any):
        """Add information to conversation memory for future reference"""
        self.conversation_memory[key] = value
    
    def get_from_memory(self, key: str, default: Any = None) -> Any:
        """Retrieve information from conversation memory with optional default"""
        return self.conversation_memory.get(key, default)
    
    def add_product_interest(self, product_key: str):
        """Track user interest in specific products to avoid duplicates"""
        if product_key not in self.user_interests:
            self.user_interests.append(product_key)
    
    def get_recent_context(self, turns: int = 3) -> List[Dict[str, str]]:
        """Get recent conversation context for maintaining conversation flow"""
        return self.conversation_history[-turns:] if self.conversation_history else [] 