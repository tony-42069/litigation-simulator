# PowerShell setup script for Litigation Simulator

Write-Host "Setting up Litigation Simulator environment..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Python could not be found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

Write-Host "Creating virtual environment..." -ForegroundColor Green
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

Write-Host "Installing required packages..." -ForegroundColor Green
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Installing spaCy language model..." -ForegroundColor Green
python -m spacy download en_core_web_sm

Write-Host "Setting up environment variables..." -ForegroundColor Green
if (Test-Path .env.example) {
    Copy-Item .env.example -Destination .env
    Write-Host "Please update the .env file with your database credentials and API keys." -ForegroundColor Yellow
}
else {
    Write-Host ".env.example not found. You will need to create a .env file manually." -ForegroundColor Yellow
}

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "To activate the virtual environment in the future, run:" -ForegroundColor Cyan
Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "Then run the application with:" -ForegroundColor Cyan
Write-Host "    python main.py" -ForegroundColor Cyan 