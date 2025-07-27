"""
Unified rendering service for product displays

This service provides common functions for rendering product lists and information,
eliminating code duplication across different product display methods.
"""

import logging
from typing import Dict, List, Any, Callable, Optional
from colorama import Fore, Style

logger = logging.getLogger(__name__)


class RenderingService:
    """
    Unified rendering service for consistent product displays
    
    This service provides common rendering functions that can be used across
    different product types to maintain consistency and reduce code duplication.
    """
    
    def __init__(self):
        """Initialize rendering service"""
        pass
    
    def render_product_list(self, 
                           header: str,
                           items: Dict[str, Dict],
                           summary_fn: Callable[[Dict], str],
                           link_label: str,
                           language: str = "en") -> str:
        """
        Render a list of products with consistent formatting
        
        Args:
            header: Header text for the product list
            items: Dictionary of product items to display
            summary_fn: Function to extract summary from product info
            link_label: Label text for product links
            language: Language for UI text (en/bg)
            
        Returns:
            Formatted string with product list
        """
        try:
            response = f"{Fore.BLUE}💳 {header}{Style.RESET_ALL}\n\n"
            
            if not items:
                if language == "bg":
                    response += f"{Fore.YELLOW}Няма налични продукти в тази категория.{Style.RESET_ALL}"
                else:
                    response += f"{Fore.YELLOW}No products available in this category.{Style.RESET_ALL}"
                return response
            
            for name, info in items.items():
                response += f"🔹 **{name}**\n"
                
                # Get summary using provided function
                try:
                    summary = summary_fn(info)
                    if summary:
                        response += f"   {summary}\n"
                except Exception as e:
                    logger.warning(f"Error getting summary for {name}: {e}")
                
                # Add link if available
                link = info.get('link', '')
                if link:
                    if language == "bg":
                        response += f"   🔗 {link_label}: {link}\n\n"
                    else:
                        response += f"   🔗 {link_label}: {link}\n\n"
                else:
                    response += "\n"
            
            # Add helpful tip
            if language == "bg":
                response += f"{Fore.YELLOW}За повече детайли за конкретен продукт, просто го споменете по име.{Style.RESET_ALL}"
            else:
                response += f"{Fore.YELLOW}For more details about a specific product, just mention it by name.{Style.RESET_ALL}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error rendering product list: {e}")
            if language == "bg":
                return f"{Fore.RED}Съжалявам, възникна грешка при показването на продуктите.{Style.RESET_ALL}"
            else:
                return f"{Fore.RED}Sorry, an error occurred while displaying the products.{Style.RESET_ALL}"
    
    def render_specific_product(self, 
                               product_name: str,
                               product_data: Dict[str, Any],
                               language: str = "en") -> str:
        """
        Render detailed information for a specific product
        
        Args:
            product_name: Name of the product
            product_data: Product data dictionary
            language: Language for UI text (en/bg)
            
        Returns:
            Formatted string with detailed product information
        """
        try:
            if language == "bg":
                response = f"{Fore.BLUE}💳 Информация за {product_name}:{Style.RESET_ALL}\n\n"
            else:
                response = f"{Fore.BLUE}💳 Information about {product_name}:{Style.RESET_ALL}\n\n"
            
            # Extract and format key information
            info = product_data.get('информация за продукта', '')
            if info:
                # Split by main sections
                sections = info.split('\n- ')
                
                for i, section in enumerate(sections):
                    if i == 0:
                        # First section (benefits)
                        if language == "bg":
                            response += f"**Основни предимства:**\n{section.strip()}\n\n"
                        else:
                            response += f"**Key Benefits:**\n{section.strip()}\n\n"
                    else:
                        # Technical details section
                        if language == "bg":
                            response += f"**Технически детайли:**\n- {section.strip()}\n\n"
                        else:
                            response += f"**Technical Details:**\n- {section.strip()}\n\n"
            
            # Add link
            link = product_data.get('link', '')
            if link:
                if language == "bg":
                    response += f"{Fore.GREEN}🔗 За повече информация: {link}{Style.RESET_ALL}\n\n"
                else:
                    response += f"{Fore.GREEN}🔗 For more information: {link}{Style.RESET_ALL}\n\n"
            
            # Add helpful tip
            if language == "bg":
                response += f"{Fore.YELLOW}💡 Можете да попитате за други продукти или да сравните с друг продукт.{Style.RESET_ALL}"
            else:
                response += f"{Fore.YELLOW}💡 You can ask about other products or compare with another product.{Style.RESET_ALL}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error rendering specific product {product_name}: {e}")
            if language == "bg":
                return f"{Fore.RED}Съжалявам, възникна грешка при показването на информацията за продукта.{Style.RESET_ALL}"
            else:
                return f"{Fore.RED}Sorry, an error occurred while showing the product information.{Style.RESET_ALL}"
    
    def render_category_overview(self, 
                                categories: Dict[str, Dict],
                                language: str = "en") -> str:
        """
        Render overview of all product categories
        
        Args:
            categories: Dictionary of product categories
            language: Language for UI text (en/bg)
            
        Returns:
            Formatted string with category overview
        """
        try:
            if language == "bg":
                response = f"{Fore.BLUE}💰 Предлагаме продукти в следните категории:{Style.RESET_ALL}\n\n"
            else:
                response = f"{Fore.BLUE}💰 We offer products in the following categories:{Style.RESET_ALL}\n\n"
            
            for category_name, products in categories.items():
                response += f"🔹 **{category_name}** ({len(products)} "
                if language == "bg":
                    response += "продукта)\n"
                else:
                    response += "products)\n"
                
                # Show first few products as examples
                product_names = list(products.keys())[:3]
                for name in product_names:
                    response += f"   • {name}\n"
                
                if len(products) > 3:
                    if language == "bg":
                        response += f"   • и още {len(products) - 3} продукта...\n"
                    else:
                        response += f"   • and {len(products) - 3} more products...\n"
                response += "\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error rendering category overview: {e}")
            if language == "bg":
                return f"{Fore.RED}Съжалявам, възникна грешка при показването на категориите.{Style.RESET_ALL}"
            else:
                return f"{Fore.RED}Sorry, an error occurred while displaying the categories.{Style.RESET_ALL}"
    
    def get_credit_card_summary(self, card_info: Dict[str, Any]) -> str:
        """
        Extract key summary information for credit cards
        
        Args:
            card_info: Credit card information dictionary
            
        Returns:
            Summary string with key details
        """
        try:
            info = card_info.get('информация за продукта', '')
            if not info:
                return ""
            
            # Extract key details for summary
            lines = info.split(';')
            key_info = []
            
            for line in lines:
                line = line.strip()
                if any(keyword in line.lower() for keyword in ['лимит:', 'годишна такса:', 'cashback:']):
                    key_info.append(line)
            
            return "\n   ".join(key_info[:3])  # Return top 3 key details
            
        except Exception as e:
            logger.warning(f"Error extracting credit card summary: {e}")
            return ""
    
    def get_loan_summary(self, loan_info: Dict[str, Any]) -> str:
        """
        Extract key summary information for loans
        
        Args:
            loan_info: Loan information dictionary
            
        Returns:
            Summary string with key details
        """
        try:
            info = loan_info.get('информация за продукта', '')
            if not info:
                return ""
            
            # Extract first few lines for summary
            lines = info.split('\n')
            key_info = []
            
            for line in lines[:2]:  # First 2 lines for summary
                line = line.strip()
                if line and not line.startswith('-'):
                    key_info.append(line)
            
            return "\n   ".join(key_info)
            
        except Exception as e:
            logger.warning(f"Error extracting loan summary: {e}")
            return "" 