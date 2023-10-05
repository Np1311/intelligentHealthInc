#!/bin/bash

echo "BUILD START"

# Check Python version
echo "Using Python version $(python3 --version)"

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

# Install dependencies excluding humanize and admindocs
pip install --no-cache-dir -r requirements.txt || { echo 'Failed to install dependencies'; exit 1; }

# Remove unnecessary files and directories
echo "Removing unnecessary files and directories..."
rm -rf venv/lib/python*/site-packages/tests
rm -rf venv/lib/python*/site-packages/docs
rm -rf venv/lib/python*/site-packages/django/contrib/postgres
rm -rf venv/lib/python*/site-packages/django/contrib/humanize
rm -rf venv/lib/python*/site-packages/django/contrib/admindocs

# Collect static files
python manage.py collectstatic --noinput || { echo 'Failed to collect static files'; exit 1; }

# Debugging: Print the size of the virtual environment
du -sh venv

# Debugging: List installed packages and their sizes
echo "Installed packages and their sizes:"
pip freeze | xargs pip show | awk '/^Name:/ {name=$2} /^Size:/ {print name, $2}'

# Debugging: Print the size of the deployment directory
du -sh .

# Debugging: Print the size of specific files or directories in the environment
echo "Size of specific files or directories in the environment:"
du -sh venv/bin
du -sh venv/lib

# Debugging: Print the contents of the environment directory
echo "Contents of the environment directory:"
ls -lh venv

# Print the size of specific files or directories in the project
echo "Size of specific files or directories in the project:"
du -sh manage.py
du -sh requirements.txt
du -sh static
du -sh templates

# Deactivate the virtual environment
deactivate

echo "BUILD END"
