"""
command_synthesizer.py - Converts parsed tasks into executable shell commands

This module interfaces with AI-Shell-Agent's LLM integration to convert
verb-object task pairs into executable shell commands with proper context.
"""

from typing import List, Dict, Tuple, Optional, Any
import os
import sys
import platform
import shutil
import re
from collections import deque
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import real LLM, fallback to mock if not available
try:
    from langchain_core.language_models import BaseChatModel
    from langchain_core.messages import SystemMessage, HumanMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Warning: langchain not available, using mock LLM for command synthesis")

class CommandContext:
    """
    Stores contextual information for command synthesis.
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize the command context.
        
        Args:
            max_history: Maximum number of previous commands to retain
        """
        self.os_info = {
            'name': platform.system(),
            'version': platform.version(),
            'release': platform.release(),
            'architecture': platform.machine()
        }
        
        self.current_dir = os.getcwd()
        self.home_dir = os.path.expanduser("~")
        self.command_history = deque(maxlen=max_history)
        self.shell_info = self._detect_shell()
    
    def _detect_shell(self) -> Dict[str, str]:
        """
        Detect the user's shell environment.
        
        Returns:
            Dict containing shell information
        """
        shell_info = {
            'name': 'unknown',
            'path': 'unknown',
            'is_powershell': False,
            'is_bash': False,
            'is_cmd': False
        }
        
        # Get shell from environment
        shell_path = os.environ.get('SHELL', '')
        comspec = os.environ.get('COMSPEC', '')
        
        if shell_path:
            shell_name = os.path.basename(shell_path)
            shell_info['name'] = shell_name
            shell_info['path'] = shell_path
            shell_info['is_bash'] = 'bash' in shell_name.lower()
        elif comspec:
            shell_name = os.path.basename(comspec)
            shell_info['name'] = shell_name
            shell_info['path'] = comspec
            shell_info['is_cmd'] = 'cmd' in shell_name.lower()
        
        # Check if PowerShell is available
        powershell_path = shutil.which('powershell') or shutil.which('pwsh')
        if powershell_path:
            if not shell_path and not comspec:
                shell_info['name'] = 'powershell'
                shell_info['path'] = powershell_path
            shell_info['is_powershell'] = True
        
        return shell_info
    
    def update_current_dir(self, new_dir: str):
        """
        Update the current directory context.
        
        Args:
            new_dir: The new current directory
        """
        self.current_dir = new_dir
    
    def add_to_history(self, command: str, output: str = '', success: bool = True):
        """
        Add a command and its output to the history.
        
        Args:
            command: The executed command
            output: Command output (truncated if too large)
            success: Whether the command executed successfully
        """
        # Truncate output if it's too large
        max_output_length = 1000
        if len(output) > max_output_length:
            output = output[:max_output_length] + "... [output truncated]"
        
        self.command_history.append({
            'command': command,
            'output': output,
            'success': success,
            'directory': self.current_dir
        })
    
    def get_formatted_history(self) -> str:
        """
        Get formatted command history for context.
        
        Returns:
            Formatted string of recent commands and outputs
        """
        if not self.command_history:
            return "No command history."
        
        history_text = "Recent commands:\n"
        
        for i, entry in enumerate(self.command_history):
            history_text += f"{i+1}. Command: {entry['command']}\n"
            history_text += f"   Directory: {entry['directory']}\n"
            if entry['output']:
                # Format output for readability
                output_lines = entry['output'].split('\n')
                truncated_output = '\n   '.join(output_lines[:5])
                if len(output_lines) > 5:
                    truncated_output += "\n   ... [output truncated]"
                history_text += f"   Output: {truncated_output}\n"
            history_text += f"   Success: {entry['success']}\n\n"
        
        return history_text
    
    def to_dict(self) -> Dict:
        """
        Convert context to a dictionary for prompt context.
        
        Returns:
            Dict representation of the context
        """
        return {
            'os': self.os_info,
            'current_directory': self.current_dir,
            'home_directory': self.home_dir,
            'shell': self.shell_info,
            'recent_history': self.get_formatted_history()
        }


