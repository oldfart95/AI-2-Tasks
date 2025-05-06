# PowerShell script to run AI Agent diagnostics

Write-Host "Running AI Agent import diagnostics..." -ForegroundColor Green

# Get the script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = $scriptDir

# Install required dependencies first
Write-Host "Installing required dependencies..." -ForegroundColor Cyan
pip install -r $projectRoot/tests/requirements.txt

# Set PYTHONPATH to include the project root and ai_agent directory
$aiAgentPath = Join-Path -Path $projectRoot -ChildPath "ai_agent"
$env:PYTHONPATH = "$projectRoot;$aiAgentPath"
Write-Host "Set PYTHONPATH to: $env:PYTHONPATH" -ForegroundColor Cyan

# Run the diagnostic script
Write-Host "Running diagnostics..." -ForegroundColor Cyan
python $projectRoot/tests/diagnose_imports.py

Write-Host "`nDiagnostics completed." -ForegroundColor Green
Read-Host "Press Enter to exit" 