#!/usr/bin/env python3
"""
Setup script to migrate from SQLite to PostgreSQL (Supabase)
Run this script after setting your DATABASE_URL environment variable
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scouting_backend.settings')
django.setup()

from django.core.management import execute_from_command_line

def main():
    print("🔧 Setting up PostgreSQL migration...")
    
    # Check if DATABASE_URL is set
    if not os.environ.get('DATABASE_URL'):
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("Please set it with your Supabase connection string:")
        print('export DATABASE_URL="postgresql://user:password@host:port/database"')
        return
    
    print("✅ DATABASE_URL found")
    
    # Run migrations
    print("🔄 Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ Setup complete! Your app is now using PostgreSQL.")
    print("To migrate existing SQLite data, run: python manage.py migrate_sqlite_data.py")

if __name__ == '__main__':
    main()