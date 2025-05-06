@echo off
echo Running Google AI API integration tests...

echo Checking for required dependencies...
pip install -r tests/requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo Running tests...
python tests/test_google_ai.py
if %ERRORLEVEL% EQU 0 (
    echo Tests completed successfully.
) else (
    echo Tests failed with error code %ERRORLEVEL%.
)
pause 