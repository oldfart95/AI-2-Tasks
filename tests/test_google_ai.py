#!/usr/bin/env python
"""
test_google_ai.py - Test script for verifying Google AI API integration

This script tests the connection to Google AI API and verifies that basic 
functionality is working correctly.
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    if os.path.exists(os.path.join(project_root, '.env')):
        load_dotenv(os.path.join(project_root, '.env'))
    print("Loaded environment variables from .env file")
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")

# Check for required packages
MISSING_PACKAGES = []
try:
    import langchain_google_genai
except ImportError:
    MISSING_PACKAGES.append("langchain-google-genai")
    
try:
    import langchain_core
except ImportError:
    MISSING_PACKAGES.append("langchain-core")

# Check if ai_agent is properly set up (it's a local module, not an installable package)
HAS_AI_AGENT = False
ai_agent_path = project_root / "ai_agent"
if not ai_agent_path.exists():
    print(f"Warning: ai_agent directory not found at {ai_agent_path}")
else:
    # Import ai_agent as a package
    try:
        # Fix: Import from the correct module path
        from ai_agent.ai_shell_agent.llm import get_llm_plain
        HAS_AI_AGENT = True
    except ImportError as e:
        print(f"Cannot import from ai_agent.ai_shell_agent: {e}")
        print("Make sure the ai_agent directory structure is correct")
        # Try alternate import path as fallback
        try:
            sys.path.insert(0, str(ai_agent_path))
            from ai_shell_agent.llm import get_llm_plain
            HAS_AI_AGENT = True
            print("Successfully imported using alternative path")
        except ImportError as e2:
            print(f"Fallback import also failed: {e2}")


class GoogleAITest(unittest.TestCase):
    """Test cases for Google AI API integration"""
    
    def setUp(self):
        """Skip tests if dependencies are missing"""
        if MISSING_PACKAGES:
            self.skipTest(f"Missing required packages: {', '.join(MISSING_PACKAGES)}")
    
    def test_api_key_exists(self):
        """Test that Google API key is set in environment variables"""
        api_key = os.getenv('GOOGLE_API_KEY')
        self.assertIsNotNone(api_key, "GOOGLE_API_KEY environment variable not set")
        self.assertTrue(len(api_key) > 0, "GOOGLE_API_KEY is empty")
        print("✓ Google API key found in environment variables")
    
    def test_google_ai_connection(self):
        """Test that we can connect to Google AI API and get a response"""
        if "langchain-google-genai" in MISSING_PACKAGES:
            self.skipTest("langchain-google-genai package is not installed")
            
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            # Initialize the model - using gemini-1.5-pro instead of gemini-pro
            model = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                convert_system_message_to_human=True
            )
            
            # Test with a simple prompt
            from langchain_core.messages import HumanMessage
            response = model.invoke([HumanMessage(content="Say 'Hello, World!' and nothing else.")])
            
            # Check response
            self.assertIsNotNone(response, "No response received from Google AI API")
            self.assertIn("Hello, World", response.content, 
                          f"Expected 'Hello, World' in response, got: {response.content}")
            
            print(f"✓ Successfully received response from Google AI: '{response.content}'")
            return True
        except Exception as e:
            self.fail(f"Failed to connect to Google AI API: {str(e)}")
            return False
    
    def test_llm_integration(self):
        """Test our application's LLM integration with Google AI"""
        if not HAS_AI_AGENT:
            self.skipTest("ai_shell_agent module is not properly configured")
            
        try:
            # Import get_llm_plain and use it directly - it should already be configured to use Google
            from ai_agent.ai_shell_agent.llm import get_llm_plain
            from langchain_core.messages import HumanMessage
            
            # Get the LLM instance
            llm = get_llm_plain()
            
            # Test with a simple prompt
            response = llm.invoke([HumanMessage(content="Generate a simple shell command to list files.")])
            
            # Check response
            self.assertIsNotNone(response, "No response received from LLM")
            self.assertTrue(len(response.content) > 0, "Empty response from LLM")
            
            print(f"✓ Successfully integrated with LLM: '{response.content}'")
            return True
                
        except Exception as e:
            self.fail(f"Failed to test LLM integration: {str(e)}")
            return False


def run_tests():
    """Run the tests and return True if all tests pass"""
    if MISSING_PACKAGES:
        print(f"\n⚠️ Missing required PyPI packages: {', '.join(MISSING_PACKAGES)}")
        print("Install them with: pip install " + " ".join(MISSING_PACKAGES))
        print("\nNote: The ai_shell_agent module is not a PyPI package, but a local module.")
        print("Make sure the ai_agent directory is correctly structured and accessible.")
        return False
        
    if not HAS_AI_AGENT:
        print("\n⚠️ The ai_shell_agent module could not be imported.")
        print("This is a local module, not a package to install with pip.")
        print("Check the ai_agent directory structure and make sure it's properly set up.")
        return False
        
    suite = unittest.TestSuite()
    suite.addTest(GoogleAITest('test_api_key_exists'))
    suite.addTest(GoogleAITest('test_google_ai_connection'))
    suite.addTest(GoogleAITest('test_llm_integration'))
    
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running Google AI API integration tests...")
    success = run_tests()
    if success:
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed or were skipped due to missing dependencies.")
        sys.exit(1) 