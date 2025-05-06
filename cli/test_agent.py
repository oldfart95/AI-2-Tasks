#!/usr/bin/env python
"""
test_agent.py - Test script for AI-Driven Productivity Shell Tool

Tests the basic functionality of the task parser and command synthesizer
without requiring a full agent instance.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task_parser import TaskParser, get_example_tasks
from command_synthesizer import CommandSynthesizer

def test_rule_based_parsing():
    """Test the rule-based parsing fallback"""
    print("\n=== Testing Rule-Based Parsing ===")
    
    # Create parser with None LLM to force rule-based parsing
    parser = TaskParser(None)
    
    for example in get_example_tasks():
        print(f"\nInput: {example}")
        tasks = parser.parse_tasks_simple(example)
        
        if tasks:
            print(f"Parsed {len(tasks)} tasks:")
            for i, (verb, obj) in enumerate(tasks, 1):
                print(f"{i}. {verb} {obj}")
        else:
            print("No tasks parsed")


def test_full_integration(llm=None):
    """
    Test the full integration between task parser and command synthesizer.
    
    Args:
        llm: Optional LLM instance to use
    """
    if not llm:
        # Try to import and get LLM
        try:
            # First try to import from the actual module
            from ai_agent.ai_shell_agent.llm import get_llm_plain
            llm = get_llm_plain()
        except ImportError:
            try:
                # Fall back to the mock implementation
                print("Using mock LLM implementation for testing")
                from mock_llm import get_llm_plain
                llm = get_llm_plain()
            except Exception as e:
                print(f"Could not initialize mock LLM: {e}")
                print("Testing rule-based parsing only")
                test_rule_based_parsing()
                return
        except Exception as e:
            print(f"Could not initialize LLM: {e}")
            print("Testing rule-based parsing only")
            test_rule_based_parsing()
            return
    
    if not llm:
        print("LLM initialization failed, testing rule-based parsing only")
        test_rule_based_parsing()
        return
    
    print("\n=== Testing Full Integration ===")
    
    # Initialize parser and synthesizer
    parser = TaskParser(llm)
    synthesizer = CommandSynthesizer(llm)
    
    # Test with natural language inputs
    test_inputs = [
        "List all files in the current directory",
        "Find all Python files modified in the last week",
        "Check system information and show available disk space"
    ]
    
    for text_input in test_inputs:
        print(f"\nInput: {text_input}")
        
        # Parse tasks
        tasks = parser.parse_tasks(text_input)
        
        if not tasks:
            print("LLM parsing failed, falling back to rule-based parsing")
            tasks = parser.parse_tasks_simple(text_input)
        
        if tasks:
            print(f"Parsed {len(tasks)} tasks:")
            for i, (verb, obj) in enumerate(tasks, 1):
                print(f"{i}. {verb} {obj}")
                
                # Synthesize command for each task
                print(f"\nSynthesizing command for: {verb} {obj}")
                result = synthesizer.synthesize_command((verb, obj))
                
                if result['command']:
                    print(f"Command: {result['command']}")
                    print(f"Explanation: {result['explanation']}")
                else:
                    print("Command synthesis failed")
        else:
            print("No tasks parsed")


if __name__ == "__main__":
    # If running directly, test the full integration
    test_full_integration() 