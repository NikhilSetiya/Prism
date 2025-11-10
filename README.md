# Prism

Generate localized marketing assets across products, formats, and languages. One brief → campaign.

## Quick Start

```bash
pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-..." > .env

# Run demo campaign
cd test_campaigns_package && ./setup.sh && cd ..
python run_prism.py --campaign fittech_2025_brief.json

# Or use UI
streamlit run app.py
```

**Output:** 2 products × 3 ratios × 2 locales = 12 assets in ~30s ($0.32)

## Features

- **Multi-format generation:** 9:16, 16:9, 1:1 (native composition, not crops)
- **Automated governance:** Brand/legal/quality checks, compliance tracking
- **Production quality:** Film-like post-processing, professional photography prompts
- **Cache-first:** 33% cost reduction via intelligent asset reuse
- **Parallel processing:** Configurable worker pools, rate limiting
- **Dual interface:** CLI + Streamlit UI

## Architecture

```
Brief → Governance → Asset Manager → Generator → Compositor → Post-Process → Output
         (validate)   (cache/input)    (DALL-E)   (text+logo)  (film effects)
```

**Pipeline:** Configurable workers, rate limiting, parallel execution  
**Storage:** Local (prod-ready for S3/Azure Blob)

## Configuration

Edit `config.yaml`:

```yaml
campaign:
  quality: "hd"              # standard ($0.04) or hd ($0.08)
governance:
  validation_blocking: true   # Block on compliance failures
post_processing:
  enabled: true
  intensity: 0.3             # Film grain effect (0.0-1.0)
scalability:
  max_workers: 3
  rate_limit: 45             # req/min for DALL-E
```

## Example Brief

```json
{
  "campaign_id": "summer_2025",
  "campaign_message": "Discover Summer Freshness",
  "locales": ["en", "fr"],
  "products": [{
    "id": "shampoo_citrus",
    "name": "Citrus Fresh Shampoo",
    "category": "personal_care",
    "creative_brief": {
      "setting": "bright modern bathroom",
      "mood": "energetic and fresh"
    }
  }]
}
```

See `test_campaigns_package/` for complete examples.

## Cost

**Typical campaign:** 2 products × 3 ratios × 2 locales = 12 assets

- Validation: $0.002
- Images (6 unique): $0.48
- Cache savings (33%): -$0.16
- **Total: $0.32** (~30s)

## Troubleshooting

```bash
# Clear cache
python run_prism.py --clear-cache

# Verify setup
python validate_setup.py

# Check logs
cat logs/{campaign_id}_execution.json
```

## License

MIT
