# Prism Setup Guide

Complete step-by-step instructions to run Prism locally.

---

## 1. Prerequisites

- **Python 3.9+** installed
- **OpenAI API Key** (get from: https://platform.openai.com/api-keys)
- **Terminal/Command Line** access

---

## 2. Initial Setup

### Step 1: Clone/Navigate to Project

```bash
cd /Users/nikhilsetiya/Desktop/Nikhil/Projects/Prism
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Expected packages:
- openai (API client)
- Pillow (image processing)
- pydantic (validation)
- PyYAML (config)
- streamlit (UI)
- numpy (post-processing)
- pandas (reporting)

---

## 3. Environment Configuration

### Step 1: Create .env File

```bash
cp .env.example .env
```

### Step 2: Add Your OpenAI API Key

Edit `.env` file:

```bash
# Option A: Using nano
nano .env

# Option B: Using vim
vim .env

# Option C: Using VS Code
code .env
```

Replace `your_openai_api_key_here` with your actual key:

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Save and close the file.**

### Step 3: Verify Setup

```bash
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✓ API Key loaded' if os.getenv('OPENAI_API_KEY') else '✗ API Key missing')"
```

Expected output: `✓ API Key loaded`

---

## 4. Test Campaigns Setup (Optional but Recommended)

### Quick Setup

```bash
cd test_campaigns_package
./setup.sh
cd ..
```

This will:
- Copy brand logos to `assets/brand/`
- Copy product images to `assets/input/`
- Move campaign briefs to project root
- Verify all files in place

### Manual Setup (Alternative)

```bash
# Create directories
mkdir -p assets/brand/fittech_2025
mkdir -p assets/brand/urban_brew_2025
mkdir -p assets/input/fittech_2025
mkdir -p assets/input/urban_brew_2025

# Copy brand assets
cp test_campaigns_package/fittech_2025/brand/logo.png assets/brand/fittech_2025/
cp test_campaigns_package/urban_brew_2025/brand/logo.png assets/brand/urban_brew_2025/

# Copy input assets
cp test_campaigns_package/fittech_2025/input/*.png assets/input/fittech_2025/
cp test_campaigns_package/urban_brew_2025/input/*.png assets/input/urban_brew_2025/

# Copy campaign briefs
cp test_campaigns_package/fittech_2025_brief.json .
cp test_campaigns_package/urban_brew_2025_brief.json .
```

---

## 5. Running Prism

### Option A: CLI (Command Line Interface)

#### Test Campaign 1: FitTech 2025

```bash
python run_prism.py --campaign fittech_2025_brief.json
```

**Output:**
- Location: `output/fittech_2025/`
- Assets: 12 files (2 products × 3 ratios × 2 locales)
- Time: ~5 seconds (with input assets)
- Cost: ~$0.003 (validation only)

#### Test Campaign 2: Urban Brew 2025

```bash
python run_prism.py --campaign urban_brew_2025_brief.json
```

**Output:**
- Location: `output/urban_brew_2025/`
- Assets: 12 files
- Time: ~5 seconds
- Cost: ~$0.003

#### Create Custom Campaign

```bash
python create_campaign.py
```

Follow the interactive wizard to create your own campaign brief.

#### CLI Options

```bash
# Clear cache before running
python run_prism.py --campaign your_brief.json --clear-cache

# Verify cache status
python run_prism.py --campaign your_brief.json --verify-cache

# Help
python run_prism.py --help
```

---

### Option B: Streamlit Web UI

#### Step 1: Clear Any Running Streamlit Instances

```bash
# Kill existing Streamlit processes
lsof -ti:8501 | xargs kill -9

# Or on Windows
# netstat -ano | findstr :8501
# taskkill /PID <PID> /F
```

#### Step 2: Start Streamlit

```bash
streamlit run app.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

#### Step 3: Open Browser

- **Automatic:** Browser should open automatically
- **Manual:** Go to http://localhost:8501

#### Step 4: Use Web UI

1. **Upload campaign brief** (JSON file) or use example
2. **Review validation** results
3. **Click "Run Campaign"**
4. **Monitor progress** in real-time
5. **Download assets** when complete
6. **View execution report** with timing and costs

#### Stop Streamlit

Press `Ctrl+C` in the terminal where Streamlit is running.

---

## 6. Verify Output

### Check Generated Assets

```bash
# List all outputs
ls -R output/

# Check specific campaign
ls -lh output/fittech_2025/pulse_smartwatch/
```

Expected files per product:
```
1x1_en.png      # Square format, English
1x1_es.png      # Square format, Spanish
9x16_en.png     # Vertical format, English
9x16_es.png     # Vertical format, Spanish
16x9_en.png     # Horizontal format, English
16x9_es.png     # Horizontal format, Spanish
```

### Check Execution Logs

```bash
# View latest log
ls -lt logs/ | head -5

# Read specific campaign log
cat logs/fittech_2025_execution.json
```

### Check Cache

```bash
# View cached assets
ls -lh cache/
```

---

## 7. Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "API Key not found"

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify content
cat .env

# Ensure OPENAI_API_KEY is set
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY', 'MISSING'))"
```

### Issue: "Permission denied: ./setup.sh"

**Solution:**
```bash
chmod +x test_campaigns_package/setup.sh
```

### Issue: Streamlit won't start on port 8501

**Solution:**
```bash
# Kill process on port 8501
lsof -ti:8501 | xargs kill -9

# Or run on different port
streamlit run app.py --server.port 8502
```

### Issue: Assets not found

**Solution:**
```bash
# Verify directory structure
ls -R assets/

# Re-run setup
cd test_campaigns_package && ./setup.sh && cd ..
```

### Issue: "Rate limit exceeded"

**Solution:**
- Wait 1 minute and retry
- Check your OpenAI API usage limits
- Reduce `max_workers` in `config.yaml`

### Issue: Generated images look bad

**Solution:**
- Ensure `quality: "hd"` in `config.yaml`
- Check `post_processing.enabled: true`
- Verify prompt_builder is using production photography specs

---

## 8. Configuration (Advanced)

Edit `config.yaml` for custom settings:

```yaml
campaign:
  quality: "hd"              # "standard" or "hd"
  
governance:
  llm_validation_enabled: true
  validation_blocking: true   # Block if validation fails
  
post_processing:
  enabled: true
  intensity: 0.3             # 0.0-1.0

scalability:
  max_workers: 3             # Parallel processing
  rate_limit: 45             # Requests per minute
```

---

## 9. Quick Reference Commands

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env
# Add OPENAI_API_KEY to .env

# Test campaigns setup
cd test_campaigns_package && ./setup.sh && cd ..

# Run CLI
python run_prism.py --campaign fittech_2025_brief.json

# Run Streamlit
streamlit run app.py

# Clear Streamlit port
lsof -ti:8501 | xargs kill -9

# Check outputs
ls -R output/

# View logs
cat logs/fittech_2025_execution.json

# Clear cache
rm -rf cache/*.png
```

---

## 10. Expected Costs

| Operation | Cost | Time |
|-----------|------|------|
| LLM Validation | $0.0015 | <1s |
| Image Generation (HD) | $0.08/image | 5-10s |
| Cache Hit | $0 | <1s |
| Full Campaign (12 assets, no cache) | ~$0.96 | 45-60s |
| Full Campaign (with input assets) | ~$0.003 | 2-5s |

---

**You're ready to run Prism!** 🚀

For questions or issues, check:
- `README.md` - Architecture and design decisions
- `logs/` - Detailed execution logs
- GitHub Issues - Report bugs or request features


