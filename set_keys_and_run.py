#!/usr/bin/env python
"""
set_keys_and_run.py - Set API keys and run tests

This script sets API keys directly from command line arguments
or prompts for them if not provided, then runs the tests.
"""

import os
import sys
import argparse
from pathlib import Path

def main():
    """Set API keys and run tests"""
    parser = argparse.ArgumentParser(description="Set API keys and run tests")
    parser.add_argument("--google-key", help="Google API key")
    parser.add_argument("--openai-key", help="OpenAI API key (not used in this version, but kept for backward compatibility)")
    parser.add_argument("--model", default="gemini-2.0-flash", help="Model name (default: gemini-2.0-flash)")
    args = parser.parse_args()
    
    print("This version uses only Google Gemini models.\n")
    
    # Get Google API key - required
    google_key = args.google_key
    if not google_key:
        google_key = input("Enter your Google API key (required): ")
    
    if google_key:
        os.environ['GOOGLE_API_KEY'] = google_key
        print(f"✓ Set GOOGLE_API_KEY (starts with: {google_key[:4]}...)")
    else:
        print("❌ No Google API key provided. Tests will fail.")
        return 1
    
    # OpenAI key is now optional with a clear message
    openai_key = args.openai_key
    if not openai_key and "--openai-key" in sys.argv:
        print("Note: OpenAI API key parameter is accepted for backward compatibility,")
        print("      but this version uses only Google Gemini models.")
        openai_key = input("Enter your OpenAI API key (optional, not used): ")
    
    if openai_key:
        # We'll still set it in the environment in case any legacy code needs it
        os.environ['OPENAI_API_KEY'] = openai_key
        print(f"✓ Set OPENAI_API_KEY (not used in this version)")
    else:
        # Make sure it's not set in the environment to avoid confusing providers
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        print("ℹ️ No OpenAI API key provided (not required for this version).")
    
    # Set model - force to Gemini if something else is specified
    if not args.model.startswith("gemini-"):
        print(f"⚠️ Model '{args.model}' is not a Gemini model. Forcing to gemini-2.0-flash.")
        os.environ['DEFAULT_MODEL'] = "gemini-2.0-flash"
    else:
        os.environ['DEFAULT_MODEL'] = args.model
    
    print(f"✓ Using model: {os.environ['DEFAULT_MODEL']}")
    
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Run tests
    print("\nRunning Google AI integration tests...")
    from tests.test_google_ai import run_tests
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Tests failed or were skipped.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 