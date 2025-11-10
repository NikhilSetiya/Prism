"""Data models for Prism campaign pipeline using Pydantic for validation."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum


class AspectRatio(str, Enum):
    """Supported aspect ratios for social media."""
    SQUARE = "1:1"
    VERTICAL = "9:16"
    HORIZONTAL = "16:9"


class BrandStyle(BaseModel):
    """Brand styling guidelines."""
    color_palette: List[str] = Field(..., min_length=1, max_length=5)
    visual_style: str
    photography_style: str = "Commercial product photography"


class CreativeBrief(BaseModel):
    """Creative direction for asset generation."""
    setting: str
    mood: str
    key_visual_elements: List[str] = Field(..., min_length=1)


class Product(BaseModel):
    """Product information and creative brief."""
    id: str = Field(..., pattern=r'^[a-z0-9_]+$')
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    category: str
    creative_brief: CreativeBrief
    brand_style: BrandStyle

    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Ensure product ID is filesystem-safe."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Product ID must be alphanumeric with underscores/hyphens')
        return v


class CampaignBrief(BaseModel):
    """Complete campaign specification."""
    campaign_id: str = Field(..., pattern=r'^[a-z0-9_]+$')
    region: str
    target_audience: str
    campaign_message: str = Field(..., min_length=5, max_length=200)
    locales: List[str] = Field(default_factory=lambda: ["en"], min_length=1)
    products: List[Product] = Field(..., min_length=1, max_length=10)

    @field_validator('campaign_id')
    @classmethod
    def validate_campaign_id(cls, v: str) -> str:
        """Ensure campaign ID is filesystem-safe."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Campaign ID must be alphanumeric with underscores/hyphens')
        return v


class ValidationResult(BaseModel):
    """Result of pre-flight campaign validation."""
    passed: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class GeneratedAsset(BaseModel):
    """Metadata for generated asset."""
    product_id: str
    aspect_ratio: AspectRatio
    locale: str
    file_path: str
    generation_cost: float
    cached: bool = False
    compliance_passed: bool = True
    compliance_warnings: List[str] = Field(default_factory=list)
    compliance_errors: List[str] = Field(default_factory=list)


class ExecutionReport(BaseModel):
    """Campaign execution summary."""
    campaign_id: str
    products_count: int
    assets_generated: int
    assets_reused: int
    total_cost: float
    execution_time: float
    cache_efficiency: float
    output_path: str
    errors: List[str] = Field(default_factory=list)
    timings: Optional[Dict[str, Any]] = None  # Changed to Any to allow nested dicts
    compliance_summary: Optional[Dict[str, int]] = None
    worker_count: int = 3
    
    # Hero + variations tracking
    hero_images_generated: int = 0
    hero_images_cached: int = 0
    variations_created: int = 0

