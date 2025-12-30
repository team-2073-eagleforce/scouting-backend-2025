#!/usr/bin/env bash
# Production build script for FRC Team 2073 Scouting System
# Works on Linux, macOS, and Windows (via Git Bash/WSL)

set -o errexit  # Exit on error
set -o pipefail # Exit on pipe failure
set -o nounset  # Exit on undefined variable

echo "========================================="
echo "FRC Scouting System - Build"
echo "========================================="
echo ""

# Detect Python command (python3 or python)
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python not found. Please install Python 3.10 or higher."
    exit 1
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version
echo ""

# Detect pip command
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "ERROR: pip not found. Please install pip."
    exit 1
fi

echo "Using pip: $PIP_CMD"
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found. Please install Node.js 18 or higher."
    exit 1
fi

echo "Using Node.js: $(node --version)"
echo "Using npm: $(npm --version)"
echo ""

# Step 1: Upgrade pip
echo "[1/6] Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip --quiet
echo "pip upgraded"
echo ""

# Step 2: Install Python dependencies
echo "[2/6] Installing Python dependencies..."
$PIP_CMD install --no-cache-dir -r requirements.txt --quiet
echo "Python dependencies installed"
echo ""

# Step 3: Install Node.js dependencies
echo "[3/6] Installing Node.js dependencies..."
if [ -f "package-lock.json" ]; then
    npm ci --quiet
else
    npm install --quiet
fi
echo "Node.js dependencies installed"
echo ""

# Step 4: Build frontend assets
echo "[4/6] Building frontend assets with Webpack..."
npm run build
echo "Frontend assets built"
echo ""

# Step 5: Collect static files
echo "[5/6] Collecting Django static files..."
$PYTHON_CMD manage.py collectstatic --no-input
echo "Static files collected"
echo ""

# Step 6: Run database migrations (optional, can be disabled)
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "[6/6] Running database migrations..."
    $PYTHON_CMD manage.py migrate --no-input
    echo "Migrations applied"
else
    echo "[6/6] Skipping migrations (RUN_MIGRATIONS=false)"
fi
echo ""

echo "========================================="
echo "Build completed successfully!"
echo "========================================="
echo ""
echo "To start the server:"
echo "  Development: $PYTHON_CMD manage.py runserver"
echo "  Production:  gunicorn scouting_backend.wsgi:application"
echo ""
