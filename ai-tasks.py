#!/usr/bin/env python
"""
ai-tasks.py - Entry point for AI-Driven Productivity Shell Tool

This script launches the AI-Driven Productivity Shell Tool from the project root.
It can be run directly from the command line.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main function from the CLI module
try:
    from cli.agent import main
    main()
except ImportError as e:
    print(f"Error: Could not import the agent module: {e}")
    print("Make sure you have installed the package with 'pip install -e .'")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nOperation cancelled by user. Exiting...")
    sys.exit(0)
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 