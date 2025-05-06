#!/usr/bin/env python
"""
check_api_keys.py - Diagnostic tool for API keys

Verifies API keys are properly configured in the environment
and shows their masked values for confirmation.
"""

import os
import sys
from pathlib import Path

def mask_key(key):
    """Mask a key for display"""
    if not key:
        return "None"
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]

def check_api_keys():
    """Check API keys in environment"""
    # Determine project root
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    
    # Check for .env file
    env_path = project_root / '.env'
    print(f".env file exists: {env_path.exists()}")
    
    if env_path.exists():
        print(f".env file permissions: {oct(env_path.stat().st_mode)[-3:]}")
        print(f".env file size: {env_path.stat().st_size} bytes")
        
        # Try to read .env file directly
        try:
            with open(env_path, 'r') as f:
                env_contents = f.read()
                print("\n.env file contents (with keys masked):")
                for line in env_contents.splitlines():
                    if "API_KEY" in line and "=" in line:
                        key, value = line.split("=", 1)
                        print(f"{key}={mask_key(value)}")
                    else:
                        print(line)
        except Exception as e:
            print(f"Error reading .env file: {e}")
    
    # Try to load using dotenv
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        print("\nLoaded .env file with python-dotenv")
    except ImportError:
        print("\nWarning: python-dotenv not installed")
    
    # Check environment variables
    print("\nEnvironment variables:")
    google_key = os.environ.get('GOOGLE_API_KEY')
    openai_key = os.environ.get('OPENAI_API_KEY')
    default_model = os.environ.get('DEFAULT_MODEL')
    
    print(f"GOOGLE_API_KEY: {mask_key(google_key)}")
    print(f"OPENAI_API_KEY: {mask_key(openai_key)}")
    print(f"DEFAULT_MODEL: {default_model}")
    
    # Set them manually for testing if needed
    if not google_key or google_key == 'your_google_api_key_here':
        print("\nGOOGLE_API_KEY is not set or is using placeholder value.")
        print("To set it manually for this session:")
        print("os.environ['GOOGLE_API_KEY'] = 'your_actual_key'")
    
    if not openai_key or openai_key == 'your_openai_api_key_here':
        print("\nOPENAI_API_KEY is not set or is using placeholder value.")
        print("To set it manually for this session:")
        print("os.environ['OPENAI_API_KEY'] = 'your_actual_key'")
    
    # Check for system environment variables
    print("\nChecking system environment variables (outside of process):")
    import subprocess
    try:
        google_sys_env = subprocess.check_output('echo %GOOGLE_API_KEY%', shell=True).decode().strip()
        openai_sys_env = subprocess.check_output('echo %OPENAI_API_KEY%', shell=True).decode().strip()
        
        if google_sys_env and google_sys_env != '%GOOGLE_API_KEY%':
            print(f"System GOOGLE_API_KEY: {mask_key(google_sys_env)}")
        else:
            print("System GOOGLE_API_KEY not set")
            
        if openai_sys_env and openai_sys_env != '%OPENAI_API_KEY%':
            print(f"System OPENAI_API_KEY: {mask_key(openai_sys_env)}")
        else:
            print("System OPENAI_API_KEY not set")
    except Exception as e:
        print(f"Error checking system environment: {e}")

if __name__ == "__main__":
    print("API Key Diagnostic Tool")
    print("======================")
    check_api_keys() 