#!/usr/bin/env python
"""
set_api_keys.py - Simple utility to set API keys for testing

This script helps set up API keys for Google and OpenAI
when running the tests. It creates or updates the .env file.
"""

import os
import sys
from pathlib import Path
from getpass import getpass

def setup_api_keys():
    """Set up API keys for testing"""
    project_root = Path(__file__).parent.parent
    env_path = project_root / '.env'
    
    try:
        # Try to import dotenv
        from dotenv import load_dotenv, set_key
        env_exists = env_path.exists()
        
        if env_exists:
            load_dotenv(env_path)
            print(f"Loaded existing .env file from {env_path}")
        else:
            print(f"Will create new .env file at {env_path}")
            
        # Get API keys
        google_key = os.getenv('GOOGLE_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if not google_key or google_key == 'your_google_api_key_here':
            google_key = getpass('Enter your Google API key (hidden): ')
            if google_key:
                os.environ['GOOGLE_API_KEY'] = google_key
                set_key(env_path, 'GOOGLE_API_KEY', google_key)
                print("✓ Google API key set")
        else:
            print("✓ Google API key already set")
            
        if not openai_key or openai_key == 'your_openai_api_key_here':
            openai_key = getpass('Enter your OpenAI API key (hidden): ')
            if openai_key:
                os.environ['OPENAI_API_KEY'] = openai_key
                set_key(env_path, 'OPENAI_API_KEY', openai_key)
                print("✓ OpenAI API key set")
        else:
            print("✓ OpenAI API key already set")
            
        # Set default model
        if not os.getenv('DEFAULT_MODEL'):
            os.environ['DEFAULT_MODEL'] = 'gemini-1.5-pro'
            set_key(env_path, 'DEFAULT_MODEL', 'gemini-1.5-pro')
            print("✓ DEFAULT_MODEL set to gemini-1.5-pro")
            
        print("\nAPI keys are set and ready for testing.")
        print(f"Environment file saved at: {env_path}")
        return True
        
    except ImportError:
        print("Error: python-dotenv not installed. Please install it with:")
        print("pip install python-dotenv")
        return False
    except Exception as e:
        print(f"Error setting up API keys: {e}")
        return False

if __name__ == "__main__":
    print("API Key Setup Utility for Tests")
    print("===============================")
    setup_api_keys() 