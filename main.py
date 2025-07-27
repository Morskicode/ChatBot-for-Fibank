#!/usr/bin/env python3
"""
Fibank Chatbot - Main Entry Point (Modular Version)

A sophisticated banking chatbot for First Investment Bank AD (Fibank) built with
a modular architecture for enhanced maintainability and extensibility.

Features:
- Modular architecture with separated concerns
- Google Gemini AI integration with fallback
- Bilingual support (English/Bulgarian)
- Semantic search with lazy loading
- Configuration-driven intent recognition
- Unified rendering service
- Comprehensive error handling and logging
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fibank_chatbot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    Main function to run the modular chatbot
    
    Entry point that initializes the modular chatbot and starts the conversation.
    Includes proper error handling for initialization and runtime errors.
    """
    try:
        # Import the modular chatbot
        from core.chatbot import FibankChatbot
        
        # Initialize chatbot with modular components
        print("🏦 Starting Fibank Chatbot (Modular Version)...")
        chatbot = FibankChatbot()
        
        # Start interactive conversation
        chatbot.start_conversation()
            
    except KeyboardInterrupt:
        print(f"\n👋 Chatbot interrupted by user")
        logger.info("Chatbot interrupted by user")
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Please make sure all required packages are installed:")
        print("pip install -r requirements.txt")
        logger.error(f"Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 