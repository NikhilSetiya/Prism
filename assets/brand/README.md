# Brand Assets Directory

Store campaign-specific brand logos here.

## Structure

```
assets/brand/
├── {campaign_id}/
│   └── logo.png          # Campaign-specific logo
```

## Usage

The pipeline automatically looks for campaign-specific logos at:
- `assets/brand/{campaign_id}/logo.png`

If not found, no logo is added to the generated assets (no generic fallback).

## Example

For a campaign with `campaign_id: "fittech_2025"`:

```bash
assets/brand/fittech_2025/logo.png
```

This logo will be applied to all assets generated for that campaign.

## Logo Requirements

- **Format:** PNG (with transparency recommended)
- **Size:** Square format (e.g., 400×400px or higher)
- **Quality:** High resolution for best results
- **Naming:** Must be named `logo.png` within campaign directory
