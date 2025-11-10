# Prism Test Campaigns Package

Complete offline test package with 2 campaigns, brand assets, and input images.

## Contents

### Campaign 1: FitTech 2025
**Target:** Fitness enthusiasts (25-40), North America  
**Message:** "Your Fitness, Elevated"  
**Products:**
- Pulse Pro Smartwatch (advanced fitness tracking)
- AirFlow Wireless Earbuds (workout-optimized)

**Assets:**
- `fittech_2025/brand/logo.png` - Brand logo
- `fittech_2025/input/pulse_smartwatch.png` - Product asset
- `fittech_2025/input/airflow_earbuds.png` - Product asset

### Campaign 2: Urban Brew 2025
**Target:** Urban professionals (28-45), EMEA  
**Message:** "Craft Your Day"  
**Products:**
- Urban Cold Brew Original (single-origin coffee)
- Urban Energize+ Drink (natural energy drink)

**Assets:**
- `urban_brew_2025/brand/logo.png` - Brand logo
- `urban_brew_2025/input/cold_brew_original.png` - Product asset
- `urban_brew_2025/input/energize_plus.png` - Product asset

## Setup Instructions

### 1. Copy to Prism Project

```bash
# From test_campaigns_package directory
cp -r fittech_2025/brand assets/brand/
cp -r fittech_2025/input/* assets/input/fittech_2025/
mkdir -p assets/input/fittech_2025

cp -r urban_brew_2025/brand assets/brand/
cp -r urban_brew_2025/input/* assets/input/urban_brew_2025/
mkdir -p assets/input/urban_brew_2025

cp fittech_2025_brief.json ../
cp urban_brew_2025_brief.json ../
```

### 2. Run Campaigns

```bash
# Campaign 1: FitTech
python run_prism.py --campaign fittech_2025_brief.json

# Campaign 2: Urban Brew
python run_prism.py --campaign urban_brew_2025_brief.json
```

### 3. Expected Output

Each campaign generates:
- 2 products × 3 aspect ratios × 2 locales = **12 assets**
- Output location: `output/{campaign_id}/{product_id}/`
- Execution log: `logs/{campaign_id}_execution.json`

**FitTech Output:**
```
output/fittech_2025/
├── pulse_smartwatch/
│   ├── 1x1_en.png, 1x1_es.png
│   ├── 9x16_en.png, 9x16_es.png
│   └── 16x9_en.png, 16x9_es.png
└── airflow_earbuds/
    └── (same structure)
```

**Urban Brew Output:**
```
output/urban_brew_2025/
├── cold_brew_original/
│   ├── 1x1_en.png, 1x1_fr.png
│   ├── 9x16_en.png, 9x16_fr.png
│   └── 16x9_en.png, 16x9_fr.png
└── energize_plus/
    └── (same structure)
```

## Quick Setup Script

Use the included `setup.sh` script:

```bash
chmod +x setup.sh
./setup.sh
```

This will:
1. Create necessary directories
2. Copy all assets to correct locations
3. Move campaign briefs to project root
4. Verify setup

## Testing Scenarios

### Test 1: Full Generation (No Cache)
```bash
python run_prism.py --campaign fittech_2025_brief.json --clear-cache
```
Expected: All 12 assets generated fresh (~45 seconds)

### Test 2: Cache Verification
```bash
python run_prism.py --campaign fittech_2025_brief.json --verify-cache
```
Expected: Run 1 generates, Run 2 uses cache (100% hit rate)

### Test 3: Input Asset Usage
Assets in `assets/input/{campaign_id}/` are automatically used instead of generation.

### Test 4: Campaign-Specific Branding
Each campaign uses its own logo from `assets/brand/{campaign_id}/logo.png`.

### Test 5: LLM Pre-Flight Validation
Validation runs automatically. Check logs for validation results.

## Validation Checklist

✅ Campaign briefs are valid JSON  
✅ Product IDs match input asset filenames  
✅ Brand logos exist for both campaigns  
✅ Input assets are in correct directories  
✅ Config.yaml has required settings  
✅ OPENAI_API_KEY is set in .env  

## Costs

**Per Campaign:**
- LLM validation: $0.0015
- Image generation: 12 assets × $0.08 = $0.96 (if not cached)
- With input assets: $0.0015 (validation only)

**Total for both campaigns:**
- With generation: ~$1.92
- With input assets: ~$0.003

## Troubleshooting

**Issue:** Assets not found  
**Fix:** Ensure directory structure matches:
```
assets/
├── brand/
│   ├── fittech_2025/logo.png
│   └── urban_brew_2025/logo.png
└── input/
    ├── fittech_2025/
    │   ├── pulse_smartwatch.png
    │   └── airflow_earbuds.png
    └── urban_brew_2025/
        ├── cold_brew_original.png
        └── energize_plus.png
```

**Issue:** Validation fails  
**Fix:** Check `logs/{campaign_id}_execution.json` for detailed errors

**Issue:** Wrong logo appears  
**Fix:** Verify campaign_id in brief matches brand folder name

