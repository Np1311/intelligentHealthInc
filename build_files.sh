#!/bin/bash

echo "BUILD START"

# Remove existing virtual environment if it exists
rm -rf venv

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || { echo 'Failed to install dependencies'; exit 1; }
python manage.py collectstatic --noinput || { echo 'Failed to collect static files'; exit 1; }
deactivate

echo "BUILD END"
