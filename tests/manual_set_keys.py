#!/usr/bin/env python
"""
manual_set_keys.py - Manually set API keys for testing

This script allows you to manually enter API keys that will be set
in the environment variables for the current process only.
"""

import os
import sys
from pathlib import Path
from getpass import getpass

def manual_set_keys():
    """Manually set API keys for testing"""
    print("This will set API keys for the current process only.")
    print("These values won't be saved to a file.\n")
    
    # Get Google API key
    google_key = getpass("Enter your Google API key (hidden): ")
    if google_key:
        os.environ['GOOGLE_API_KEY'] = google_key
        print("Set GOOGLE_API_KEY environment variable")
    else:
        print("No Google API key provided")
    
    # Get OpenAI API key
    openai_key = getpass("Enter your OpenAI API key (hidden): ")
    if openai_key:
        os.environ['OPENAI_API_KEY'] = openai_key
        print("Set OPENAI_API_KEY environment variable")
    else:
        print("No OpenAI API key provided")
    
    # Set default model
    default_model = input("Enter default model name [gemini-1.5-pro]: ")
    if not default_model:
        default_model = 'gemini-1.5-pro'
    os.environ['DEFAULT_MODEL'] = default_model
    print(f"Set DEFAULT_MODEL to {default_model}")
    
    print("\nAPI keys are set in the environment.")
    print("Now you can run the tests with:")
    print("python -c \"import os; from tests.manual_set_keys import manual_set_keys; manual_set_keys(); import unittest; unittest.main(module='tests.test_google_ai')\"")

if __name__ == "__main__":
    print("Manual API Key Setting Tool")
    print("==========================")
    manual_set_keys()
    
    # Offer to run tests right away
    if input("\nRun tests right away? (y/N): ").lower() == 'y':
        import unittest
        print("\nRunning tests...")
        unittest.main(module='tests.test_google_ai') 