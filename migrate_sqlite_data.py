#!/usr/bin/env python3
"""
Data migration script to transfer SQLite data to PostgreSQL
"""

import os
import sys
import django
import json
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

def main():
    print("📦 Starting SQLite to PostgreSQL data migration...")
    
    # Check if SQLite file exists
    sqlite_path = BASE_DIR / 'db.sqlite3'
    if not sqlite_path.exists():
        print("❌ No SQLite database found at db.sqlite3")
        return
    
    # Temporarily use SQLite to dump data
    print("🔄 Dumping data from SQLite...")
    os.environ['DATABASE_URL'] = ''  # Force SQLite usage
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scouting_backend.settings')
    django.setup()
    
    from django.core.management import call_command
    
    # Dump data
    with open('data_dump.json', 'w') as f:
        call_command('dumpdata', '--natural-foreign', '--natural-primary', stdout=f)
    
    print("✅ Data dumped to data_dump.json")
    
    # Now switch to PostgreSQL and load data
    database_url = input("Enter your Supabase DATABASE_URL: ")
    os.environ['DATABASE_URL'] = database_url
    
    # Reload Django with PostgreSQL
    from importlib import reload
    from django.conf import settings
    reload(settings)
    
    print("🔄 Loading data into PostgreSQL...")
    call_command('loaddata', 'data_dump.json')
    
    print("✅ Migration complete!")
    print("🗑️  You can now delete db.sqlite3 and data_dump.json")

if __name__ == '__main__':
    main()