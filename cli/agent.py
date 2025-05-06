#!/usr/bin/env python
"""
agent.py - Main CLI wrapper that combines task parsing and command synthesis

This module provides a unified CLI interface for accepting natural language inputs,
breaking them into tasks, and executing those tasks as shell commands.
"""

import os
import sys
import subprocess
import argparse
import traceback
from typing import List, Tuple, Dict, Optional, Any
from pathlib import Path

# Platform-specific readline support
try:
    # Unix systems
    import readline
except ImportError:
    try:
        # Windows - try to use pyreadline3 if available
        import pyreadline3 as readline
    except ImportError:
        # Define a dummy readline module for Windows if no alternative is available
        class DummyReadline:
            def read_history_file(self, *args, **kwargs):
                pass
                
            def write_history_file(self, *args, **kwargs):
                pass
                
            def set_history_length(self, *args, **kwargs):
                pass
                
        readline = DummyReadline()
        print("Warning: readline functionality not available. Command history will not be saved.")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Ensure the current directory is also in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    # Try to load from project root first, then from current directory
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(os.path.join(root_dir, '.env')):
        load_dotenv(os.path.join(root_dir, '.env'))
    elif os.path.exists('.env'):
        load_dotenv()
except ImportError:
    print("Warning: python-dotenv package not installed. Environment variables must be set manually.")

# Import modules
try:
    # First try to import local modules
    from task_parser import TaskParser, get_example_tasks
    from command_synthesizer import CommandSynthesizer
    
    # For real LLM integration, try to import from ai-shell-agent
    # This is wrapped in a separate try/except to handle its absence gracefully
    try:
        from ai_agent.ai_shell_agent.llm import get_llm_plain
        HAS_AI_AGENT = True
    except ImportError:
        from mock_llm import get_llm_plain
        HAS_AI_AGENT = False
        print("Using mock LLM implementation (ai_agent module not found)")
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you've installed all required dependencies")
    sys.exit(1)

# ASCII art logo
LOGO = """
┌─────────────────────────────────────────┐
│  AI-DRIVEN PRODUCTIVITY SHELL TOOL      │
│                                         │
│  Natural Language → Tasks → Commands    │
└─────────────────────────────────────────┘
"""

# Environment variable guidance
ENV_GUIDANCE = """
API key not configured. To use this tool with actual LLM capabilities:

1. Create a .env file in the project root with your API keys:

   # For OpenAI
   OPENAI_API_KEY=your_api_key_here
   
   # For Google (if using Gemini models)
   GOOGLE_API_KEY=your_api_key_here
   
   # Model selection
   DEFAULT_MODEL=gpt-4  # or gpt-3.5-turbo, gemini-pro, etc.

2. Install the required dependencies:
   pip install -r cli/requirements-core.txt

For testing without API keys, you can use the mock implementation:
   python cli/agent.py --test
"""


