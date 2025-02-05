#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install --no-cache-dir -r requirements.txt

echo "Collecting static files..."
python3 manage.py collectstatic --no-input

echo "Build completed!"
