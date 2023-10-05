#!/bin/bash

echo "BUILD START"

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv/{lib/python*,include,pip,share,bin/__pycache__}
    echo "Virtual environment cleaned."
else
    echo "No existing virtual environment found."
fi

# Create a new virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt || { echo 'Failed to install dependencies'; exit 1; }

# Collect static files
python manage.py collectstatic --noinput || { echo 'Failed to collect static files'; exit 1; }

# Debugging: Print the size of the virtual environment
du -sh venv

# Debugging: List installed packages and their sizes
echo "Installed packages and their sizes:"
pip freeze | xargs pip show | awk '/^Name:|^Size:/'

# Debugging: Print the size of the deployment directory
du -sh .

# Deactivate the virtual environment
deactivate

echo "BUILD END"
