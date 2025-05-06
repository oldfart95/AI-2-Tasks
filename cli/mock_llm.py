"""
mock_llm.py - Mock LLM implementation for testing

This module provides mock implementations of LLM functionality
for testing when the actual LLM module can't be imported.
"""

class MockResponse:
    """A mock response from an LLM"""
    def __init__(self, content):
        self.content = content

class MockLLM:
    """A mock LLM for testing"""
    def __init__(self):
        pass
        
    def invoke(self, messages):
        """Return a mock response based on the input messages"""
        # Check if this is a task parsing request or command synthesis request
        system_content = messages[0].content if messages else ""
        user_content = messages[1].content if len(messages) > 1 else ""
        
        # For task parsing (look for verb-object in system prompt)
        if "verb-object pairs" in system_content:
            content = "list, files in current directory"
            if "system information" in user_content.lower():
                content = "check, system information\nshow, disk space"
            elif "python files" in user_content.lower():
                content = "find, Python files modified in the last week"
            return MockResponse(content)
            
        # For command synthesis (look for CLI command generator in system prompt)
        elif "CLI command generator" in system_content:
            if "list files" in user_content.lower():
                return MockResponse(
                    "COMMAND: dir\n"
                    "EXPLANATION: Lists all files and directories in the current location."
                )
            elif "python files" in user_content.lower():
                return MockResponse(
                    "COMMAND: Get-ChildItem -Recurse -Include *.py | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }\n"
                    "EXPLANATION: Finds all Python files (*.py) modified in the last week using PowerShell."
                )
            elif "system information" in user_content.lower():
                return MockResponse(
                    "COMMAND: systeminfo\n"
                    "EXPLANATION: Displays detailed configuration information about the computer and operating system."
                )
            elif "disk space" in user_content.lower():
                return MockResponse(
                    "COMMAND: Get-PSDrive -PSProvider FileSystem\n"
                    "EXPLANATION: Shows disk space information for all drives on the system using PowerShell."
                )
            else:
                return MockResponse(
                    "COMMAND: echo 'Hello, world!'\n"
                    "EXPLANATION: A simple command that prints 'Hello, world!' to the console."
                )
        
        # Default fallback
        return MockResponse("No mock response available for this type of request.")

def get_llm_plain():
    """Get a mock LLM instance for testing"""
    return MockLLM() 