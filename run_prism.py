#!/usr/bin/env python3
"""Simple runner script for Prism pipeline."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run main
from src.__main__ import main

if __name__ == "__main__":
    sys.exit(main())

