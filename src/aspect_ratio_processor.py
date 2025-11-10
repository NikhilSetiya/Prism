"""Intelligent aspect ratio processing for creating variations from hero images."""

from typing import Dict
from PIL import Image, ImageOps


# Target sizes for each aspect ratio (optimized for social platforms)
ASPECT_RATIO_SIZES = {
    "1:1": (1080, 1080),    # Instagram feed, Facebook posts
    "9:16": (1080, 1920),   # Instagram Stories, Reels, TikTok
    "16:9": (1920, 1080)    # YouTube thumbnails, Facebook video
}


class AspectRatioProcessor:
    """Create aspect ratio variations from hero images using intelligent cropping."""
    
    def __init__(self, config: dict):
        """Initialize processor with configuration."""
        self.config = config
        processing_config = config.get('aspect_ratio_processing', {})
        self.crop_strategy = processing_config.get('crop_strategy', 'center')
        self.quality = processing_config.get('quality', 95)
    
    def create_variation(self, hero_image: Image.Image, target_aspect: str) -> Image.Image:
        """
        Create an aspect ratio variation from a hero image.
        
        Args:
            hero_image: Source hero image (1024x1024)
            target_aspect: Target aspect ratio ("1:1", "9:16", "16:9")
        
        Returns:
            Cropped/resized image at target aspect ratio
        """
        target_size = ASPECT_RATIO_SIZES.get(target_aspect, (1080, 1080))
        
        if target_aspect == "1:1":
            # For square, just resize the hero image
            return hero_image.resize(target_size, Image.Resampling.LANCZOS)
        
        elif target_aspect == "9:16":
            # Portrait: crop from center for vertical format
            return self._center_crop(hero_image, target_size)
        
        elif target_aspect == "16:9":
            # Landscape: crop from center for horizontal format
            return self._center_crop(hero_image, target_size)
        
        else:
            # Fallback: resize to target
            return hero_image.resize(target_size, Image.Resampling.LANCZOS)
    
    def _center_crop(self, image: Image.Image, target_size: tuple) -> Image.Image:
        """
        Perform center-weighted crop using PIL's ImageOps.fit.
        
        This maintains the central subject while adapting to target dimensions.
        """
        return ImageOps.fit(
            image,
            target_size,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5)  # Center crop
        )
    
    def create_all_variations(self, hero_image: Image.Image) -> Dict[str, Image.Image]:
        """
        Create all aspect ratio variations from a hero image.
        
        Args:
            hero_image: Source hero image
        
        Returns:
            Dictionary mapping aspect ratio to cropped image
        """
        variations = {}
        for aspect_ratio in ASPECT_RATIO_SIZES.keys():
            variations[aspect_ratio] = self.create_variation(hero_image, aspect_ratio)
        
        return variations