class CommandSynthesizer:
    """
    Synthesizes shell commands from verb-object task pairs.
    """
    
    def __init__(self, llm=None):
        """
        Initialize the CommandSynthesizer with an LLM instance.
        
        Args:
            llm: A language model instance from langchain (or None for mock)
        """
        self.llm = llm
        self.context = CommandContext()
        self._system_prompt = """
        You are an expert CLI command generator that helps users execute tasks on their computer.
        Your role is to convert a task described as a verb and object into the most appropriate shell command.
        
        When generating commands:
        - Consider the user's operating system and current shell environment
        - Use OS-specific commands and syntax (PowerShell, Bash, CMD, etc.)
        - Use absolute paths when necessary for clarity
        - Provide safe commands that won't damage the system
        - Include any necessary flags or options with brief explanations
        - For complex operations, use a pipeline or multiple commands when appropriate
        
        Format your response as follows:
        COMMAND: [the executable command]
        EXPLANATION: [brief explanation of what the command does and any options used]
        
        For example:
        Task: List files in current directory
        OS: Windows
        Shell: PowerShell
        
        COMMAND: Get-ChildItem
        EXPLANATION: Lists all files and folders in the current directory. This is the PowerShell equivalent of 'ls' in Unix-like systems.
        """
    
    def synthesize_command(self, task: Tuple[str, str]) -> Dict[str, str]:
        """
        Synthesize a shell command from a verb-object task pair.
        
        Args:
            task: A tuple containing (verb, object)
            
        Returns:
            Dict containing 'command' and 'explanation' keys
        """
        verb, obj = task
        task_description = f"{verb} {obj}"
        
        # Format the context information for the prompt
        context_dict = self.context.to_dict()
        os_info = f"OS: {context_dict['os']['name']} {context_dict['os']['version']}"
        shell_info = f"Shell: {context_dict['shell']['name']}"
        dir_info = f"Current Directory: {context_dict['current_directory']}"
        
        context_text = f"{os_info}\n{shell_info}\n{dir_info}\n\n"
        if self.context.command_history:
            context_text += f"{context_dict['recent_history']}\n"
        
        messages = [
            SystemMessage(content=self._system_prompt),
            HumanMessage(content=f"Task: {task_description}\n{context_text}")
        ]
        
        if self.llm and LLM_AVAILABLE:
            return self._synthesize_with_llm(task, context_dict['os']['name'], context_dict)
        else:
            return self._synthesize_with_mock(task, context_dict['os']['name'], context_dict)
    
    def _synthesize_with_llm(self, task: Tuple[str, str], os_type: str, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Synthesize a command using the LLM.
        
        Args:
            task: A tuple containing (verb, object)
            os_type: The operating system type
            context: Additional context
            
        Returns:
            Dict containing 'command' and 'explanation' keys
        """
        verb, obj = task
        task_description = f"{verb} {obj}"
        
        # System prompt to guide command generation
        system_prompt = f"""
        You are a command line expert. Your task is to generate the appropriate shell command
        based on the user's request. The user is on {os_type} operating system.
        
        Please provide ONLY the shell command without any explanations or markdown.
        The command should be accurate, efficient, and safe to execute.
        
        For example:
        User request: "list all files in current directory"
        Response for Windows: "dir"
        Response for Linux/macOS: "ls -la"
        
        If you need to use quotation marks, prefer double quotes unless single quotes are required.
        Avoid using potentially dangerous commands that could damage the system or lose data.
        
        Current directory: {context['current_directory']}
        Additional context: {json.dumps(context, default=str)}
        """

        try:
            # Generate the command
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Task: {task_description}")
            ]
            
            response = self.llm.invoke(messages)
            command = response.content.strip()
            
            # Generate an explanation in a separate call
            explanation_prompt = f"""
            Provide a brief, one-sentence explanation of what this command does:
            {command}
            
            Make the explanation helpful for a non-expert user. Be concise.
            """
            
            explanation_messages = [
                SystemMessage(content="You are a helpful command line assistant."),
                HumanMessage(content=explanation_prompt)
            ]
            
            explanation_response = self.llm.invoke(explanation_messages)
            explanation = explanation_response.content.strip()
            
            return {
                'command': command,
                'explanation': explanation,
                'task': task_description
            }
        except Exception as e:
            print(f"Error using LLM for command synthesis: {e}")
            # Fall back to mock synthesis if LLM fails
            return self._synthesize_with_mock(task, os_type, context)
    
    def _synthesize_with_mock(self, task: Tuple[str, str], os_type: str, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate a command using a rule-based mock implementation.
        
        Args:
            task: A tuple containing (verb, object)
            os_type: The operating system type
            context: Additional context
            
        Returns:
            Dict containing 'command' and 'explanation' keys
        """
        verb, obj = task
        task_description = f"{verb} {obj}"
        
        task_lower = task_description.lower()
        is_windows = os_type.startswith('win')
        
        command = ""
        explanation = ""
        
        # Simple rule-based mock command generation
        if "list" in task_lower and "file" in task_lower:
            if is_windows:
                command = "dir"
                explanation = "Lists all files and directories in the current location."
            else:
                command = "ls -la"
                explanation = "Lists all files and directories with details in the current location."
        
        elif "create" in task_lower and "directory" in task_lower:
            dir_name = "new_directory"
            for word in task_lower.split():
                if word not in ["create", "directory", "folder", "new", "a", "an", "the"]:
                    dir_name = word
                    break
            
            if is_windows:
                command = f"mkdir {dir_name}"
            else:
                command = f"mkdir {dir_name}"
            
            explanation = f"Creates a new directory named '{dir_name}'."
        
        elif "search" in task_lower or "find" in task_lower:
            search_term = "example"
            for word in task_lower.split():
                if word not in ["search", "find", "for", "a", "an", "the", "in", "files"]:
                    search_term = word
                    break
            
            if is_windows:
                command = f"findstr /s /i {search_term} *.*"
                explanation = f"Searches for '{search_term}' in all files in the current directory and subdirectories."
            else:
                command = f"grep -r {search_term} ."
                explanation = f"Searches for '{search_term}' in all files in the current directory and subdirectories."
        
        elif "date" in task_lower or "time" in task_lower:
            if is_windows:
                command = "date /t & time /t"
                explanation = "Shows the current date and time."
            else:
                command = "date"
                explanation = "Shows the current date and time."
                
        elif "file size" in task_lower or "disk space" in task_lower:
            if is_windows:
                command = "dir | sort /r /+s"
                explanation = "Lists files sorted by size in descending order."
            else:
                command = "du -sh * | sort -hr"
                explanation = "Lists directories and files with their sizes sorted by size."
        
        else:
            # Default echo command for unknown tasks
            if is_windows:
                command = "echo Not sure how to perform this task"
            else:
                command = "echo 'Not sure how to perform this task'"
            
            explanation = "This command doesn't perform the requested task. Please try a different description."
        
        return {
            'command': command,
            'explanation': explanation,
            'task': task_description
        }
    
    def update_context_after_execution(self, command: str, output: str, success: bool):
        """
        Update context after a command has been executed.
        
        Args:
            command: The executed command
            output: Command output
            success: Whether the command executed successfully
        """
        # Update current directory if it changed
        if success and ('cd ' in command or 'chdir' in command or 'Set-Location' in command):
            try:
                new_dir = os.getcwd()
                if new_dir != self.context.current_dir:
                    self.context.update_current_dir(new_dir)
            except Exception:
                pass
        
        # Add command to history
        self.context.add_to_history(command, output, success)


if __name__ == "__main__":
    # This is for testing the command synthesizer with example tasks
    from ai_agent.ai_shell_agent.llm import get_llm_plain
    
    llm = get_llm_plain()
    if llm:
        synthesizer = CommandSynthesizer(llm)
        
        # Example tasks to synthesize commands for
        example_tasks = [
            ("list", "files in current directory"),
            ("find", "large files over 100MB"),
            ("create", "backup of important documents"),
            ("check", "system information")
        ]
        
        for verb, obj in example_tasks:
            print(f"\nTask: {verb} {obj}")
            result = synthesizer.synthesize_command((verb, obj))
            
            print(f"Command: {result['command']}")
            print(f"Explanation: {result['explanation']}")
            
            # Simulate command execution and update context
            synthesizer.update_context_after_execution(
                result['command'],
                "Sample output for testing",
                True
            )
        
        # Show how context builds up
        print("\nCommand History Context:")
        print(synthesizer.context.get_formatted_history())
    else:
        print("Could not initialize LLM for command synthesis.") 