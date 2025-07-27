"""
Internationalization utilities for language detection

This module provides language detection capabilities with Bulgarian-specific
optimizations for banking terminology.
"""

from langdetect import detect, LangDetectException
import logging

logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """
    Detect the language of user input with Bulgarian-specific optimizations
    
    Uses multiple detection methods:
    1. Bulgarian character detection (Cyrillic alphabet)
    2. Common Bulgarian banking term recognition  
    3. Fallback to langdetect library for edge cases
    
    Args:
        text: User input text to analyze
        
    Returns:
        Language code: 'bg' for Bulgarian, 'en' for English
    """
    if not text or not text.strip():
        return "en"  # Default to English for empty input
    
    # Check for Bulgarian characters (Cyrillic alphabet)
    bulgarian_chars = set('абвгдежзийклмнопрстуфхцчшщъьюя')
    text_lower = text.lower()
    
    # If any Bulgarian characters found, it's likely Bulgarian
    if any(char in bulgarian_chars for char in text_lower):
        return "bg"
    
    # Check for common Bulgarian banking terms (transliterated or mixed)
    bulgarian_words = {
        'заем', 'кредит', 'карта', 'лихва', 'банка', 'пари', 'плащане',
        'ипотека', 'потребителски', 'овърдрафт', 'филиал', 'клан',
        'документи', 'заявка', 'процес', 'онлайн', 'помощ', 'информация'
    }
    
    if any(word in text_lower for word in bulgarian_words):
        return "bg"
    
    # Fallback to langdetect library for ambiguous cases
    try:
        detected = detect(text)
        return detected if detected in ['en', 'bg'] else 'en'
    except LangDetectException:
        logger.warning(f"Language detection failed for text: '{text[:50]}...'")
        return "en"  # Default to English if detection fails 