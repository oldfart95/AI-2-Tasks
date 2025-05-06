"""
task_parser.py - Breaks down natural language input into Verb + Object task pairs

This module utilizes LLM to parse free-form natural language inputs into
structured verb-object pairs that can be processed by the command synthesizer.
"""

from typing import List, Tuple, Dict, Optional
import re
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

class TaskParser:
    """
    Parses natural language input into Verb + Object pairs using an LLM.
    """
    
    def __init__(self, llm: BaseChatModel):
        """
        Initialize the TaskParser with an LLM instance.
        
        Args:
            llm: A language model instance from langchain
        """
        self.llm = llm
        self._system_prompt = """
        You are a task parser that converts natural language requests into structured Verb + Object pairs.
        
        For each input, identify the key actions and break them down into verb-object pairs.
        For example:
        
        Input: "Create a backup of my documents folder and then search for large files"
        Output: 
        backup, documents folder
        search, large files
        
        Input: "List all Python files in the current directory and count how many lines each has"
        Output:
        list, Python files in current directory
        count, lines in each file
        
        Keep verbs simple and action-oriented. Focus on identifying the primary tasks.
        Return only the verb-object pairs, one per line, with the verb and object separated by a comma.
        """
    
    def parse_tasks(self, text: str) -> List[Tuple[str, str]]:
        """
        Parse natural language input into a list of (verb, object) tuples.
        
        Args:
            text: The natural language input to parse
            
        Returns:
            A list of (verb, object) tuples
        """
        messages = [
            SystemMessage(content=self._system_prompt),
            HumanMessage(content=text)
        ]
        
        try:
            response = self.llm.invoke(messages)
            task_pairs = []
            
            # Parse the response, expecting "verb, object" format
            for line in response.content.strip().split("\n"):
                if not line.strip():
                    continue
                
                parts = line.split(",", 1)
                if len(parts) == 2:
                    verb = parts[0].strip().lower()
                    obj = parts[1].strip()
                    task_pairs.append((verb, obj))
            
            return task_pairs
        except Exception as e:
            print(f"Error parsing tasks: {e}")
            return []
    
    def parse_tasks_simple(self, text: str) -> List[Tuple[str, str]]:
        """
        A simple rule-based fallback parser that tries to extract verb-object pairs
        without using an LLM (for cases where the LLM might not be available).
        
        Args:
            text: The natural language input to parse
            
        Returns:
            A list of (verb, object) tuples
        """
        # Simple rule-based extraction of common command verbs
        common_verbs = [
            "list", "find", "search", "create", "delete", "remove", "copy", "move",
            "rename", "show", "display", "count", "backup", "install", "update",
            "download", "upload", "check", "analyze", "run", "execute", "print",
            "open", "close", "read", "write", "edit", "modify", "compile"
        ]
        
        task_pairs = []
        
        # Try to find verb-object patterns
        for verb in common_verbs:
            # Look for patterns like "verb something" or "verb the something"
            patterns = [
                rf"\b{verb}\s+the\s+([^,.;]+)",
                rf"\b{verb}\s+([^,.;]+)"
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, text.lower())
                for match in matches:
                    obj = match.group(1).strip()
                    # Don't include the verb in the object
                    if obj and not obj.startswith(verb):
                        task_pairs.append((verb, obj))
        
        return task_pairs


def get_example_tasks() -> List[str]:
    """
    Return a list of example natural language tasks for testing.
    """
    return [
        "List all the files in the current directory",
        "Create a backup of my project and compress it",
        "Find all Python files modified in the last week",
        "Show system information and check available disk space",
        "Download the latest version of Node.js and install it"
    ]


if __name__ == "__main__":
    # This is for testing the parser with example inputs
    from ai_agent.ai_shell_agent.llm import get_llm_plain
    
    llm = get_llm_plain()
    if llm:
        parser = TaskParser(llm)
        
        for example in get_example_tasks():
            print(f"\nInput: {example}")
            print("Parsed tasks:")
            tasks = parser.parse_tasks(example)
            for verb, obj in tasks:
                print(f"  - Verb: {verb}, Object: {obj}")
    else:
        print("Could not initialize LLM for task parsing. Using rule-based parsing instead.")
        parser = TaskParser(None)
        
        for example in get_example_tasks():
            print(f"\nInput: {example}")
            print("Parsed tasks (rule-based):")
            tasks = parser.parse_tasks_simple(example)
            for verb, obj in tasks:
                print(f"  - Verb: {verb}, Object: {obj}") 