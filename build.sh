#!/usr/bin/env bash
# exit on error
set -o errexit

# Use python3 -m pip instead of just pip
python3 -m pip install -r requirements.txt

python3 manage.py collectstatic --no-input
python3 manage.py migrate
