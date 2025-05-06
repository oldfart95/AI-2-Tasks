# Google AI Integration Tests

This directory contains tests to verify the integration with Google AI API.

## Setup

Before running the tests, ensure you have:

1. A `.env` file in the project root with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

2. Required dependencies installed:
   ```
   pip install -r tests/requirements.txt
   ```

3. The proper directory structure:
   - The `ai_agent` directory must exist in the project root
   - Within `ai_agent`, the `ai_shell_agent` module must exist

## Running the Tests

### Windows

You can run the tests using either:

- **PowerShell script** (recommended):
  ```
  .\run_tests.ps1
  ```
  This sets up the correct Python path environment and runs all tests.

- **Batch file**:
  ```
  run_tests.bat
  ```

### Linux/Mac

Run the test script directly:
```
python tests/test_google_ai.py
```

## Test Cases

The test suite includes the following tests:

1. **API Key Check**: Verifies that the Google API key is properly set in environment variables
2. **Direct Connection**: Tests direct connection to Google AI with a simple prompt
3. **Application Integration**: Tests the application's integration with Google AI

## Troubleshooting

If you encounter import errors or other issues, you can use the diagnostic tools:

### Diagnosing Import Issues

Run one of these scripts to diagnose import and path issues:

- **PowerShell** (recommended):
  ```
  .\run_diagnostics.ps1
  ```

- **Batch file**:
  ```
  run_diagnostics.bat
  ```

These tools will:
1. Check your Python environment
2. Verify project structure
3. Test imports of required dependencies
4. Test imports of local modules
5. Provide detailed diagnostic information

### Common Issues

- **Missing Packages**: Install required packages using the requirements file
  ```
  pip install -r tests/requirements.txt
  ```

- **Import Errors for `ai_shell_agent`**: This is a local module, not a PyPI package
  - Ensure the `ai_agent` directory exists in your project root
  - Ensure the `ai_shell_agent` module exists within `ai_agent`
  - Use the diagnostic scripts to verify the structure

- **API Key Issues**: Check your `.env` file placement and format 