class Agent:
    """
    Main agent class that integrates task parsing and command synthesis.
    """
    
    def __init__(self, use_mock=False):
        """
        Initialize the agent with task parser and command synthesizer.
        
        Args:
            use_mock: Whether to use the mock LLM implementation
        """
        try:
            # Initialize the LLM
            if use_mock or not HAS_AI_AGENT:
                try:
                    from mock_llm import get_llm_plain as get_mock_llm
                    self.llm = get_mock_llm()
                    print("Using mock LLM for testing")
                except ImportError:
                    print("Could not import mock_llm.py. Make sure it exists in the cli directory.")
                    sys.exit(1)
            else:
                self.llm = get_llm_plain()
                
            if self.llm is None:
                # Check for API keys and provide guidance
                if not os.getenv('OPENAI_API_KEY') and not os.getenv('GOOGLE_API_KEY'):
                    print(ENV_GUIDANCE)
                raise ValueError("Failed to initialize LLM. Please check your API keys and configuration.")
                
            # Initialize parser and synthesizer
            self.parser = TaskParser(self.llm)
            self.synthesizer = CommandSynthesizer(self.llm)
            
            # Initialize command history for readline
            self.command_history = []
            self.setup_readline()
            
        except Exception as e:
            print(f"Error initializing agent: {e}")
            traceback.print_exc()
            sys.exit(1)
    
    def setup_readline(self):
        """
        Set up readline for command history and editing.
        """
        # Set up command history file
        try:
            history_file = os.path.expanduser("~/.ai_shell_history")
            try:
                readline.read_history_file(history_file)
            except (FileNotFoundError, AttributeError, IOError):
                pass
            
            readline.set_history_length(1000)
            try:
                # Save history on exit
                import atexit
                atexit.register(readline.write_history_file, history_file)
            except (AttributeError, TypeError):
                print("Warning: Could not set up history file")
        except Exception as e:
            print(f"Warning: Could not set up readline functionality: {e}")
    
    def parse_input(self, user_input: str) -> List[Tuple[str, str]]:
        """
        Parse user input into task pairs.
        
        Args:
            user_input: Natural language input from user
            
        Returns:
            List of (verb, object) tuples
        """
        tasks = self.parser.parse_tasks(user_input)
        
        # Fall back to simple parsing if LLM parsing fails
        if not tasks:
            print("Using fallback parsing method...")
            tasks = self.parser.parse_tasks_simple(user_input)
        
        return tasks
    
    def execute_command(self, command: str) -> Tuple[str, bool]:
        """
        Execute a shell command and return its output and success status.
        
        Args:
            command: Shell command to execute
            
        Returns:
            Tuple of (output, success)
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            
            success = result.returncode == 0
            return output, success
        except Exception as e:
            return f"Error executing command: {e}", False
    
    def run_repl(self):
        """
        Run the main Read-Eval-Print Loop for the agent.
        """
        print(LOGO)
        print("Type 'exit' or 'quit' to exit, 'help' for help.")
        
        while True:
            try:
                # Get input
                user_input = input("\n>> ").strip()
                
                # Handle special commands
                if user_input.lower() in ('exit', 'quit'):
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif not user_input:
                    continue
                
                # Parse input into tasks
                tasks = self.parse_input(user_input)
                
                if not tasks:
                    print("I couldn't parse that into actionable tasks. Please try rephrasing.")
                    continue
                
                print(f"\nI've broken that down into {len(tasks)} tasks:")
                for i, (verb, obj) in enumerate(tasks, 1):
                    print(f"{i}. {verb.title()} {obj}")
                
                # Process each task
                for verb, obj in tasks:
                    print(f"\nProcessing task: {verb} {obj}")
                    
                    # Synthesize command
                    result = self.synthesizer.synthesize_command((verb, obj))
                    
                    if not result['command']:
                        print("Sorry, I couldn't generate a command for this task.")
                        continue
                    
                    # Present command for approval
                    print(f"\nAI suggests: {result['command']}")
                    print(f"Explanation: {result['explanation']}")
                    
                    # Get user confirmation
                    confirm = input("\nRun this command? (y/N/edit): ").strip().lower()
                    
                    if confirm == 'y':
                        # Execute the command
                        print(f"\nExecuting: {result['command']}")
                        output, success = self.execute_command(result['command'])
                        
                        # Update context
                        self.synthesizer.update_context_after_execution(
                            result['command'],
                            output,
                            success
                        )
                        
                        # Show output
                        print("\nOutput:")
                        print(output)
                        
                        # Show status
                        if success:
                            print("\n✓ Command executed successfully")
                        else:
                            print("\n✗ Command failed")
                            
                    elif confirm.startswith('edit'):
                        # Let user edit the command
                        edited_cmd = input(f"Edit command: {result['command']}\n> ").strip()
                        if edited_cmd:
                            print(f"\nExecuting edited command: {edited_cmd}")
                            output, success = self.execute_command(edited_cmd)
                            
                            # Update context
                            self.synthesizer.update_context_after_execution(
                                edited_cmd,
                                output,
                                success
                            )
                            
                            # Show output
                            print("\nOutput:")
                            print(output)
                            
                            # Show status
                            if success:
                                print("\n✓ Command executed successfully")
                            else:
                                print("\n✗ Command failed")
                    else:
                        print("Command skipped.")
            
            except KeyboardInterrupt:
                print("\nOperation cancelled. Type 'exit' to quit.")
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
    
    def show_help(self):
        """
        Display help information.
        """
        help_text = """
        AI-Driven Productivity Shell Tool - Help
        ---------------------------------------
        
        This tool allows you to express tasks in natural language,
        which will be broken down and converted into shell commands.
        
        Usage:
          - Type your request in natural language
          - The AI will break it down into tasks
          - For each task, a command will be suggested
          - You can approve (y), skip (n), or edit the command
          
        Special commands:
          help - Show this help message
          exit/quit - Exit the program
          
        Examples of things you can ask:
          "Find all PDF files in my Documents folder"
          "Create a backup of my project and compress it"
          "Check system information and available disk space"
        """
        print(help_text)


def run_test_mode():
    """Run a simple test using the mock LLM"""
    print("\n=== Running in test mode with mock LLM ===\n")
    try:
        # Create agent with mock LLM
        agent = Agent(use_mock=True)
        
        # Define test inputs
        test_inputs = [
            "List all files in the current directory",
            "Find all Python files modified in the last week",
            "Check system information and show available disk space"
        ]
        
        # Process each test input
        for user_input in test_inputs:
            print(f"\n>> {user_input}")
            
            # Parse input into tasks
            tasks = agent.parse_input(user_input)
            
            if not tasks:
                print("I couldn't parse that into actionable tasks.")
                continue
            
            print(f"\nI've broken that down into {len(tasks)} tasks:")
            for i, (verb, obj) in enumerate(tasks, 1):
                print(f"{i}. {verb.title()} {obj}")
            
            # Process each task
            for verb, obj in tasks:
                print(f"\nProcessing task: {verb} {obj}")
                
                # Synthesize command
                result = agent.synthesizer.synthesize_command((verb, obj))
                
                if not result['command']:
                    print("Sorry, I couldn't generate a command for this task.")
                    continue
                
                # Display command and explanation
                print(f"\nAI suggests: {result['command']}")
                print(f"Explanation: {result['explanation']}")
                print("\nCommand execution skipped in test mode.")
        
        print("\n=== Test completed successfully ===\n")
    except Exception as e:
        print(f"Error in test mode: {e}")
        traceback.print_exc()


def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="AI-Driven Productivity Shell Tool"
    )
    # Add future command line arguments here
    parser.add_argument('--test', action='store_true', help='Run in test mode using mock LLM')
    return parser.parse_args()


def main():
    """
    Main entry point for the application.
    """
    # Parse command line args
    args = parse_args()
    
    # If test mode is enabled, use the mock LLM
    if args.test:
        run_test_mode()
        return
    
    # Create and run the agent - will fallback to mock if ai_agent is not available
    agent = Agent()
    agent.run_repl()


if __name__ == "__main__":
    main() 