"""Main pipeline orchestrator for Prism campaign processing."""

import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Tuple
from pathlib import Path
from PIL import Image

from src.models import CampaignBrief, AspectRatio, ExecutionReport, GeneratedAsset
from src.image_generator import ImageGenerator
from src.asset_manager import AssetManager
from src.aspect_ratio_processor import AspectRatioProcessor
from src.compositor import AssetCompositor
from src.localizer import Localizer
from src.storage import LocalStorage
from src.governance import GovernanceEngine
from src.post_processor import PostProcessor
from src.utils import Config, ExecutionContext, RateLimiter, ensure_dir, save_json


class CampaignPipeline:
    """Main pipeline for processing campaign briefs."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize pipeline with configuration."""
        self.config = config
        
        # Initialize components
        self.image_generator = ImageGenerator(config)
        self.aspect_processor = AspectRatioProcessor(config)
        self.localizer = Localizer(config)
        self.compositor = AssetCompositor(config)
        self.governance = GovernanceEngine(config)
        self.post_processor = PostProcessor(config)
        
        # Initialize storage
        storage_config = config.get('storage', {}).get('local', {})
        cache_storage = LocalStorage(storage_config.get('cache_base', './cache'))
        output_storage = LocalStorage(storage_config.get('output_base', './output'))
        
        self.asset_manager = AssetManager(config, self.image_generator, cache_storage)
        self.output_storage = output_storage
        
        # Rate limiter
        generator_config = config.get('generator', {})
        self.rate_limiter = RateLimiter(generator_config.get('rate_limit', 45))
        
        # Aspect ratios from config
        self.aspect_ratios = [
            AspectRatio(ratio) for ratio in config.get('campaign', {}).get('aspect_ratios', ['1:1', '9:16', '16:9'])
        ]
        
        # Worker configuration
        self.max_workers = config.get('scalability', {}).get('max_workers', 3)
    
    def run(self, brief: CampaignBrief) -> ExecutionReport:
        """
        Run the campaign pipeline in 3 phases:
        Phase 1: Get/generate hero images
        Phase 2: Create aspect ratio variations
        Phase 3: Compose with text/logo and validate
        
        Args:
            brief: Campaign brief with products and configuration
        
        Returns:
            Execution report with metrics
        """
        # Pre-flight validation
        validation_result = self.governance.validate_campaign_brief(brief)
        if not validation_result.get('passed', True):
            errors = validation_result.get('errors', [])
            error_msg = "Campaign validation failed:\n" + "\n".join(f"- {e}" for e in errors)
            raise ValueError(error_msg)
        
        # Log warnings and suggestions
        if validation_result.get('warnings'):
            print("⚠️  Validation warnings:")
            for w in validation_result['warnings']:
                print(f"  - {w}")
        if validation_result.get('suggestions'):
            print("💡 Suggestions:")
            for s in validation_result['suggestions']:
                print(f"  - {s}")
        
        with ExecutionContext(brief.campaign_id) as ctx:
            ctx.products_count = len(brief.products)
            
            # PHASE 1: Get/Generate Hero Images (expensive operations)
            print(f"\n🎨 Phase 1: Getting/generating hero images for {len(brief.products)} product(s)...")
            heroes = self._get_heroes(brief, ctx)
            
            # PHASE 2: Create Aspect Ratio Variations (local processing)
            print(f"\n✂️  Phase 2: Creating aspect ratio variations...")
            variants = self._create_all_variations(heroes, ctx)
            
            # PHASE 3: Compose, Localize, and Validate (parallel)
            print(f"\n🎭 Phase 3: Composing with text/logo and validating...")
            results = self._compose_all_assets(variants, brief, ctx)
            
            # Generate execution report with compliance summary
            report_data = ctx.get_report()
            report_data['products_count'] = len(brief.products)
            report_data['worker_count'] = self.max_workers
            
            # Aggregate compliance results
            compliance_summary = {
                'total_assets': len(results),
                'passed': sum(1 for r in results if r.compliance_passed),
                'warnings': sum(len(r.compliance_warnings) for r in results),
                'errors': sum(len(r.compliance_errors) for r in results)
            }
            report_data['compliance_summary'] = compliance_summary
            
            # Save execution report
            report = ExecutionReport(**report_data)
            self._save_execution_report(report, brief.campaign_id)
            
            print(f"\n✅ Campaign complete: {len(results)} assets generated")
            print(f"   Heroes: {ctx.hero_images_generated} generated, {ctx.hero_images_cached} cached")
            print(f"   Variations: {ctx.variations_created} created")
            print(f"   Total cost: ${ctx.get_total_cost():.3f}")
            
            return report
    
    def _get_heroes(self, brief: CampaignBrief, ctx: ExecutionContext) -> Dict[str, Image.Image]:
        """
        Phase 1: Get or generate hero images for all products.
        
        Returns:
            Dictionary mapping product_id to post-processed hero image
        """
        heroes = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._get_or_generate_hero, product, brief, ctx): product.id
                for product in brief.products
            }
            
            for future in as_completed(futures):
                product_id = futures[future]
                try:
                    hero_image, is_cached, cost = future.result()
                    heroes[product_id] = hero_image
                    
                    # Track metrics
                    if is_cached:
                        ctx.hero_images_cached += 1
                    else:
                        ctx.hero_images_generated += 1
                        ctx.record_cost(cost)
                    
                except Exception as e:
                    error_msg = f"Failed to get hero for {product_id}: {e}"
                    ctx.record_error(error_msg)
                    print(f"❌ {error_msg}")
        
        return heroes
    
    def _get_or_generate_hero(self, product, brief: CampaignBrief, ctx: ExecutionContext) -> Tuple[Image.Image, bool, float]:
        """
        Get or generate a hero image for a product.
        
        Returns:
            Tuple of (post-processed hero image, is_cached, cost)
        """
        # Rate limit for API calls
        self.rate_limiter.acquire()
        
        # Get or generate base hero image
        hero_image, is_cached, cost = self.asset_manager.get_or_generate_hero(
            product, brief
        )
        
        # Apply post-processing to hero (film-like effects)
        processed_hero = self.post_processor.process(hero_image)
        
        if is_cached:
            print(f"   ✓ Hero cache HIT for {product.id}")
        else:
            print(f"   ✓ Hero generated for {product.id} (${cost:.3f})")
        
        return processed_hero, is_cached, cost
    
    def _create_all_variations(self, heroes: Dict[str, Image.Image], 
                               ctx: ExecutionContext) -> Dict[str, Dict[str, Image.Image]]:
        """
        Phase 2: Create aspect ratio variations from hero images.
        
        Returns:
            Nested dict: {product_id: {aspect_ratio: image}}
        """
        variants = {}
        
        for product_id, hero in heroes.items():
            variants[product_id] = {}
            for aspect_ratio in self.aspect_ratios:
                variant = self.aspect_processor.create_variation(hero, aspect_ratio.value)
                variants[product_id][aspect_ratio.value] = variant
                ctx.variations_created += 1
            
            print(f"   ✓ Created {len(self.aspect_ratios)} variations for {product_id}")
        
        return variants
    
    def _compose_all_assets(self, variants: Dict[str, Dict[str, Image.Image]], 
                           brief: CampaignBrief, ctx: ExecutionContext) -> List[GeneratedAsset]:
        """
        Phase 3: Compose all assets with text/logo and validate.
        
        Returns:
            List of GeneratedAsset objects
        """
        # Build tasks list
        tasks = []
        for product in brief.products:
            if product.id not in variants:
                continue
            for aspect_ratio in self.aspect_ratios:
                for locale in brief.locales:
                    tasks.append((product, aspect_ratio, locale, brief, variants))
        
        # Process in parallel
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._compose_asset, product, ratio, locale, brief, variants, ctx): 
                (product.id, ratio.value, locale)
                for product, ratio, locale, brief, variants in tasks
            }
            
            for future in as_completed(futures):
                product_id, aspect_ratio, locale = futures[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    error_msg = f"Failed to compose {product_id}_{aspect_ratio}_{locale}: {e}"
                    ctx.record_error(error_msg)
                    print(f"❌ {error_msg}")
        
        return results
    
    def _compose_asset(self, product, aspect_ratio: AspectRatio, locale: str,
                      brief: CampaignBrief, variants: Dict[str, Dict[str, Image.Image]], 
                      ctx: ExecutionContext) -> GeneratedAsset:
        """Compose a single asset from a variation."""
        start_time = time.time()
        
        try:
            # Get the variation for this product and aspect ratio
            base_image = variants[product.id][aspect_ratio.value]
            
            # Localize message
            localized_message = self.localizer.localize_message(
                brief.campaign_message, locale, brief.region
            )
            
            # Compose final asset with text and brand elements
            composed_image = self.compositor.compose(
                base_image, localized_message, aspect_ratio.value, locale, brief.campaign_id
            )
            
            # Run compliance checks
            compliance_result = self.governance.check_asset(
                composed_image, localized_message, product.id
            )
            
            # Save to output
            output_path = self._save_output(
                brief.campaign_id, product.id, aspect_ratio.value, locale, composed_image
            )
            
            # Record compliance issues
            if not compliance_result.passed:
                ctx.record_error(f"{product.id}_{aspect_ratio.value}_{locale}: Compliance failed")
            
            # Record timing
            duration = time.time() - start_time
            ctx.record_timing(f"{product.id}_{aspect_ratio.value}_{locale}", duration)
            
            return GeneratedAsset(
                product_id=product.id,
                aspect_ratio=aspect_ratio,
                locale=locale,
                file_path=output_path,
                generation_cost=0.0,  # No cost for composition (cost tracked at hero level)
                cached=False,  # This is a variation, not cached
                compliance_passed=compliance_result.passed,
                compliance_warnings=compliance_result.warnings,
                compliance_errors=compliance_result.errors
            )
            
        except Exception as e:
            ctx.record_error(f"{product.id}_{aspect_ratio.value}_{locale}: {e}")
            raise
    
    def _save_output(self, campaign_id: str, product_id: str,
                    aspect_ratio: str, locale: str, image) -> str:
        """Save final asset to output directory."""
        # Format: output/[campaign_id]/[product_id]/[aspect_ratio]_[locale].png
        aspect_str = aspect_ratio.replace(':', 'x')
        filename = f"{aspect_str}_{locale}.png"
        output_path = f"{campaign_id}/{product_id}/{filename}"
        
        return self.output_storage.save(output_path, image)
    
    def _save_execution_report(self, report: ExecutionReport, campaign_id: str):
        """Save execution report to logs."""
        log_dir = Path("logs")
        ensure_dir(str(log_dir))
        
        log_file = log_dir / f"{campaign_id}_execution.json"
        save_json(report.model_dump(), str(log_file))
