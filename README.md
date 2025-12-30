# FRC Scouting System

A dynamic, production-ready scouting system for FIRST Robotics Competition (FRC) built with Django and modern JavaScript.

## Features

- **Dynamic Configuration System**: Change game metrics without code changes via `game_config.json`
- **Hot-Reload**: Config changes apply instantly without server restart
- **Google OAuth Authentication**: Secure login with team Google accounts
- **Admin Panel**: User management, scout leaderboard, and match data editor
- **QR Code Scanner**: Fast data collection from scouting sheets
- **Strategy Dashboard**: Real-time match analysis and team rankings
- **Pit Scouting**: Dynamic forms generated from configuration
- **Legacy Key Support**: Rename metrics mid-season without losing historical data

## Tech Stack

- **Backend**: Django 5.1, PostgreSQL
- **Frontend**: Vanilla JavaScript, Webpack
- **Authentication**: Google OAuth 2.0
- **Hosting**: Self-hosted Ubuntu VM
- **Storage**: Cloudinary (images), PostgreSQL (data)

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- PostgreSQL database
- Google Cloud OAuth credentials
- Cloudinary account (for image uploads)
- The Blue Alliance API key

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-org/scouting-backend-2025.git
cd scouting-backend-2025
```

### 2. Environment Setup

Copy the example environment file and fill in your credentials:

```bash
cp env.txt .env
```

Edit `.env` with your credentials:

```env
DATABASE_URL=postgresql://user:password@host:port/database
X_TBA_AUTH_KEY=your_tba_api_key
CLOUD_NAME=your_cloudinary_name
CLOUD_API_KEY=your_cloudinary_key
CLOUD_API_SECRET=your_cloudinary_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SECRET_KEY=your_secret_key_here
DEBUG=True
```

Generate a secure SECRET_KEY:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

### 4. Build Frontend Assets

```bash
npm run build
```

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create first admin user (via Django shell)
python manage.py shell
```

In the shell:
- Note of course that it is not strictly bound to Team2073 and any emails can be used
```python
from authenticate.models import AuthorizedUser
AuthorizedUser.objects.create(email='your-email@team2073.com')
exit()
```

### 6. Collect Static Files

```bash
python manage.py collectstatic --no-input
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` and log in with Google OAuth.

## Production Deployment

### Self-Hosted on Ubuntu VM

This system is designed to run on a self-hosted Ubuntu server.

**Initial Setup:**

1. Install system dependencies:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm postgresql nginx
```

2. Clone and setup:
```bash
git clone https://github.com/your-org/scouting-backend-2025.git
cd scouting-backend-2025
cp env.txt .env
# Edit .env with your credentials
```

3. Run build script:
```bash
chmod +x build.sh
./build.sh
```

4. Create systemd service for auto-start:
```bash
sudo nano /etc/systemd/system/scouting.service
```

Add:
```ini
[Unit]
Description=FRC Scouting System
After=network.target postgresql.service

[Service]
User=your-username
WorkingDirectory=/path/to/scouting-backend-2025
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 manage.py runserver 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

5. Enable and start service:
```bash
sudo systemctl enable scouting
sudo systemctl start scouting
sudo systemctl status scouting
```

**Using Gunicorn (Recommended for Production):**

1. Install gunicorn:
```bash
pip install gunicorn
```

2. Update systemd service ExecStart:
```ini
ExecStart=/usr/local/bin/gunicorn scouting_backend.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

3. Setup Nginx reverse proxy:
```bash
sudo nano /etc/nginx/sites-available/scouting
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/scouting-backend-2025/staticfiles/;
    }
}
```

4. Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/scouting /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Updating the Application:**

```bash
cd /path/to/scouting-backend-2025
git pull
./build.sh
sudo systemctl restart scouting
```

### Environment Variables

Set these in your `.env` file:

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Django secret key (keep secure!)
- `DEBUG` - Set to `False` in production
- `GOOGLE_CLIENT_ID` - OAuth client ID
- `GOOGLE_CLIENT_SECRET` - OAuth client secret
- `X_TBA_AUTH_KEY` - The Blue Alliance API key
- `CLOUD_NAME`, `CLOUD_API_KEY`, `CLOUD_API_SECRET` - Cloudinary credentials

## Configuration

### Game Configuration

Edit `game_config.json` to customize for each season:

```json
{
  "version": "2025_reefscape",
  "home_team": 2073,
  "year": 2025,
  "metrics": [
    {
      "key": "auto_leave",
      "type": "number",
      "category": "auto",
      "aggregation": "avg",
      "display_name": "Auto Leave",
      "min": 0,
      "max": 1
    }
  ],
  "pit_questions": [...]
}
```

Changes apply immediately without restart (hot-reload).

### Renaming Metrics

To rename a metric without losing data, add `legacy_keys`:

```json
{
  "key": "endgame_climb",
  "legacy_keys": ["climb", "old_climb"],
  "type": "number",
  ...
}
```

## Admin Panel

Access at `/admin-panel/` after logging in.

**Features:**
- Add/remove authorized users
- View scout leaderboard by competition
- Edit match data (fix typos, correct values)

## Project Structure

```
scouting-backend-2025/
├── api/                    # The Blue Alliance API integration
├── authenticate/           # OAuth login, user management, admin panel
├── frontend/               # JavaScript source files (Webpack)
├── scanner/                # QR code scanning views
├── scouting_backend/       # Django project settings
├── strategy/               # Rankings, dashboard, picklist
├── teams/                  # Team pages, pit scouting
├── templates/              # Base HTML templates
├── game_config.json        # Dynamic game configuration
├── utils.py                # Config loader with hot-reload
├── constants.py            # Hardcoded admin emails
├── build.sh                # Production build script
└── requirements.txt        # Python dependencies
```

## Development

### Frontend Development

```bash
# Watch mode (auto-rebuild on changes)
npm run watch

# Development server with hot reload
npm run dev

# Lint JavaScript
npm run lint

# Format code
npm run format
```

### Database Migrations

```bash
# Create migration after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Adding Authorized Users

Via admin panel at `/admin-panel/` or Django shell:

```python
from authenticate.models import AuthorizedUser
AuthorizedUser.objects.create(email='user@team2073.com')
```

## Troubleshooting

### Database Connection Issues

If using Supabase or cloud PostgreSQL without IPv4:
- Use connection pooler URL
- Or run migrations locally with local PostgreSQL

### OAuth Redirect URI Mismatch

Ensure your Google Cloud Console has these redirect URIs:
- `http://localhost:8000/auth/oauth2callback/` (development)
- `https://your-domain.com/auth/oauth2callback/` (production)

### Static Files Not Loading

```bash
python manage.py collectstatic --no-input
```

Ensure `STATIC_ROOT` is set in `settings.py`.

## Documentation

- [Configuration Guide](CONFIG_GUIDE.md) - Complete guide to creating game configurations
- [Phase 4 Complete](PHASE4_COMPLETE.md) - Final implementation summary

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Team

Developed by FRC Team 2073 EagleForce

## Support

For issues or questions:
- Open a GitHub issue
- Contact team leadership
- Check documentation links above
