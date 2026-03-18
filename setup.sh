#!/bin/bash

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3-tk python3-venv

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setup complete!"