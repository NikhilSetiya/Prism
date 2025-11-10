#!/usr/bin/env python3
"""Interactive campaign brief builder with guided input."""

import json
import sys
from pathlib import Path


def prompt_with_hint(question: str, hint: str, default: str = None) -> str:
    """Prompt user with helpful hint."""
    print(f"\n{question}")
    print(f"💡 Hint: {hint}")
    if default:
        print(f"   (Press Enter for default: {default})")
    
    response = input("➤ ").strip()
    return response or default


def prompt_list(question: str, hint: str, min_items: int = 1) -> list:
    """Prompt user for comma-separated list."""
    print(f"\n{question}")
    print(f"💡 Hint: {hint}")
    print("   (Enter comma-separated values)")
    
    while True:
        response = input("➤ ").strip()
        items = [item.strip() for item in response.split(',') if item.strip()]
        if len(items) >= min_items:
            return items
        print(f"❌ Please enter at least {min_items} item(s).")


def create_product() -> dict:
    """Create a product interactively."""
    print("\n" + "="*60)
    print("PRODUCT CONFIGURATION")
    print("="*60)
    
    product_id = prompt_with_hint(
        "Product ID (filesystem-safe, lowercase with underscores)",
        "Example: shampoo_citrus_500ml, bodywash_mint_400ml"
    )
    
    name = prompt_with_hint(
        "Product Name",
        "Brand-friendly name shown in marketing",
        "Premium Product"
    )
    
    description = prompt_with_hint(
        "Product Description (10-500 chars)",
        "Detailed product description with key benefits",
        "High-quality product with natural ingredients"
    )
    
    category = prompt_with_hint(
        "Product Category",
        "Examples: haircare, skincare, bodycare, cosmetics",
        "personal_care"
    )
    
    # Creative Brief
    print("\n" + "-"*60)
    print("CREATIVE BRIEF")
    print("-"*60)
    
    setting = prompt_with_hint(
        "Setting/Environment",
        "Where product is shown: studio, bathroom, natural outdoor, lifestyle",
        "Clean studio environment"
    )
    
    mood = prompt_with_hint(
        "Mood/Tone",
        "Emotional feeling: energetic, calm, luxurious, fresh, vibrant",
        "Fresh and clean"
    )
    
    visual_elements = prompt_list(
        "Key Visual Elements",
        "Important elements to include in image (e.g., water splash, natural light, product bottle)",
        min_items=2
    )
    
    # Brand Style
    print("\n" + "-"*60)
    print("BRAND STYLE")
    print("-"*60)
    
    color_palette = prompt_list(
        "Brand Colors (hex codes)",
        "2-5 brand colors in hex format (e.g., #FF6B35, #004E89, #FFFFFF)",
        min_items=2
    )
    
    visual_style = prompt_with_hint(
        "Visual Style",
        "Overall aesthetic: modern minimalist, natural organic, bold vibrant, elegant classic",
        "Clean and modern"
    )
    
    photography_style = prompt_with_hint(
        "Photography Style",
        "Photography approach: commercial product, lifestyle editorial, artistic creative",
        "Commercial product photography"
    )
    
    return {
        "id": product_id,
        "name": name,
        "description": description,
        "category": category,
        "creative_brief": {
            "setting": setting,
            "mood": mood,
            "key_visual_elements": visual_elements
        },
        "brand_style": {
            "color_palette": color_palette,
            "visual_style": visual_style,
            "photography_style": photography_style
        }
    }


def create_campaign_brief() -> dict:
    """Create a complete campaign brief interactively."""
    print("\n" + "="*60)
    print("🎨 PRISM - Interactive Campaign Builder")
    print("="*60)
    print("\nThis wizard will guide you through creating a campaign brief.")
    print("Follow the prompts and hints to configure your campaign.\n")
    
    campaign_id = prompt_with_hint(
        "Campaign ID (filesystem-safe, lowercase with underscores)",
        "Example: summer_2025_launch, holiday_campaign_2024",
        "my_campaign_2025"
    )
    
    region = prompt_with_hint(
        "Target Region",
        "Examples: EMEA, NA (North America), APAC, LATAM",
        "EMEA"
    )
    
    target_audience = prompt_with_hint(
        "Target Audience",
        "Demographics: millennials_25-35, gen_z_18-24, families_30-45",
        "millennials_25-35"
    )
    
    campaign_message = prompt_with_hint(
        "Campaign Message (5-200 chars)",
        "Main tagline/headline: 'Discover Summer Freshness', 'Unleash Your Glow'",
        "Experience Excellence"
    )
    
    locales = prompt_list(
        "Target Locales (language codes)",
        "Examples: en (English), fr (French), de (German), es (Spanish), ja (Japanese)",
        min_items=1
    )
    
    # Products
    products = []
    while True:
        print(f"\n{'='*60}")
        print(f"PRODUCT {len(products) + 1}")
        print(f"{'='*60}")
        
        product = create_product()
        products.append(product)
        
        if len(products) >= 2:
            add_more = input("\nAdd another product? (y/N): ").strip().lower()
            if add_more not in ['y', 'yes']:
                break
        else:
            print("\n⚠️  At least 2 products required for campaign.")
    
    return {
        "campaign_id": campaign_id,
        "region": region,
        "target_audience": target_audience,
        "campaign_message": campaign_message,
        "locales": locales,
        "products": products
    }


def main():
    """Main entry point."""
    try:
        # Create campaign brief
        brief = create_campaign_brief()
        
        # Save to file
        filename = f"{brief['campaign_id']}_brief.json"
        output_path = Path(filename)
        
        with open(output_path, 'w') as f:
            json.dump(brief, f, indent=2)
        
        print("\n" + "="*60)
        print("✅ CAMPAIGN BRIEF CREATED SUCCESSFULLY")
        print("="*60)
        print(f"Saved to: {output_path.absolute()}")
        print(f"\nCampaign: {brief['campaign_id']}")
        print(f"Products: {len(brief['products'])}")
        print(f"Locales: {', '.join(brief['locales'])}")
        print("\nNext steps:")
        print(f"  1. Review the brief: cat {filename}")
        print(f"  2. Run campaign: python run_prism.py --campaign {filename}")
        print("="*60)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Campaign creation cancelled.")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

