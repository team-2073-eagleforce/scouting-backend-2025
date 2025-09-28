#!/usr/bin/env bash
set -o errexit

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install --no-cache-dir -r requirements.txt

echo "Installing Node.js dependencies..."
npm ci

echo "Building frontend assets..."
npm run build

echo "Collecting static files..."
python3 manage.py collectstatic --no-input

echo "Build completed!"
