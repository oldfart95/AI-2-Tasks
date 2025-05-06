# PowerShell script to run Google AI integration tests

Write-Host "Running Google AI API integration tests..." -ForegroundColor Green

# Get the script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = $scriptDir

# Install required dependencies
Write-Host "Checking for required dependencies..." -ForegroundColor Cyan
pip install -r $projectRoot/tests/requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install dependencies." -ForegroundColor Red
    Write-Host "Please check your internet connection and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Verify ai_agent directory exists
$aiAgentPath = Join-Path -Path $projectRoot -ChildPath "ai_agent"
if (-not (Test-Path -Path $aiAgentPath)) {
    Write-Host "ERROR: ai_agent directory not found at $aiAgentPath" -ForegroundColor Red
    Write-Host "The tests require this directory to be present." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Verify ai_shell_agent module exists within ai_agent
$moduleDir = Join-Path -Path $aiAgentPath -ChildPath "ai_shell_agent"
if (-not (Test-Path -Path $moduleDir)) {
    Write-Host "ERROR: ai_shell_agent module not found at $moduleDir" -ForegroundColor Red
    Write-Host "The tests require this module to be present in the ai_agent directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Ensure PYTHONPATH includes the project root and ai_agent directory
$env:PYTHONPATH = "$projectRoot;$aiAgentPath"
Write-Host "Set PYTHONPATH to: $env:PYTHONPATH" -ForegroundColor Cyan

# Run the tests
Write-Host "Running tests..." -ForegroundColor Cyan
python $projectRoot/tests/test_google_ai.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "Tests completed successfully." -ForegroundColor Green
} else {
    Write-Host "Tests failed with error code $LASTEXITCODE." -ForegroundColor Red
    
    # Provide more diagnostic information
    Write-Host "`nDiagnostic information:" -ForegroundColor Yellow
    Write-Host "- Python version:" -ForegroundColor Yellow
    python --version
    
    Write-Host "- Project structure:" -ForegroundColor Yellow
    Get-ChildItem -Path $projectRoot -Depth 1 | Format-Table Name, LastWriteTime, Length
    
    Write-Host "- ai_agent structure:" -ForegroundColor Yellow
    Get-ChildItem -Path $aiAgentPath -Depth 1 | Format-Table Name, LastWriteTime, Length
}

Read-Host "Press Enter to exit" 