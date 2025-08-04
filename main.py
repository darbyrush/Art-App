#!/usr/bin/env python3
"""
Art Explorer - Main Entry Point
Launch the refactored Streamlit application
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main application
from app.main import *

# This file serves as the entry point for the refactored application
# The actual Streamlit app logic is in app/main.py 