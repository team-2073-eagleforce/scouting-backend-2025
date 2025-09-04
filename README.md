# Scouting Backend 2025

Django-based scouting application with Google OAuth authentication.

## Setup

### 1. Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Google+ API (APIs & Services → Library)
4. Create OAuth 2.0 credentials (APIs & Services → Credentials)
5. Add redirect URIs:
   - `http://localhost:8000/auth/oauth2callback`
   - `http://127.0.0.1:8000/auth/oauth2callback`
   - Your production URLs
6. Add JavaScript origins:
   - `http://localhost:8000`
   - `http://127.0.0.1:8000`
   - Your production URLs

### 2. Environment Variables
Create `.env` file:
```
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
SECRET_KEY=your_django_secret_key
DATABASE_URL=your_database_url
```

### 3. Database Setup
```bash
python manage.py makemigrations authenticate
python manage.py migrate
python manage.py setup_admin  # Migrates users from constants.py
python manage.py createsuperuser  # For Django admin access
```

## User Management

### Access Levels
- **Authorized Users**: Full access, can manage other users via `/admin/`
- **Team2073 Members**: View-only access to testing competitions only
- **Others**: Blocked

### Managing Users
1. Go to `/admin/` with superuser account
2. Navigate to "Authorized users"
3. Add/remove users as needed

### User Permissions
**Authorized Users can:**
- Access all competitions
- Submit data (QR scanner, pit scouting, etc.)
- View and modify picklist
- Manage other authorized users

**Team2073 Members can:**
- View teams, rankings, dashboard in testing only
- View picklist (read-only)
- Cannot submit any data or access real competitions

## OAuth Publishing
If app is in testing mode, add test users in Google Cloud Console → OAuth consent screen → Test users.

For production, submit app for verification or keep in testing mode with approved users.

## Documentation
[Detailed docs](https://docs.google.com/document/d/1j8sGcgMbEVxCqPeh8ryBpwavfzDKIEpoXyBpnNdTXAw/edit?usp=sharing)