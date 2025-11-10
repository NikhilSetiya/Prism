#!/bin/bash

# Prism Test Campaigns Setup Script
# Automatically sets up both test campaigns

set -e  # Exit on error

echo "🚀 Prism Test Campaigns Setup"
echo "=============================="
echo ""

# Check if we're in the right directory
if [ ! -f "fittech_2025_brief.json" ]; then
    echo "❌ Error: Must run from test_campaigns_package directory"
    exit 1
fi

# Navigate to parent Prism directory
cd ..

echo "📁 Creating directory structure..."

# Create brand directories
mkdir -p assets/brand/fittech_2025
mkdir -p assets/brand/urban_brew_2025

# Create input directories  
mkdir -p assets/input/fittech_2025
mkdir -p assets/input/urban_brew_2025

echo "✓ Directories created"
echo ""

echo "📦 Copying brand assets..."

# Copy brand logos
cp test_campaigns_package/fittech_2025/brand/logo.png assets/brand/fittech_2025/
cp test_campaigns_package/urban_brew_2025/brand/logo.png assets/brand/urban_brew_2025/

echo "✓ Brand logos copied"
echo ""

echo "📦 Copying input assets..."

# Copy input assets
cp test_campaigns_package/fittech_2025/input/*.png assets/input/fittech_2025/
cp test_campaigns_package/urban_brew_2025/input/*.png assets/input/urban_brew_2025/

echo "✓ Input assets copied"
echo ""

echo "📄 Copying campaign briefs..."

# Copy campaign briefs to project root
cp test_campaigns_package/fittech_2025_brief.json .
cp test_campaigns_package/urban_brew_2025_brief.json .

echo "✓ Campaign briefs copied"
echo ""

echo "🔍 Verifying setup..."

# Verify files exist
ERRORS=0

check_file() {
    if [ ! -f "$1" ]; then
        echo "  ❌ Missing: $1"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✓ $1"
    fi
}

echo ""
echo "Brand Assets:"
check_file "assets/brand/fittech_2025/logo.png"
check_file "assets/brand/urban_brew_2025/logo.png"

echo ""
echo "Input Assets:"
check_file "assets/input/fittech_2025/pulse_smartwatch.png"
check_file "assets/input/fittech_2025/airflow_earbuds.png"
check_file "assets/input/urban_brew_2025/cold_brew_original.png"
check_file "assets/input/urban_brew_2025/energize_plus.png"

echo ""
echo "Campaign Briefs:"
check_file "fittech_2025_brief.json"
check_file "urban_brew_2025_brief.json"

echo ""
echo "=============================="

if [ $ERRORS -eq 0 ]; then
    echo "✅ Setup Complete! All files in place."
    echo ""
    echo "Next steps:"
    echo "  1. Ensure OPENAI_API_KEY is set in .env"
    echo "  2. Run: python run_prism.py --campaign fittech_2025_brief.json"
    echo "  3. Run: python run_prism.py --campaign urban_brew_2025_brief.json"
    echo ""
    echo "Expected cost: ~$1.92 total (or $0.003 if using input assets only)"
else
    echo "⚠️  Setup completed with $ERRORS error(s). Check missing files above."
    exit 1
fi

