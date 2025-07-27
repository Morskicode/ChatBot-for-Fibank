"""
Configuration loading utilities

This module provides utilities for loading and managing configuration files
including YAML and JSON configurations for intents, keywords, and other settings.
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
import logging

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Configuration loader for YAML and JSON files"""
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize configuration loader
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir
        self._intent_patterns = None
        self._keywords = None
    
    def load_json_config(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON configuration file
        
        Args:
            filename: Name of the JSON file to load
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the JSON is malformed
        """
        filepath = os.path.join(self.config_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Loaded JSON config from {filepath}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file {filepath}: {e}")
            raise
    
    def load_yaml_config(self, filename: str) -> Dict[str, Any]:
        """
        Load YAML configuration file
        
        Args:
            filename: Name of the YAML file to load
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            ImportError: If PyYAML is not installed
            yaml.YAMLError: If the YAML is malformed
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML configuration files. Install with: pip install PyYAML")
        
        filepath = os.path.join(self.config_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded YAML config from {filepath}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {filepath}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in configuration file {filepath}: {e}")
            raise
    
    def load_intent_patterns(self, filename: str = "intents.yml") -> Dict[str, List[re.Pattern]]:
        """
        Load and compile intent patterns from configuration
        
        Args:
            filename: Name of the intents configuration file
            
        Returns:
            Dictionary mapping intent names to compiled regex patterns
        """
        if self._intent_patterns is not None:
            return self._intent_patterns
        
        try:
            # Try to load YAML first, fallback to JSON if YAML not available
            if filename.endswith('.yml') or filename.endswith('.yaml'):
                if YAML_AVAILABLE:
                    intents_config = self.load_yaml_config(filename)
                else:
                    logger.warning("YAML not available, trying JSON fallback")
                    json_filename = filename.replace('.yml', '.json').replace('.yaml', '.json')
                    intents_config = self.load_json_config(json_filename)
            else:
                intents_config = self.load_json_config(filename)
            
            # Compile regex patterns
            compiled_patterns = {}
            for intent_name, patterns in intents_config.items():
                compiled_patterns[intent_name] = [
                    re.compile(pattern, re.IGNORECASE) for pattern in patterns
                ]
            
            self._intent_patterns = compiled_patterns
            logger.info(f"Loaded and compiled {len(compiled_patterns)} intent patterns")
            return compiled_patterns
            
        except (FileNotFoundError, json.JSONDecodeError, yaml.YAMLError if YAML_AVAILABLE else Exception) as e:
            logger.warning(f"Could not load intent patterns from {filename}: {e}")
            # Return default fallback patterns
            return self._get_default_intent_patterns()
    
    def load_keywords(self, filename: str = "keywords.yml") -> Dict[str, Dict[str, List[str]]]:
        """
        Load keyword configurations
        
        Args:
            filename: Name of the keywords configuration file
            
        Returns:
            Dictionary containing keyword mappings
        """
        if self._keywords is not None:
            return self._keywords
        
        try:
            # Try to load YAML first, fallback to JSON if YAML not available
            if filename.endswith('.yml') or filename.endswith('.yaml'):
                if YAML_AVAILABLE:
                    keywords = self.load_yaml_config(filename)
                else:
                    logger.warning("YAML not available, trying JSON fallback")
                    json_filename = filename.replace('.yml', '.json').replace('.yaml', '.json')
                    keywords = self.load_json_config(json_filename)
            else:
                keywords = self.load_json_config(filename)
            
            self._keywords = keywords
            logger.info(f"Loaded keyword configurations")
            return keywords
            
        except (FileNotFoundError, json.JSONDecodeError, yaml.YAMLError if YAML_AVAILABLE else Exception) as e:
            logger.warning(f"Could not load keywords from {filename}: {e}")
            # Return default fallback keywords
            return self._get_default_keywords()
    
    def _get_default_intent_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Return default intent patterns as fallback"""
        default_patterns = {
            'credit_cards': [
                r'\b(credit\s*card|кредитна\s*карта|карта|карти)\b',
                r'\b(visa|виза|визa|viza|виса|mastercard|мастеркард|мастърcard|мастер\s*кард|мастеркарт)\b',
                r'\b(платина|златна|класик|standard|стандартна|gold|голд|platinum|платинум)\b',
                r'\b(плащане|плащания|покупки|first\s*lady|фърст\s*лейди|за\s*дами)\b'
            ],
            'loans': [
                r'\b(loan|заем|кредит|ипотека|жилищен)\b',
                r'\b(consumer|потребителски|overdraft|овърдрафт)\b',
                r'\b(финансиране|пари|сума)\b'
            ],
            'rates': [
                r'\b(rate|лихва|лихвен|процент)\b',
                r'\b(price|цена|такса|комисионна)\b',
                r'\b(how\s*much|колко\s*струва|цената)\b'
            ],
            'application': [
                r'\b(apply|кандидатствам|заявка|процес)\b',
                r'\b(how\s*to|как\s*да|документи|изисквания)\b',
                r'\b(online|онлайн|клон|филиал)\b'
            ],
            'help': [
                r'\b(help|помощ|помогнете|информация)\b',
                r'\b(what\s*can\s*you|какво\s*можеш|възможности)\b',
                r'\b(guide|ръководство|инструкции)\b'
            ]
        }
        
        # Compile the patterns
        compiled_patterns = {}
        for intent_name, patterns in default_patterns.items():
            compiled_patterns[intent_name] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
        
        return compiled_patterns
    
    def _get_default_keywords(self) -> Dict[str, Dict[str, List[str]]]:
        """Return default keywords as fallback"""
        return {
            "visa": {
                "classic": ["visa classic", "виза класик", "класическа виза"],
                "gold": ["visa gold", "виза голд", "златна виза"],
                "platinum": ["visa platinum", "виза платинум", "платинена виза"]
            },
            "mastercard": {
                "standard": ["mastercard standard", "мастеркард стандартна"],
                "gold": ["mastercard gold", "мастеркард златна"],
                "platinum": ["mastercard platinum", "мастеркард платинена"],
                "first_lady": ["first lady", "фърст лейди", "за дами"]
            },
            "loans": {
                "housing": ["жилищен", "ипотечен", "ипотека", "mortgage"],
                "consumer": ["потребителски", "consumer", "personal loan"],
                "overdraft": ["овърдрафт", "overdraft"]
            }
        } 