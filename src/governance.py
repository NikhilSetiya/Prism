"""Compliance and governance checks for generated assets."""

from typing import Dict, List, Tuple, Optional
from PIL import Image
import numpy as np
from pathlib import Path
import os
import json
from openai import OpenAI


class ComplianceResult:
    """Result of compliance checks."""
    
    def __init__(self):
        self.passed = True
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.checks_performed: List[str] = []
    
    def add_warning(self, message: str):
        """Add a warning."""
        self.warnings.append(message)
        self.checks_performed.append(f"WARNING: {message}")
    
    def add_error(self, message: str):
        """Add an error and mark as failed."""
        self.errors.append(message)
        self.passed = False
        self.checks_performed.append(f"ERROR: {message}")
    
    def add_pass(self, check_name: str):
        """Record a passed check."""
        self.checks_performed.append(f"PASS: {check_name}")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'passed': self.passed,
            'warnings': self.warnings,
            'errors': self.errors,
            'checks_performed': self.checks_performed
        }


class GovernanceEngine:
    """Automated compliance and governance checks."""
    
    def __init__(self, config: Dict):
        """Initialize governance engine."""
        self.config = config
        self.governance_config = config.get('governance', {})
        self.brand_config = config.get('brand', {})
        
        # Load prohibited terms (backwards compatibility)
        self.prohibited_terms = set(
            term.lower() for term in self.governance_config.get('prohibited_terms', [])
        )
        
        # Load prohibited categories (configurable)
        self.prohibited_categories = self.governance_config.get('prohibited_categories', [
            'violence',
            'hate speech',
            'sexual content'
        ])
        
        # Brand color palette for validation
        self.brand_colors = self.brand_config.get('brand_colors', [])
        
        # Logo path for brand compliance
        self.logo_path = self.brand_config.get('logo_path', 'assets/brand/logo.png')
        
        # LLM validation setup
        if self.governance_config.get('llm_validation_enabled', True):
            api_key = config.get('generator', {}).get('api_key') or os.getenv('OPENAI_API_KEY')
            self.llm_client = OpenAI(api_key=api_key) if api_key else None
            self.llm_model = self.governance_config.get('llm_validation_model', 'gpt-4o-mini')
        else:
            self.llm_client = None
    
    def check_asset(self, image: Image.Image, campaign_message: str, 
                   product_id: str) -> ComplianceResult:
        """
        Run all compliance checks on an asset.
        
        Args:
            image: Generated image
            campaign_message: Campaign message text
            product_id: Product identifier
        
        Returns:
            ComplianceResult with findings
        """
        result = ComplianceResult()
        
        # Legal compliance
        if self.governance_config.get('legal_check_enabled', True):
            self._check_legal_terms(campaign_message, result)
        
        # Brand compliance
        if self.governance_config.get('brand_check_enabled', True):
            self._check_brand_presence(image, result)
            self._check_image_quality(image, result)
        
        # Content safety
        if self.governance_config.get('content_safety_enabled', False):
            self._check_content_safety(image, result)
        
        return result
    
    def _check_legal_terms(self, text: str, result: ComplianceResult):
        """Check for prohibited legal terms."""
        text_lower = text.lower()
        found_terms = [term for term in self.prohibited_terms if term in text_lower]
        
        if found_terms:
            result.add_error(f"Prohibited terms found: {', '.join(found_terms)}")
        else:
            result.add_pass("Legal terms check")
    
    def _check_brand_presence(self, image: Image.Image, result: ComplianceResult):
        """Check if brand elements are present (simplified check)."""
        # Check if logo file exists (runtime check)
        logo_exists = Path(self.logo_path).exists()
        
        if logo_exists:
            result.add_pass("Brand logo available")
        else:
            result.add_warning("Brand logo not found - may affect brand compliance")
    
    def _check_image_quality(self, image: Image.Image, result: ComplianceResult):
        """Validate image meets quality standards."""
        width, height = image.size
        min_resolution = self.governance_config.get('min_resolution', 1024)
        
        if min(width, height) < min_resolution:
            result.add_error(
                f"Image resolution {width}x{height} below minimum {min_resolution}px"
            )
        else:
            result.add_pass(f"Resolution check ({width}x{height})")
        
        # Check aspect ratio is reasonable
        aspect = max(width, height) / min(width, height)
        if aspect > 3.0:
            result.add_warning(f"Unusual aspect ratio: {aspect:.2f}:1")
    
    def _check_content_safety(self, image: Image.Image, result: ComplianceResult):
        """Placeholder for content safety checks (would use AI moderation in production)."""
        # In production: integrate Azure Content Safety or similar
        result.add_pass("Content safety check (placeholder)")
    
    def check_color_compliance(self, image: Image.Image) -> Tuple[bool, List[str]]:
        """
        Check if image uses brand-appropriate colors.
        
        Returns:
            (is_compliant, messages)
        """
        if not self.brand_colors:
            return True, ["No brand colors configured"]
        
        # Simplified check: ensure image isn't monochrome
        img_array = np.array(image.convert('RGB'))
        std_dev = img_array.std()
        
        if std_dev < 10:
            return False, ["Image appears monochrome - brand colors not evident"]
        
        return True, ["Color variance acceptable"]
    
    def validate_campaign_brief(self, brief) -> Dict:
        """
        Pre-flight LLM validation of campaign brief before generation.
        
        Args:
            brief: CampaignBrief object
        
        Returns:
            ValidationResult dict with errors, warnings, suggestions
        """
        if not self.llm_client:
            return {'passed': True, 'errors': [], 'warnings': ['LLM validation disabled'], 'suggestions': []}
        
        # Build validation prompt with prohibited categories
        prohibited_list = ", ".join(self.prohibited_categories)
        
        validation_prompt = f"""Validate this advertising campaign brief for image generation quality:

Campaign: {brief.campaign_id}
Message: {brief.campaign_message}
Target Audience: {brief.target_audience}
Region: {brief.region}

Products ({len(brief.products)}):
{self._format_products_for_validation(brief.products)}

Validate for:
1. Brand alignment - Does message match professional brand voice?
2. Prohibited content - Check for: {prohibited_list}
3. Completeness - Are all required fields present and clear?
4. Image generation quality - Will this produce good commercial imagery?

Respond in JSON:
{{"passed": true/false, "errors": [], "warnings": [], "suggestions": []}}

Errors = blocking issues that prevent generation. Warnings = proceed with caution. Suggestions = improvements."""

        try:
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are an advertising compliance expert. Validate campaign briefs for image generation."},
                    {"role": "user", "content": validation_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Apply blocking behavior if configured
            if self.governance_config.get('validation_blocking', True) and result.get('errors'):
                result['passed'] = False
            
            return result
            
        except Exception as e:
            return {
                'passed': False,
                'errors': [f"LLM validation failed: {str(e)}"],
                'warnings': [],
                'suggestions': []
            }
    
    def _format_products_for_validation(self, products) -> str:
        """Format products for LLM validation."""
        lines = []
        for p in products:
            lines.append(f"- {p.name}: {p.description}")
            lines.append(f"  Setting: {p.creative_brief.setting}")
            lines.append(f"  Mood: {p.creative_brief.mood}")
            lines.append(f"  Style: {p.brand_style.visual_style}")
        return "\n".join(lines)

