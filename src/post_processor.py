"""Post-processing for adding film-like imperfections to avoid AI-generated look."""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, Any


class PostProcessor:
    """Add subtle film-like imperfections to generated images."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize post-processor with configuration."""
        self.config = config
        self.post_config = config.get('post_processing', {})
        self.enabled = self.post_config.get('enabled', True)
        self.intensity = self.post_config.get('intensity', 0.3)  # 0.0 to 1.0
    
    def process(self, image: Image.Image) -> Image.Image:
        """
        Apply film-like post-processing effects.
        
        Args:
            image: Input PIL Image
        
        Returns:
            Processed image with subtle imperfections
        """
        if not self.enabled:
            return image
        
        img = image.copy()
        
        # Apply subtle film grain
        img = self._add_film_grain(img)
        
        # Add subtle vignette
        img = self._add_vignette(img)
        
        # Slight color temperature shift
        img = self._adjust_color_temperature(img)
        
        # Subtle sharpness adjustment
        img = self._adjust_sharpness(img)
        
        return img
    
    def _add_film_grain(self, img: Image.Image) -> Image.Image:
        """Add subtle film grain to image."""
        img_array = np.array(img).astype(float)
        
        # Generate noise
        noise_intensity = 2 * self.intensity  # 0-2% noise
        noise = np.random.normal(0, noise_intensity, img_array.shape)
        
        # Add noise to image
        img_array = img_array + noise
        
        # Clip values to valid range
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        
        return Image.fromarray(img_array)
    
    def _add_vignette(self, img: Image.Image) -> Image.Image:
        """Add subtle vignette effect."""
        width, height = img.size
        
        # Create vignette mask
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        X, Y = np.meshgrid(x, y)
        
        # Radial distance from center
        radius = np.sqrt(X**2 + Y**2)
        
        # Vignette function (subtle)
        vignette_strength = 0.3 * self.intensity
        vignette = 1 - vignette_strength * (radius / radius.max())**2
        vignette = np.clip(vignette, 0, 1)
        
        # Apply to RGB channels
        img_array = np.array(img).astype(float)
        for i in range(3):  # RGB channels
            img_array[:, :, i] *= vignette
        
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        
        return Image.fromarray(img_array)
    
    def _adjust_color_temperature(self, img: Image.Image) -> Image.Image:
        """Slight color temperature adjustment for warmth."""
        img_array = np.array(img).astype(float)
        
        # Warm shift (increase red, slight decrease blue)
        warmth = 0.02 * self.intensity
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] * (1 + warmth), 0, 255)  # Red
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] * (1 - warmth/2), 0, 255)  # Blue
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def _adjust_sharpness(self, img: Image.Image) -> Image.Image:
        """Subtle sharpness adjustment."""
        # Very subtle sharpening (factor 1.0-1.2 range)
        sharpness_factor = 1.0 + (0.15 * self.intensity)
        enhancer = ImageEnhance.Sharpness(img)
        return enhancer.enhance(sharpness_factor)
    
    def add_chromatic_aberration(self, img: Image.Image, strength: float = 1.0) -> Image.Image:
        """
        Add subtle chromatic aberration (optional, more intense effect).
        
        Args:
            img: Input image
            strength: Effect strength (0.0 to 1.0)
        
        Returns:
            Image with chromatic aberration
        """
        if strength <= 0:
            return img
        
        img_rgb = img.convert('RGB')
        r, g, b = img_rgb.split()
        
        # Shift red and blue channels slightly
        shift = int(2 * strength * self.intensity)
        
        # Shift red channel
        r_array = np.array(r)
        r_shifted = np.roll(r_array, shift, axis=1)
        r = Image.fromarray(r_shifted)
        
        # Shift blue channel opposite direction
        b_array = np.array(b)
        b_shifted = np.roll(b_array, -shift, axis=1)
        b = Image.fromarray(b_shifted)
        
        return Image.merge('RGB', (r, g, b))

