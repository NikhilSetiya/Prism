#!/usr/bin/env python3
"""Validate Prism installation and configuration."""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def check_file(path: str, description: str) -> bool:
    """Check if file exists."""
    if Path(path).exists():
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description} MISSING: {path}")
        return False


def check_import(module: str) -> bool:
    """Check if module can be imported."""
    try:
        __import__(module)
        print(f"✅ Module: {module}")
        return True
    except ImportError as e:
        print(f"❌ Module MISSING: {module} - {e}")
        return False


def check_env_var(var: str) -> bool:
    """Check if environment variable is set."""
    value = os.getenv(var)
    if value and value.strip():
        print(f"✅ Environment: {var} (set)")
        return True
    else:
        print(f"⚠️  Environment: {var} (not set - required for GenAI)")
        return False


def main():
    """Run validation checks."""
    print("="*60)
    print("PRISM ENTERPRISE MVP - SETUP VALIDATION")
    print("="*60)
    
    all_ok = True
    
    # Core files
    print("\n📁 Core Files:")
    all_ok &= check_file("src/pipeline.py", "Pipeline")
    all_ok &= check_file("src/governance.py", "Governance")
    all_ok &= check_file("src/models.py", "Models")
    all_ok &= check_file("src/utils.py", "Utils")
    all_ok &= check_file("config.yaml", "Config")
    
    # Entry points
    print("\n🚀 Entry Points:")
    all_ok &= check_file("run_prism.py", "CLI Runner")
    all_ok &= check_file("create_campaign.py", "Campaign Builder")
    all_ok &= check_file("app.py", "Streamlit UI")
    

    
    # Dependencies
    print("\n📦 Python Dependencies:")
    deps_ok = True
    deps_ok &= check_import("openai")
    deps_ok &= check_import("PIL")
    deps_ok &= check_import("pydantic")
    deps_ok &= check_import("yaml")
    deps_ok &= check_import("dotenv")
    deps_ok &= check_import("numpy")
    
    if not deps_ok:
        print("\n   Run: pip install -r requirements.txt")
        all_ok = False
    
    # Environment
    print("\n🔑 Environment:")
    env_ok = check_env_var("OPENAI_API_KEY")
    
    # Directories
    print("\n📂 Directories:")
    dirs = ["cache", "output", "logs", "assets/input", "assets/brand"]
    for d in dirs:
        if Path(d).exists():
            print(f"✅ {d}")
        else:
            print(f"⚠️  {d} (will be created on first run)")
    
    # Summary
    print("\n" + "="*60)
    if all_ok and deps_ok and env_ok:
        print("✅ ALL CHECKS PASSED - READY TO RUN")
        print("\nNext steps:")
        print("  1. Create campaign: python create_campaign.py")
        print("  2. Run campaign: python run_prism.py --campaign brief.json")
        print("  3. Or use UI: streamlit run app.py")
        return 0
    else:
        print("⚠️  SETUP INCOMPLETE")
        if not deps_ok:
            print("\n  Missing dependencies: pip install -r requirements.txt")
        if not env_ok:
            print("\n  Missing API key: Set OPENAI_API_KEY in .env file")
        return 1


if __name__ == "__main__":
    sys.exit(main())

