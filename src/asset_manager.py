"""Asset reuse manager with cache-first strategy for hero images."""

import os
import hashlib
from typing import Optional, Tuple
from pathlib import Path
from PIL import Image

from src.models import Product, CampaignBrief
from src.image_generator import ImageGenerator
from src.storage import LocalStorage
from src.utils import ensure_dir


class AssetManager:
    """Manage hero image reuse with cache-first strategy."""
    
    def __init__(self, config: dict, image_generator: ImageGenerator, cache_storage: LocalStorage):
        """Initialize asset manager."""
        self.config = config
        self.image_generator = image_generator
        self.cache_storage = cache_storage
        self.input_folder = config.get('assets', {}).get('input_folder', './assets/input')
        
        # Hero cache configuration
        hero_config = config.get('hero_image', {})
        self.cache_enabled = hero_config.get('cache_enabled', True)
        
        # Ensure input folder exists
        ensure_dir(self.input_folder)
    
    def get_or_generate_hero(self, product: Product, campaign_brief: CampaignBrief) -> Tuple[Image.Image, bool, float]:
        """
        Get hero image from input/cache or generate new one.
        
        Args:
            product: Product model
            campaign_brief: Campaign brief
        
        Returns:
            Tuple of (Image, is_cached, cost)
        """
        # Priority 1: Check input folder for user-provided hero
        input_image = self._check_input_folder(product.id, campaign_brief.campaign_id)
        if input_image:
            return input_image, False, 0.0  # Input assets are free but not "cached"
        
        # Compute cache key once (avoid duplicate calculation)
        cache_key = None
        if self.cache_enabled:
            cache_key = self._compute_cache_key(product.id, campaign_brief)
        
        # Priority 2: Check cache for previously generated hero
        if cache_key:
            cached_image = self._check_cache(cache_key)
            if cached_image:
                return cached_image, True, 0.0
        
        # Priority 3: Generate new hero image
        image, cost = self.image_generator.generate_hero(product, campaign_brief)
        
        # Save to cache
        if cache_key:
            self._save_to_cache(cache_key, image)
        
        return image, False, cost
    
    def _check_input_folder(self, product_id: str, campaign_id: str) -> Optional[Image.Image]:
        """
        Check input folder for user-provided hero images.
        
        Priority:
        1. Campaign-specific: assets/input/{campaign_id}/{product_id}.png
        2. Global: assets/input/{product_id}.png
        """
        # Priority 1: Campaign-specific hero
        campaign_hero = Path(self.input_folder) / campaign_id / f"{product_id}.png"
        if campaign_hero.exists():
            try:
                return Image.open(str(campaign_hero))
            except Exception:
                pass
        
        # Priority 2: Global hero
        global_hero = Path(self.input_folder) / f"{product_id}.png"
        if global_hero.exists():
            try:
                return Image.open(str(global_hero))
            except Exception:
                pass
        
        return None
    
    def _compute_cache_key(self, product_id: str, campaign_brief: CampaignBrief) -> str:
        """
        Compute content-addressable cache key for hero image.
        
        Note: No aspect ratio in key since we cache hero images only.
        """
        content = f"{product_id}_{campaign_brief.campaign_message}_{campaign_brief.region}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _check_cache(self, cache_key: str) -> Optional[Image.Image]:
        """Check cache for previously generated hero."""
        cache_path = f"hero_{cache_key}.png"
        return self.cache_storage.load(cache_path)
    
    def _save_to_cache(self, cache_key: str, image: Image.Image):
        """Save generated hero to cache."""
        cache_path = f"hero_{cache_key}.png"
        self.cache_storage.save(cache_path, image)
