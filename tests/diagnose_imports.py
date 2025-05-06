#!/usr/bin/env python
"""
diagnose_imports.py - A tool to diagnose import issues with the AI agent

This script checks if the necessary modules are importable and helps
identify issues with the project structure or dependencies.
"""

import os
import sys
from pathlib import Path
import importlib.util

def check_module(module_name, package_name=None):
    """Check if a module can be imported"""
    try:
        if package_name:
            importlib.import_module(module_name, package=package_name)
        else:
            importlib.import_module(module_name)
        return True
    except ImportError as e:
        return str(e)

def main():
    """Run diagnostics on the project structure and imports"""
    print("=== AI Agent Import Diagnostics ===\n")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"sys.path: {sys.path}")
    
    # Current project structure
    project_root = Path(__file__).parent.parent
    print(f"\nProject root: {project_root}")
    
    # Check if ai_agent directory exists
    ai_agent_path = project_root / "ai_agent"
    print(f"\nChecking ai_agent directory: {ai_agent_path}")
    if not ai_agent_path.exists():
        print(f"ERROR: ai_agent directory not found at {ai_agent_path}")
    else:
        print(f"✓ ai_agent directory exists")
        # List contents
        print("\nContents of ai_agent directory:")
        for item in ai_agent_path.iterdir():
            print(f"  {item.name}")
    
    # Check if ai_shell_agent module exists
    ai_shell_agent_path = ai_agent_path / "ai_shell_agent"
    print(f"\nChecking ai_shell_agent module: {ai_shell_agent_path}")
    if not ai_shell_agent_path.exists():
        print(f"ERROR: ai_shell_agent module not found at {ai_shell_agent_path}")
    else:
        print(f"✓ ai_shell_agent module exists")
        # List contents
        print("\nContents of ai_shell_agent module:")
        for item in ai_shell_agent_path.iterdir():
            if item.is_file() and item.suffix == '.py':
                print(f"  {item.name}")
    
    # Add ai_agent to path
    if ai_agent_path.exists():
        sys.path.insert(0, str(ai_agent_path))
    
    # Check external dependencies
    print("\nChecking external dependencies:")
    dependencies = [
        "dotenv",
        "langchain_core",
        "langchain_google_genai",
        "langchain_openai",
        "google.generativeai"
    ]
    
    for dep in dependencies:
        result = check_module(dep)
        if result is True:
            print(f"✓ {dep}: Successfully imported")
        else:
            print(f"✗ {dep}: Import failed - {result}")
    
    # Check ai_shell_agent
    print("\nAttempting to import ai_shell_agent.llm:")
    try:
        # Try to import the target module
        from ai_shell_agent.llm import get_llm_plain
        print("✓ Successfully imported ai_shell_agent.llm.get_llm_plain")
    except ImportError as e:
        print(f"✗ Failed to import ai_shell_agent.llm: {e}")
        
        # Try to import the parent module
        try:
            import ai_shell_agent
            print(f"  But ai_shell_agent module itself can be imported")
            print(f"  ai_shell_agent.__file__: {ai_shell_agent.__file__}")
        except ImportError as e2:
            print(f"  ai_shell_agent module also cannot be imported: {e2}")

if __name__ == "__main__":
    main() 