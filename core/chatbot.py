"""
Main chatbot core class

This module contains the main FibankChatbot class that orchestrates all
the modular components for a clean, maintainable architecture.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

from colorama import Fore, Back, Style, init

# Import modular components
from core.context import ConversationContext
from services.gemini_service import GeminiService
from services.semantic_service import SemanticService
from services.rendering_service import RenderingService
from utils.i18n import detect_language
from utils.config_loader import ConfigLoader

# Initialize colorama for cross-platform colored output
init(autoreset=True)

logger = logging.getLogger(__name__)


class FibankChatbot:
    """
    Enhanced modular chatbot class for Fibank
    
    This is the main chatbot class that orchestrates all functionality using
    a modular architecture for better maintainability and extensibility.
    """
    
    def __init__(self, config_dir: str = "config", data_dir: str = "data"):
        """
        Initialize the chatbot with modular components
        
        Args:
            config_dir: Directory containing configuration files
            data_dir: Directory containing data files
        """
        print(f"{Fore.BLUE}[BOT] Initializing Fibank Chatbot...")
        
        # Initialize configuration loader
        self.config_loader = ConfigLoader(config_dir)
        self.data_dir = data_dir
        
        # Initialize conversation context
        self.context = ConversationContext()
        
        # Initialize services
        self._initialize_services()
        
        # Load knowledge base and setup components
        self._setup_knowledge_base()
        self._setup_intent_patterns()
        self._setup_keywords()
        
        print(f"{Fore.GREEN}[OK] Fibank Chatbot ready!")
        logger.info("Chatbot initialization completed successfully")
    
    def _initialize_services(self):
        """Initialize all service components"""
        try:
            # Initialize Gemini service
            self.gemini_service = GeminiService()
            if self.gemini_service.is_available:
                print(f"{Fore.GREEN}✅ Gemini AI service configured successfully!")
            else:
                print(f"{Fore.YELLOW}⚠️  Gemini AI not available. Running in fallback mode.")
            
            # Initialize semantic service with lazy loading
            self.semantic_service = SemanticService()
            print(f"{Fore.GREEN}✅ Semantic service initialized!")
            
            # Initialize rendering service
            self.rendering_service = RenderingService()
            print(f"{Fore.GREEN}✅ Rendering service initialized!")
            
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            raise
    
    def _setup_knowledge_base(self):
        """Load and setup knowledge base from JSON files"""
        try:
            # Load credit cards data
            credit_cards_path = os.path.join(self.data_dir, 'credit_cards.json')
            with open(credit_cards_path, 'r', encoding='utf-8') as f:
                credit_cards = json.load(f)
            
            # Load credits data
            credits_path = os.path.join(self.data_dir, 'credits.json')
            with open(credits_path, 'r', encoding='utf-8') as f:
                credits = json.load(f)
            
            # Combine products into unified structure
            combined_products = self._combine_products(credit_cards, credits)
            
            # Create knowledge base structure
            self.knowledge_base = {
                "products": combined_products,
                "credit_cards": credit_cards,
                "credits": credits
            }
            
            # Set knowledge base for semantic service
            self.semantic_service.set_knowledge_base(self.knowledge_base)
            
            print(f"{Fore.GREEN}✅ Loaded {len(combined_products)} products from knowledge base")
            logger.info(f"Knowledge base loaded with {len(combined_products)} products")
            
        except FileNotFoundError as e:
            logger.error(f"Knowledge base file not found: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            raise
    
    def _combine_products(self, credit_cards: Dict, credits: Dict) -> Dict[str, Any]:
        """Combine and normalize products from JSON files"""
        combined = {}
        
        # Process credit cards
        for card_type, cards in credit_cards.items():
            for card_name, card_info in cards.items():
                key = card_name.replace('"', '').replace('„', '').replace('"', '')
                combined[key] = {
                    'name': card_name,
                    'type': 'credit_card',
                    'category': card_type,
                    'description': card_info.get('информация за продукта', ''),
                    'raw_data': card_info
                }
        
        # Process credits
        for credit_category, credit_types in credits.items():
            for credit_name, credit_info in credit_types.items():
                key = credit_name.replace('"', '').replace('„', '').replace('"', '')
                combined[key] = {
                    'name': credit_name,
                    'type': 'credit',
                    'category': credit_category,
                    'description': credit_info.get('информация за продукта', ''),
                    'raw_data': credit_info
                }
        
        return combined
    
    def _setup_intent_patterns(self):
        """Load and setup intent recognition patterns"""
        try:
            self.intent_patterns = self.config_loader.load_intent_patterns()
            logger.info(f"Loaded {len(self.intent_patterns)} intent patterns")
        except Exception as e:
            logger.warning(f"Error loading intent patterns: {e}")
            # Fall back to default patterns from config loader
            self.intent_patterns = self.config_loader._get_default_intent_patterns()
    
    def _setup_keywords(self):
        """Load and setup keyword configurations"""
        try:
            self.keywords = self.config_loader.load_keywords()
            logger.info("Keyword configurations loaded successfully")
        except Exception as e:
            logger.warning(f"Error loading keywords: {e}")
            # Fall back to default keywords from config loader
            self.keywords = self.config_loader._get_default_keywords()
    
    def find_intent(self, text: str) -> Tuple[str, float]:
        """Classify user intent using loaded patterns"""
        text_lower = text.lower()
        best_intent = "general"
        best_score = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern.search(text_lower):
                    # Simple scoring based on pattern matches
                    score = 0.8  # Fixed confidence for pattern matches
                    if score > best_score:
                        best_score = score
                        best_intent = intent
                        break
        
        return best_intent, best_score
    
    def handle_credit_card_inquiry(self, user_input: str) -> str:
        """Handle credit card inquiries using keywords and rendering service"""
        try:
            user_input_lower = user_input.lower()
            
            # Check for specific card types using loaded keywords
            visa_keywords = self.keywords.get('visa', {})
            mastercard_keywords = self.keywords.get('mastercard', {})
            
            # Check for specific Visa cards
            for card_type, keywords in visa_keywords.items():
                if any(keyword.lower() in user_input_lower for keyword in keywords):
                    return self._show_specific_card('Visa', f'Visa {card_type.title()}')
            
            # Check for specific Mastercard cards  
            for card_type, keywords in mastercard_keywords.items():
                if any(keyword.lower() in user_input_lower for keyword in keywords):
                    if card_type == 'first_lady':
                        return self._show_specific_card('Mastercard', 'Mastercard Platinum First Lady')
                    else:
                        return self._show_specific_card('Mastercard', f'Mastercard {card_type.title()}')
            
            # Check for general brand mentions
            brand_keywords = self.keywords.get('brands', {})
            visa_mentioned = any(keyword.lower() in user_input_lower 
                               for keyword in brand_keywords.get('visa', []))
            mastercard_mentioned = any(keyword.lower() in user_input_lower 
                                     for keyword in brand_keywords.get('mastercard', []))
            
            if visa_mentioned and not mastercard_mentioned:
                return self._show_brand_cards('Visa')
            elif mastercard_mentioned and not visa_mentioned:
                return self._show_brand_cards('Mastercard')
            else:
                return self._show_all_credit_cards()
                
        except Exception as e:
            logger.error(f"Error handling credit card inquiry: {e}")
            return self._generate_error_response()
    
    def handle_loan_inquiry(self, user_input: str) -> str:
        """Handle loan inquiries using keywords and rendering service"""
        try:
            user_input_lower = user_input.lower()
            
            # Check for specific loan types using loaded keywords
            loan_keywords = self.keywords.get('loans', {})
            
            mentioned_types = []
            for loan_type, keywords in loan_keywords.items():
                if any(keyword.lower() in user_input_lower for keyword in keywords):
                    mentioned_types.append(loan_type)
            
            # Map keyword types to actual category names
            category_mapping = {
                'housing': 'Жилищни и ипотечни кредити',
                'consumer': 'Потребителски кредити', 
                'overdraft': 'Овърдрафт',
                'other': 'Други кредити'
            }
            
            if len(mentioned_types) == 1:
                category = category_mapping.get(mentioned_types[0])
                if category:
                    return self._show_loan_category(category)
            
            # Show all categories if multiple or no specific type mentioned
            return self._show_all_loan_categories()
            
        except Exception as e:
            logger.error(f"Error handling loan inquiry: {e}")
            return self._generate_error_response()
    
    def _show_specific_card(self, brand: str, card_name: str) -> str:
        """Show specific card using rendering service"""
        try:
            card_data = self.knowledge_base.get('credit_cards', {}).get(brand, {}).get(card_name, {})
            
            if not card_data:
                if self.context.user_language == 'bg':
                    return f"{Fore.RED}Съжалявам, не намерих информация за {card_name}.{Style.RESET_ALL}"
                else:
                    return f"{Fore.RED}Sorry, I couldn't find information for {card_name}.{Style.RESET_ALL}"
            
            return self.rendering_service.render_specific_product(
                card_name, card_data, self.context.user_language
            )
            
        except Exception as e:
            logger.error(f"Error showing specific card {brand} {card_name}: {e}")
            return self._generate_error_response()
    
    def _show_brand_cards(self, brand: str) -> str:
        """Show all cards from a specific brand"""
        try:
            cards = self.knowledge_base.get('credit_cards', {}).get(brand, {})
            
            if self.context.user_language == 'bg':
                header = f"Всички налични {brand} карти от Fibank"
                link_label = "Повече информация"
            else:
                header = f"All available {brand} cards from Fibank"
                link_label = "More information"
            
            return self.rendering_service.render_product_list(
                header, cards, self.rendering_service.get_credit_card_summary,
                link_label, self.context.user_language
            )
            
        except Exception as e:
            logger.error(f"Error showing {brand} cards: {e}")
            return self._generate_error_response()
    
    def _show_all_credit_cards(self) -> str:
        """Show all credit cards using rendering service"""
        try:
            credit_cards = self.knowledge_base.get('credit_cards', {})
            
            if self.context.user_language == 'bg':
                response = f"{Fore.BLUE}💳 Всички налични кредитни карти от Fibank:{Style.RESET_ALL}\n\n"
            else:
                response = f"{Fore.BLUE}💳 All available credit cards from Fibank:{Style.RESET_ALL}\n\n"
            
            # Show each brand category
            for brand, cards in credit_cards.items():
                if self.context.user_language == 'bg':
                    response += f"{Fore.MAGENTA}📱 {brand} карти:{Style.RESET_ALL}\n"
                else:
                    response += f"{Fore.MAGENTA}📱 {brand} cards:{Style.RESET_ALL}\n"
                
                for card_name, card_info in cards.items():
                    response += f"🔹 **{card_name}**\n"
                    
                    summary = self.rendering_service.get_credit_card_summary(card_info)
                    if summary:
                        response += f"   {summary}\n"
                    
                    link = card_info.get('link', '')
                    if link:
                        if self.context.user_language == 'bg':
                            response += f"   🔗 Повече информация: {link}\n\n"
                        else:
                            response += f"   🔗 More info: {link}\n\n"
                    else:
                        response += "\n"
            
            if self.context.user_language == 'bg':
                response += f"{Fore.YELLOW}За повече детайли за конкретна карта, просто я споменете по име.{Style.RESET_ALL}"
            else:
                response += f"{Fore.YELLOW}For more details about a specific card, just mention it by name.{Style.RESET_ALL}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error showing all credit cards: {e}")
            return self._generate_error_response()
    
    def _show_loan_category(self, category_name: str) -> str:
        """Show loans from specific category using rendering service"""
        try:
            loans = self.knowledge_base.get('credits', {}).get(category_name, {})
            
            if self.context.user_language == 'bg':
                header = f'Продукти от категория "{category_name}"'
                link_label = "За повече информация посетете"
            else:
                header = f'Products from category "{category_name}"'
                link_label = "For more information visit"
            
            return self.rendering_service.render_product_list(
                header, loans, self.rendering_service.get_loan_summary,
                link_label, self.context.user_language
            )
            
        except Exception as e:
            logger.error(f"Error showing loan category {category_name}: {e}")
            return self._generate_error_response()
    
    def _show_all_loan_categories(self) -> str:
        """Show all loan categories using rendering service"""
        try:
            credits = self.knowledge_base.get('credits', {})
            response = self.rendering_service.render_category_overview(credits, self.context.user_language)
            
            if self.context.user_language == 'bg':
                response += f"""{Fore.YELLOW}За да видите конкретна категория, моля уточнете:
