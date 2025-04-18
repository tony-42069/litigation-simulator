#!/bin/bash
# Setup script for Litigation Simulator

echo "Setting up Litigation Simulator environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found. Please install Python 3.8 or higher."
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

echo "Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Installing spaCy language model..."
python -m spacy download en_core_web_sm

echo "Setting up environment variables..."
cp .env.example .env
echo "Please update the .env file with your database credentials and API keys."

echo "Setup complete! Activate the virtual environment with:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "    source venv/Scripts/activate"
else
    echo "    source venv/bin/activate"
fi
echo "Then run the application with:"
echo "    python main.py" 