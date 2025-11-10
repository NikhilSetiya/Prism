"""Asset composition with text overlay and brand elements."""

import os
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pathlib import Path

from src.utils import ensure_dir


# Text positioning by aspect ratio
TEXT_POSITIONS = {
    "1:1": "bottom_third",      # 67-90% height
    "9:16": "bottom_quarter",   # 75-95% height
    "16:9": "bottom_third"      # 67-90% height
}


class AssetCompositor:
    """Compose final assets with text overlay and brand elements."""
    
    def __init__(self, config: dict):
        """Initialize compositor with configuration."""
        self.config = config
        self.text_config = config.get('text_overlay', {})
        self.brand_config = config.get('brand', {})
        
        # Text styling
        self.font_path = self.text_config.get('font', 'assets/brand/Helvetica-Bold.ttf')
        self.font_size = self.text_config.get('font_size', 48)
        self.text_color = self.text_config.get('color', '#FFFFFF')
        self.outline_color = self.text_config.get('outline_color', '#000000')
        self.outline_width = self.text_config.get('outline_width', 2)
        
        # Brand elements
        self.logo_position = self.brand_config.get('logo_position', 'bottom_right')
        self.logo_opacity = self.brand_config.get('logo_opacity', 0.9)
        self.logo_scale = self.brand_config.get('logo_scale', 0.1)
    
    def compose(self, base_image: Image.Image, campaign_message: str,
               aspect_ratio: str, locale: str, campaign_id: str) -> Image.Image:
        """
        Compose final asset with text overlay and brand elements.
        
        Args:
            base_image: Base generated image
            campaign_message: Campaign message to overlay
            aspect_ratio: Aspect ratio string
            locale: Locale code
            campaign_id: Campaign identifier for campaign-specific assets
        
        Returns:
            Composed image with text and brand elements
        """
        # Create a copy to avoid modifying original
        img = base_image.copy()
        
        # Overlay text
        img = self._overlay_text(img, campaign_message, aspect_ratio)
        
        # Overlay campaign-specific logo if available (no fallback to generic logo)
        campaign_logo_path = f"assets/brand/{campaign_id}/logo.png"
        if os.path.exists(campaign_logo_path):
            img = self._overlay_logo(img, aspect_ratio, campaign_logo_path)
        
        return img
    
    def _overlay_text(self, img: Image.Image, text: str, aspect_ratio: str) -> Image.Image:
        """Overlay text on image with proper positioning and styling."""
        draw = ImageDraw.Draw(img)
        img_width, img_height = img.size
        
        # Calculate font size based on image resolution
        base_font_size = int(self.font_size * (img_width / 1024))
        
        # Load font with fallback chain
        font = self._load_font_with_fallback(base_font_size)
        
        # Get text position based on aspect ratio
        text_zone = TEXT_POSITIONS.get(aspect_ratio, "bottom_third")
        box_position = self._get_text_position(img_width, img_height, text_zone)
        
        # Wrap text to fit within image width
        max_width = int(img_width * 0.85)  # 85% of image width for better margins
        lines = self._wrap_text(text, font, max_width)
        
        # Dynamic font sizing if text still too long
        if len(lines) > 3:  # More than 3 lines, reduce font size
            font = self._scale_font_to_fit(text, max_width, base_font_size, max_lines=3)
            lines = self._wrap_text(text, font, max_width)
        
        # Calculate text block dimensions using actual line measurements
        line_spacing = 10
        line_heights = []
        line_widths = []
        for line in lines:
            bbox = font.getbbox(line)
            line_heights.append(bbox[3] - bbox[1])
            line_widths.append(bbox[2] - bbox[0])
        
        total_height = sum(line_heights) + (line_spacing * (len(lines) - 1))
        max_line_width = max(line_widths) if line_widths else 0
        
        # Add semi-transparent background for better readability
        # Account for outline width and add generous padding
        outline_padding = self.outline_width * 2
        padding = 25 + outline_padding
        
        bg_x1 = max(0, box_position[0] - (max_line_width // 2) - padding)
        bg_y1 = max(0, box_position[1] - (total_height // 2) - padding)
        bg_x2 = min(img_width, box_position[0] + (max_line_width // 2) + padding)
        bg_y2 = min(img_height, box_position[1] + (total_height // 2) + padding)
        
        # Draw semi-transparent background
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=(0, 0, 0, 128))
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)
        
        # Calculate text offset adjustment based on aspect ratio (move text down within box)
        aspect = img_width / img_height
        if 0.9 <= aspect <= 1.1:  # 1:1 square
            text_offset_adj = int(total_height * 0.17)  # Move text down 17% of text height
        elif aspect < 0.9:  # 9:16 portrait
            text_offset_adj = int(total_height * 0.22)  # Move text down 22% of text height
        else:  # 16:9 landscape
            text_offset_adj = int(total_height * 0.20)  # Move text down 20% of text height
        
        # Draw each line with centered anchor (using 'mm' = middle-middle)
        y_offset = -(total_height // 2) + text_offset_adj
        for i, line in enumerate(lines):
            y_pos = box_position[1] + y_offset
            
            # Draw text with outline and proper center anchoring
            self._draw_text_with_outline(
                draw, line, (box_position[0], y_pos), font,
                self.text_color, self.outline_color, self.outline_width,
                anchor="mm"
            )
        
            y_offset += line_heights[i] + line_spacing
        
        return img.convert('RGB')
    
    def _load_font_with_fallback(self, font_size: int) -> ImageFont.FreeTypeFont:
        """
        Load font with fallback chain.
        
        Tries in order:
        1. Configured font path
        2. System fonts (Arial, Helvetica, DejaVu Sans)
        3. PIL default font
        """
        # Try configured font
        if os.path.exists(self.font_path):
            try:
                return ImageFont.truetype(self.font_path, font_size)
            except Exception:
                pass
        
        # Try common system fonts
        system_fonts = [
            '/System/Library/Fonts/Helvetica.ttc',  # macOS
            '/System/Library/Fonts/Supplemental/Arial.ttf',  # macOS
            'C:\\Windows\\Fonts\\arial.ttf',  # Windows
            'C:\\Windows\\Fonts\\Helvetica.ttf',  # Windows
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',  # Linux
        ]
        
        for font_path in system_fonts:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except Exception:
                    continue
        
        # Fallback to PIL default font
        print("Warning: Using PIL default font. Text may not render optimally.")
        return ImageFont.load_default()
    
    def _get_text_position(self, width: int, height: int, text_zone: str) -> Tuple[int, int]:
        """Get text position based on zone specification."""
        if text_zone == "bottom_third":
            # Center horizontally, bottom third vertically
            # Used for 1:1 (84%) and 16:9 (85%)
            x = width // 2
            # Differentiate between 1:1 and 16:9 based on aspect ratio
            aspect = width / height
            if 0.9 <= aspect <= 1.1:  # 1:1 square
                y = int(height * 0.84)  # 84% from top (1:1)
            else:  # 16:9 landscape
                y = int(height * 0.85)  # 85% from top (16:9)
        elif text_zone == "bottom_quarter":
            # Center horizontally, bottom quarter vertically (9:16 portrait)
            x = width // 2
            y = int(height * 0.90)  # 90% from top (9:16)
        else:
            # Default to center
            x = width // 2
            y = height // 2
        
        return (x, y)
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text to fit within max_width, preserving words."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Get text bounding box
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def _scale_font_to_fit(self, text: str, max_width: int, initial_size: int, max_lines: int = 3) -> ImageFont.FreeTypeFont:
        """Dynamically scale font size to fit text within constraints."""
        font_size = initial_size
        min_font_size = 20
        
        while font_size > min_font_size:
            font = self._load_font_with_fallback(font_size)
            lines = self._wrap_text(text, font, max_width)
            
            if len(lines) <= max_lines:
                return font
            
            # Reduce font size by 10%
            font_size = int(font_size * 0.9)
        
        # Return minimum font size
        return self._load_font_with_fallback(min_font_size)
    
    def _draw_text_with_outline(self, draw: ImageDraw.Draw, text: str,
                               position: Tuple[int, int], font: ImageFont.FreeTypeFont,
                               fill_color: str, outline_color: str, outline_width: int,
                               anchor: str = "mm"):
        """Draw text with outline for readability and proper centering."""
        x, y = position
        
        # Draw outline (multiple passes for thicker outline)
        for adj in range(-outline_width, outline_width + 1):
            for adj2 in range(-outline_width, outline_width + 1):
                if adj != 0 or adj2 != 0:
                    draw.text((x + adj, y + adj2), text, font=font, fill=outline_color, anchor=anchor)
        
        # Draw main text with anchor for perfect centering
        draw.text(position, text, font=font, fill=fill_color, anchor=anchor)
    
    def _overlay_logo(self, img: Image.Image, aspect_ratio: str, logo_path: str) -> Image.Image:
        """Overlay brand logo on image."""
        # Check if logo file exists and is valid
        if not os.path.exists(logo_path):
            return img
        
        try:
            # Try to open and verify it's a valid image
            logo = Image.open(logo_path)
            logo.verify()  # Verify the image file
            logo = Image.open(logo_path)  # Reopen after verify() closes it
            img_width, img_height = img.size
            
            # Resize logo (10% of image width by default)
            logo_size = int(img_width * self.logo_scale)
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Apply opacity
            if self.logo_opacity < 1.0:
                alpha = logo.split()[3] if logo.mode == 'RGBA' else None
                if alpha:
                    alpha = ImageEnhance.Brightness(alpha).enhance(self.logo_opacity)
                    logo.putalpha(alpha)
                else:
                    logo = logo.convert('RGBA')
                    alpha = logo.split()[3]
                    alpha = ImageEnhance.Brightness(alpha).enhance(self.logo_opacity)
                    logo.putalpha(alpha)
            
            # Get logo position
            logo_x, logo_y = self._get_logo_position(
                img_width, img_height, logo.width, logo.height, self.logo_position
            )
            
            # Paste logo on image
            if logo.mode == 'RGBA':
                img.paste(logo, (logo_x, logo_y), logo)
            else:
                img.paste(logo, (logo_x, logo_y))
            
        except Exception as e:
            print(f"Warning: Could not overlay logo: {e}")
        
        return img
    
    def _get_logo_position(self, img_width: int, img_height: int,
                          logo_width: int, logo_height: int, position: str) -> Tuple[int, int]:
        """Get logo position based on configuration."""
        margin = 20  # Margin from edges
        
        if position == "bottom_right":
            x = img_width - logo_width - margin
            y = img_height - logo_height - margin
        elif position == "bottom_left":
            x = margin
            y = img_height - logo_height - margin
        elif position == "top_right":
            x = img_width - logo_width - margin
            y = margin
        elif position == "top_left":
            x = margin
            y = margin
        else:
            # Default to bottom right
            x = img_width - logo_width - margin
            y = img_height - logo_height - margin
        
        return (x, y)

