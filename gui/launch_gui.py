#!/usr/bin/env python3
"""
Roblox Trade Command Engine - GUI Client Launcher
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import main
    print("Starting Roblox Trade Command Engine GUI...")
    main()
except ImportError as e:
    print(f"Error: {e}")
    print("Please install required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error starting GUI: {e}")
    sys.exit(1) 