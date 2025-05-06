#!/usr/bin/env python
"""
run_with_keys.py - Set API keys and run tests in one step

This script sets the API keys in the environment and then
runs the Google AI integration tests all in one step.
"""

import os
import sys
import unittest
from pathlib import Path
from getpass import getpass

def main():
    """Set API keys and run tests"""
    print("Setting API keys and running tests")
    print("=================================")
    print("This version uses only Google Gemini models.")
    
    # Set API keys - Google is required
    google_key = getpass("Enter your Google API key (required, hidden): ")
    if google_key:
        os.environ['GOOGLE_API_KEY'] = google_key
        print("✓ Set GOOGLE_API_KEY")
    else:
        print("❌ No Google API key provided. Tests will fail.")
        return 1
    
    # Make OpenAI key optional with clear messaging
    print("\nNote: This version uses only Google models. OpenAI key is not required.")
    openai_response = input("Do you want to provide an OpenAI API key anyway? (y/N): ").lower()
    
    if openai_response.startswith('y'):
        openai_key = getpass("Enter your OpenAI API key (optional, hidden): ")
        if openai_key:
            # Store it but with a message that it won't be used
            os.environ['OPENAI_API_KEY'] = openai_key
            print("✓ Set OPENAI_API_KEY (not used in this version)")
        else:
            print("ℹ️ No OpenAI API key provided.")
    else:
        # Make sure it's not set in the environment to avoid confusing providers
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        print("ℹ️ Skipped OpenAI API key (not required for this version).")
    
    # Set model name - only Gemini models allowed
    model_name = 'gemini-2.0-flash'
    os.environ['DEFAULT_MODEL'] = model_name
    print(f"✓ Using model: {model_name}")
    
    # Add project root to path to ensure imports work
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