• "Жилищни кредити" или "ипотечни кредити"
• "Потребителски кредити"  
• "Овърдрафт"
• "Други кредити"

Или можете да споменете конкретен продукт по име.{Style.RESET_ALL}"""
            else:
                response += f"""{Fore.YELLOW}To see a specific category, please specify:
• "Housing loans" or "mortgage loans"
• "Consumer loans"
• "Overdraft"
• "Other loans"

Or you can mention a specific product by name.{Style.RESET_ALL}"""
            
            return response
            
        except Exception as e:
            logger.error(f"Error showing all loan categories: {e}")
            return self._generate_error_response()
    
    def generate_response(self, user_input: str) -> str:
        """Main response generation orchestrator"""
        try:
            # Validate input
            if not user_input or not user_input.strip():
                return f"{Fore.YELLOW}💡 Please enter your question.{Style.RESET_ALL}"
            
            # Detect language
            self.context.user_language = detect_language(user_input)
            
            # Classify intent
            intent, confidence = self.find_intent(user_input)
            
            # Store interaction in conversation history
            self.context.conversation_history.append({
                "user": user_input,
                "timestamp": datetime.now().isoformat(),
                "language": self.context.user_language,
                "intent": intent,
                "confidence": confidence
            })
            
            # Handle specific intents
            if intent == 'credit_cards':
                response = self.handle_credit_card_inquiry(user_input)
            elif intent == 'loans':
                response = self.handle_loan_inquiry(user_input)
            else:
                # Use AI or semantic search for general queries
                response = self._generate_ai_or_fallback_response(user_input, intent, confidence)
            
            # Append contact information
            if self.context.user_language == "bg":
                response += f"\n\n{Fore.CYAN}📞 За повече информация: *2265 или посетете някой от нашите 119 клона в България.{Style.RESET_ALL}"
            else:
                response += f"\n\n{Fore.CYAN}📞 For more information: *2265 or visit any of our 119 branches in Bulgaria.{Style.RESET_ALL}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._generate_error_response()
    
    def _generate_ai_or_fallback_response(self, user_input: str, intent: str, confidence: float) -> str:
        """Generate response using AI or fallback to semantic search"""
        try:
            # Try Gemini AI first
            if self.gemini_service.is_available:
                relevant_products = self.semantic_service.find_similar_products(user_input)
                recent_context = self.context.get_recent_context(3)
                
                prompt = self.gemini_service.create_structured_prompt(
                    user_input, self.context.user_language, relevant_products, recent_context
                )
                
                ai_response = self.gemini_service.generate_response(prompt)
                if ai_response:
                    return ai_response
            
            # Fallback to semantic search
            return self._generate_semantic_fallback_response(user_input)
            
        except Exception as e:
            logger.error(f"Error in AI/fallback response generation: {e}")
            return self._generate_semantic_fallback_response(user_input)
    
    def _generate_semantic_fallback_response(self, user_input: str) -> str:
        """Generate response using semantic search fallback"""
        try:
            relevant_products = self.semantic_service.find_similar_products(user_input, top_k=5)
            
            if not relevant_products:
                if self.context.user_language == 'bg':
                    return (f"{Fore.YELLOW}Съжалявам, не намерих релевантна информация за вашия въпрос. "
                           f"Можете да попитате за кредитни карти или кредити.{Style.RESET_ALL}")
                else:
                    return (f"{Fore.YELLOW}Sorry, I couldn't find relevant information for your question. "
                           f"You can ask about credit cards or loans.{Style.RESET_ALL}")
            
            # Build response with found products
            if self.context.user_language == 'bg':
                response = f"{Fore.BLUE}Въз основа на вашия въпрос, ето някои продукти, които биха могли да ви интересуват:{Style.RESET_ALL}\n\n"
            else:
                response = f"{Fore.BLUE}Based on your question, here are some products that might interest you:{Style.RESET_ALL}\n\n"
            
            for i, (_, product, score) in enumerate(relevant_products[:3], 1):
                response += f"{i}. **{product['name']}**\n"
                if product['description']:
                    desc = product['description'][:200]
                    if len(product['description']) > 200:
                        desc += "..."
                    response += f"   {desc}\n\n"
            
            if self.context.user_language == 'bg':
                response += f"{Fore.YELLOW}Искате ли да научите повече за някой от тези продукти?{Style.RESET_ALL}"
            else:
                response += f"{Fore.YELLOW}Would you like to learn more about any of these products?{Style.RESET_ALL}"
                
            return response
            
        except Exception as e:
            logger.error(f"Error in semantic fallback response: {e}")
            return self._generate_error_response()
    
    def _generate_error_response(self) -> str:
        """Generate error response"""
        if self.context.user_language == 'bg':
            return f"{Fore.RED}Съжалявам, възникна грешка. Моля, опитайте отново.{Style.RESET_ALL}"
        else:
            return f"{Fore.RED}Sorry, an error occurred. Please try again.{Style.RESET_ALL}"
    
    def start_conversation(self):
        """Start the interactive conversation loop"""
        # Display welcome banner
        print(f"\n{Back.BLUE}{Fore.WHITE} FIBANK ВИРТУАЛЕН АСИСТЕНТ (МОДУЛНА ВЕРСИЯ) {Style.RESET_ALL}")
        print(f"{Fore.CYAN}Добре дошли във виртуелния асистент на Fibank!")
        print(f"Мога да ви помогна с информация за нашите кредитни карти и кредити.")
        print(f"Можете да задавате въпроси на български или английски език.")
        print(f"Напишете 'help' или 'помощ' за насоки, 'quit', 'exit' или 'довиждане' за край.\n{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}[TIP] Опитайте: 'Какви кредитни карти предлагате?' или 'Разкажете ми за кредитите'{Style.RESET_ALL}\n")
        
        # Main conversation loop
        while True:
            try:
                user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'довиждане', 'чао', 'изход']:
                    print(f"\n{Fore.BLUE}[BOT] Fibank Assistant: {Style.RESET_ALL}", end="")
                    if self.context.user_language == "bg":
                        print("Довиждане! Благодарим ви, че избрахте Fibank! 🌟")
                    else:
                        print("Goodbye! Thank you for choosing Fibank! 🌟")
                    break
                
                if not user_input:
                    continue
                
                # Generate and display response
                response = self.generate_response(user_input)
                print(f"\n{Fore.BLUE}[BOT] Fibank Assistant:{Style.RESET_ALL}")
                print(response)
                print(f"\n{'-' * 60}")
                
            except EOFError:
                print(f"\n\n{Fore.BLUE}[BOT] Довиждане! 🌟{Style.RESET_ALL}")
                break
            except KeyboardInterrupt:
                print(f"\n\n{Fore.BLUE}[BOT] Довиждане! 🌟{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"\n{Fore.RED}❌ An error occurred: {e}{Style.RESET_ALL}")
                logger.error(f"Unexpected error in conversation loop: {e}")
                continue 