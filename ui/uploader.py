"""File upload handling functions."""

from pathlib import Path
from typing import List, Optional
from PIL import Image
import streamlit as st


def save_input_assets(uploaded_files: List, input_dir: str = "assets/input") -> List[str]:
    """
    Save uploaded images to assets/input directory.
    
    Returns:
        List of saved file paths
    """
    input_path = Path(input_dir)
    input_path.mkdir(parents=True, exist_ok=True)
    
    saved_paths = []
    for uploaded_file in uploaded_files:
        # Save with original filename
        file_path = input_path / uploaded_file.name
        
        try:
            # Load and save as PIL Image to validate
            img = Image.open(uploaded_file)
            img.save(str(file_path))
            saved_paths.append(str(file_path))
        except Exception as e:
            st.error(f"Failed to save {uploaded_file.name}: {e}")
    
    return saved_paths


def validate_asset_naming(filename: str, product_ids: List[str]) -> Optional[str]:
    """
    Check if asset filename matches expected pattern.
    
    Expected patterns:
    - {product_id}.png
    - {product_id}_{aspect_ratio}.png
    
    Returns:
        None if valid, error message if invalid
    """
    name_without_ext = filename.rsplit('.', 1)[0]
    
    # Check if it matches any product ID
    for product_id in product_ids:
        if name_without_ext == product_id:
            return None
        if name_without_ext.startswith(f"{product_id}_"):
            return None
    
    return f"Filename '{filename}' doesn't match any product ID: {', '.join(product_ids)}"


def list_existing_assets(input_dir: str = "assets/input") -> List[Path]:
    """List all existing assets in input directory."""
    input_path = Path(input_dir)
    if not input_path.exists():
        return []
    
    return sorted(list(input_path.glob("*.png")) + list(input_path.glob("*.jpg")))


def delete_asset(asset_path: Path) -> bool:
    """Delete an asset file."""
    try:
        asset_path.unlink()
        return True
    except Exception:
        return False

