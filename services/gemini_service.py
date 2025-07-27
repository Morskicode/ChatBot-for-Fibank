"""
Google Gemini AI service

This service handles Google Gemini AI integration for intelligent response generation
with proper error handling and fallback mechanisms.
"""

import os
import logging
from typing import Dict, List, Any, Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Google Gemini AI service for intelligent response generation
    
    This service manages Google Gemini AI model initialization and response generation
    with comprehensive error handling and fallback mechanisms.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = 'gemini-1.5-flash'):
        """
        Initialize Gemini service
        
        Args:
            api_key: Google Gemini API key (if None, will try to load from environment)
            model_name: Name of the Gemini model to use
        """
        self.model_name = model_name
        self.model = None
        self.is_available = False
        
        # Check if Gemini is available
        if genai is None:
            logger.error("google-generativeai not available. Install with: pip install google-generativeai")
            return
        
        # Get API key from parameter or environment
        if api_key is None:
            api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        
        self._setup_model(api_key)
    
    def _setup_model(self, api_key: str):
        """
        Setup Google Gemini AI model
        
        Args:
            api_key: Google Gemini API key
        """
        try:
            # Check if API key is properly configured
            if not api_key or api_key == 'your_gemini_api_key_here':
                logger.warning("Gemini API key not configured")
                return
            
            # Configure Gemini AI with the API key
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.is_available = True
            
            logger.info(f"Gemini model '{self.model_name}' configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup Gemini AI: {e}")
            self.model = None
            self.is_available = False
    
    def generate_response(self, prompt: str, max_retries: int = 2) -> Optional[str]:
        """
        Generate response using Gemini AI
        
        Args:
            prompt: Input prompt for Gemini
            max_retries: Maximum number of retries on failure
            
        Returns:
            Generated response text or None if failed
        """
        if not self.is_available or not self.model:
            logger.warning("Gemini service not available")
            return None
        
        for attempt in range(max_retries + 1):
            try:
                response = self.model.generate_content(prompt)
                
                if response and response.text:
                    logger.info(f"Gemini response generated successfully (attempt {attempt + 1})")
                    return response.text.strip()
                else:
                    logger.warning(f"Empty response from Gemini (attempt {attempt + 1})")
                    
            except Exception as e:
                logger.error(f"Error generating Gemini response (attempt {attempt + 1}): {e}")
                
                # If it's the last attempt, log and return None
                if attempt == max_retries:
                    logger.error("All Gemini generation attempts failed")
                    return None
        
        return None
    
    def create_structured_prompt(self, 
                                user_input: str, 
                                language: str, 
                                relevant_products: List, 
                                recent_context: List) -> str:
        """
        Create structured prompt for Gemini AI
        
        Args:
            user_input: User's current question
            language: Detected language (en/bg)
            relevant_products: List of semantically relevant products
            recent_context: Recent conversation history
            
        Returns:
            Structured prompt string for Gemini AI
        """
        # Define system instruction based on detected language
        if language == "bg":
            system_prompt = """Ти си AI асистент на Първа инвестиционна банка АД (Fibank). 
            Отговаряй на въпросите на клиентите относно кредитни карти и кредити.
            Бъди професионален, полезен и приветлив. Използвай информацията за продуктите, която ти е предоставена.
            Винаги предоставяй точна информация и насърчавай клиентите да се свържат с банката за повече детайли."""
        else:
            system_prompt = """You are an AI assistant for First Investment Bank AD (Fibank).
            Answer customer questions about credit cards and loans.
            Be professional, helpful, and friendly. Use the product information provided to you.
            Always provide accurate information and encourage customers to contact the bank for more details."""
        
        # Build context from recent conversation
        context_text = ""
        if recent_context:
            context_text = "\nRecent conversation:\n"
            for turn in recent_context[-3:]:  # Only last 3 turns
                user_msg = turn.get('user', '')
                if user_msg:
                    context_text += f"User: {user_msg}\n"
        
        # Build product information context
        products_text = ""
        if relevant_products:
            if language == "bg":
                products_text = "\nРелевантни продукти на Fibank:\n"
            else:
                products_text = "\nRelevant Fibank products:\n"
                
            for _, product, score in relevant_products[:3]:  # Only top 3 products
                products_text += f"- {product['name']}: {product['description'][:200]}...\n"
        
        # Additional guidelines
        if language == "bg":
            guidelines = """
            
Указания:
- Отговори директно на въпроса на клиента
- Ако питането е за конкретен продукт, предостави подробна информация
- Ако не знаеш точен отговор, препоръчай да се свържат с банката
- Винаги завършвай с информация за контакт: *2265 или 119 клона в България
- Бъди кратък и ясен в отговорите си"""
        else:
            guidelines = """
            
Guidelines:
- Answer the customer's question directly
- If asking about a specific product, provide detailed information
- If you don't know the exact answer, recommend contacting the bank
- Always end with contact information: *2265 or 119 branches in Bulgaria
- Keep responses concise and clear"""
        
        # Combine all components into final prompt
        full_prompt = f"""{system_prompt}
        
{context_text}
{products_text}
{guidelines}

User question: {user_input}

Response:"""
        
        return full_prompt
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get service status information
        
        Returns:
            Dictionary with service status details
        """
        return {
            "available": self.is_available,
            "model_name": self.model_name,
            "api_key_configured": bool(os.getenv('GOOGLE_GEMINI_API_KEY')),
            "genai_installed": genai is not None
        } 