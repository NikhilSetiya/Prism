"""GenAI image generation with integrated prompt building for hero images."""

import os
import time
import requests
from typing import Optional, Tuple, Dict, Any
from PIL import Image
from io import BytesIO
from openai import OpenAI
from openai import RateLimitError, APIError, APIConnectionError

from src.models import Product, CampaignBrief


# DALL-E 3 pricing (as of 2024)
COST_PER_IMAGE = {
    "standard": 0.04,
    "hd": 0.08
}


class ImageGenerator:
    """Generate hero images using OpenAI DALL-E 3 API with integrated prompting."""
    
    def __init__(self, config: dict):
        """Initialize image generator with configuration."""
        self.config = config
        generator_config = config.get('generator', {})
        self.model = generator_config.get('model', 'dall-e-3')
        self.api_key = generator_config.get('api_key') or os.getenv('OPENAI_API_KEY')
        self.max_retries = generator_config.get('max_retries', 3)
        
        # Hero image configuration
        hero_config = config.get('hero_image', {})
        self.hero_size = hero_config.get('size', '1024x1024')
        self.quality = hero_config.get('quality', 'hd')
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_hero(self, product: Product, campaign_brief: CampaignBrief) -> Tuple[Image.Image, float]:
        """
        Generate a hero image for a product.
        
        Args:
            product: Product model with details and creative brief
            campaign_brief: Campaign brief with region and audience
        
        Returns:
            Tuple of (PIL Image, cost)
        """
        # Build hero-focused prompt
        prompt = self._build_hero_prompt(product, campaign_brief)
        
        # Call API with retry logic
        image = self._call_api_with_retry(prompt, self.hero_size)
        
        # Calculate cost
        cost = COST_PER_IMAGE.get(self.quality, 0.08)
        
        return image, cost
    
    def _build_hero_prompt(self, product: Product, campaign_brief: CampaignBrief) -> str:
        """
        Build a photorealistic hero image prompt optimized for multi-format cropping.
        
        Focus: Center-weighted composition with generous negative space and realistic photography.
        """
        # Determine photography style based on setting and mood
        setting_lower = product.creative_brief.setting.lower()
        mood_lower = product.creative_brief.mood.lower()
        
        # Select lighting description
        if "studio" in setting_lower or "minimal" in setting_lower:
            lighting = "professional studio lighting with softbox, subtle rim light, minimal shadows, f/2.8"
        elif "natural" in setting_lower or "eco" in setting_lower:
            lighting = "natural window light at golden hour, soft ambient fill, organic shadows, f/4"
        elif "dramatic" in mood_lower or "bold" in mood_lower:
            lighting = "dramatic side lighting with Profoto strobes, depth and dimension, f/2.8"
        else:
            lighting = "natural diffused daylight through large windows, soft shadows, f/3.5"
        
        # Build photorealistic hero prompt
        prompt = f"""PHOTOREALISTIC PRODUCT PHOTOGRAPHY - Commercial advertising shoot

SUBJECT: {product.name}
{product.description[:180]}

CAMERA SETUP:
- Professional DSLR/mirrorless camera (Canon EOS R5 or Sony A7R IV quality)
- 85mm prime lens for natural perspective
- {lighting}
- Shot on actual camera, NOT AI-generated or CGI

COMPOSITION (CRITICAL):
- Product perfectly centered in frame, occupying 60-70% of image
- Generous negative space on all sides for safe cropping to 1:1, 9:16, and 16:9
- Clean, uncluttered {product.creative_brief.setting}
- Include: {", ".join(product.creative_brief.key_visual_elements[:3])}

STYLING & MOOD:
- {product.creative_brief.mood} atmosphere
- Brand colors: {", ".join(product.brand_style.color_palette[:3])}
- Visual style: {product.brand_style.visual_style}
- Target: {campaign_brief.target_audience}

REALISM DIRECTIVES:
- Real photography aesthetic with subtle lens characteristics
- Natural depth of field with bokeh
- Authentic product textures and materials
- Subtle reflections and environmental interactions
- NO artificial perfection, NO generic stock photo look
- Preserve natural lighting imperfections and subtle shadows
- Professional commercial advertising quality
- Think Apple, Nike, or premium magazine editorial

AVOID: Oversaturation, artificial lighting, CGI appearance, symmetrical perfection, generic angles"""

        return prompt
    
    def _call_api_with_retry(self, prompt: str, size: str, retry_count: int = 0) -> Image.Image:
        """Call OpenAI API with exponential backoff retry logic."""
        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=size,
                quality="hd" if self.quality == "hd" else "standard",
                n=1
            )
            
            # Download image from URL
            image_url = response.data[0].url
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            
            # Convert to PIL Image
            image = Image.open(BytesIO(img_response.content))
            return image
            
        except RateLimitError as e:
            if retry_count < self.max_retries:
                wait_time = 2 ** retry_count
                time.sleep(wait_time)
                return self._call_api_with_retry(prompt, size, retry_count + 1)
            else:
                raise Exception(f"Rate limit exceeded after {self.max_retries} retries: {e}")
        
        except (APIError, APIConnectionError) as e:
            if retry_count < self.max_retries:
                wait_time = 2 ** retry_count
                time.sleep(wait_time)
                return self._call_api_with_retry(prompt, size, retry_count + 1)
            else:
                raise Exception(f"API error after {self.max_retries} retries: {e}")
        
        except Exception as e:
            raise Exception(f"Image generation failed: {e}")
