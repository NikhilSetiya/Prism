"""Gallery helper functions for asset display and management."""

import zipfile
from pathlib import Path
from typing import List, Dict, Tuple
from io import BytesIO


def list_campaigns() -> List[str]:
    """Get all campaign IDs from output directory."""
    output_dir = Path("output")
    if not output_dir.exists():
        return []
    return [d.name for d in output_dir.iterdir() if d.is_dir()]


def load_campaign_assets(campaign_id: str) -> Dict[str, List[Path]]:
    """
    Load all assets for a campaign grouped by product.
    
    Returns:
        Dict mapping product_id to list of asset paths
    """
    campaign_path = Path("output") / campaign_id
    if not campaign_path.exists():
        return {}
    
    assets_by_product = {}
    for product_dir in campaign_path.iterdir():
        if product_dir.is_dir():
            product_id = product_dir.name
            assets = list(product_dir.glob("*.png"))
            assets_by_product[product_id] = sorted(assets)
    
    return assets_by_product


def get_asset_info(asset_path: Path) -> Tuple[str, str]:
    """
    Extract aspect ratio and locale from asset filename.
    
    Filename format: {aspect_ratio}_{locale}.png
    Example: 1x1_en.png -> ("1x1", "en")
    """
    name = asset_path.stem
    parts = name.split('_')
    if len(parts) >= 2:
        aspect_ratio = parts[0]
        locale = parts[1]
        return aspect_ratio, locale
    return "unknown", "unknown"


def create_campaign_zip(campaign_id: str) -> BytesIO:
    """Create ZIP archive of all assets for a campaign."""
    zip_buffer = BytesIO()
    campaign_path = Path("output") / campaign_id
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for product_dir in campaign_path.iterdir():
            if product_dir.is_dir():
                for asset in product_dir.glob("*.png"):
                    # Archive path: {product_id}/{filename}
                    arcname = f"{product_dir.name}/{asset.name}"
                    zip_file.write(str(asset), arcname)
    
    zip_buffer.seek(0)
    return zip_buffer


def get_locales_from_assets(assets: List[Path]) -> List[str]:
    """Extract unique locales from asset list."""
    locales = set()
    for asset in assets:
        _, locale = get_asset_info(asset)
        locales.add(locale)
    return sorted(list(locales))


def get_aspect_ratios_from_assets(assets: List[Path]) -> List[str]:
    """Extract unique aspect ratios from asset list."""
    ratios = set()
    for asset in assets:
        ratio, _ = get_asset_info(asset)
        ratios.add(ratio)
    # Return in specific order
    order = ["1x1", "9x16", "16x9"]
    return [r for r in order if r in ratios]


