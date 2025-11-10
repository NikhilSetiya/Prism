"""Localization and translation for campaign messages."""

import os
from typing import Dict, Optional
from openai import OpenAI

from src.utils import Config


# Region to language mapping
REGION_LANGUAGE_MAP = {
    'EMEA': 'en',
    'EMEA_FR': 'fr',
    'EMEA_DE': 'de',
    'APAC_JP': 'ja',
    'LATAM': 'es',
    'NA': 'en'
}


class Localizer:
    """Translate and localize campaign messages."""
    
    def __init__(self, config: dict):
        """Initialize localizer with configuration."""
        self.config = config
        localization_config = config.get('localization', {})
        self.enabled = localization_config.get('enabled', True)
        self.default_locale = localization_config.get('default_locale', 'en')
        self.translation_model = localization_config.get('translation_model', 'gpt-4o')
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.translation_cache: Dict[str, str] = {}
    
    def localize_message(self, message: str, target_locale: str, region: str) -> str:
        """
        Localize campaign message to target locale.
        
        Args:
            message: Original campaign message
            target_locale: Target locale code (e.g., 'en', 'fr', 'de')
            region: Campaign region
        
        Returns:
            Localized message
        """
        if not self.enabled:
            return message
        
        # Return original if already in target locale
        if target_locale == self.default_locale:
            return message
        
        # Check cache
        cache_key = f"{message}_{target_locale}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # Translate using GPT-4
        translated = self._translate(message, target_locale, region)
        
        # Cache translation
        self.translation_cache[cache_key] = translated
        
        return translated
    
    def _translate(self, text: str, target_lang: str, region: str) -> str:
        """Translate text to target language using GPT-4."""
        if target_lang == 'en':
            return text
        
        try:
            response = self.client.chat.completions.create(
                model=self.translation_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional marketing translator. Translate the following campaign message to {target_lang}. Maintain brand tone and marketing impact. Keep it concise and impactful."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Translation failed: {e}. Using original text.")
            return text
    
    def get_locale_from_region(self, region: str) -> str:
        """Get default locale for a region."""
        return REGION_LANGUAGE_MAP.get(region, self.default_locale)

