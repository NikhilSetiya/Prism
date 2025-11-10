# Input Assets Directory

Store pre-existing product images here to skip AI generation.

## Structure

```
assets/input/
├── {campaign_id}/
│   ├── {product_id}.png                    # Generic (all aspect ratios)
│   ├── {product_id}_1x1.png               # Square format
│   ├── {product_id}_9x16.png              # Vertical format  
│   └── {product_id}_16x9.png              # Horizontal format
```

## Priority Order

The asset manager checks in this order:

1. `assets/input/{campaign_id}/{product_id}_{aspect_ratio}.png` (specific)
2. `assets/input/{campaign_id}/{product_id}.png` (generic)
3. `assets/input/{product_id}_{aspect_ratio}.png` (fallback specific)
4. `assets/input/{product_id}.png` (fallback generic)
5. Generate with DALL-E 3 (if none found)

## Example

For campaign `fittech_2025` with product `pulse_smartwatch`:

```bash
assets/input/fittech_2025/pulse_smartwatch.png
```

This image will be used for all aspect ratios instead of generating new ones.

## Asset Requirements

- **Format:** PNG or JPG
- **Resolution:** Minimum 1024px on shortest side
- **Quality:** High resolution recommended
- **Naming:** Must match product ID from campaign brief exactly

## Cost Impact

Campaign costs with input assets:
- **User-provided assets:** $0.0015 per campaign (validation only)
- **Generated heroes:** $0.08 per hero image
- **Variations & composition:** $0.00 (local processing)
