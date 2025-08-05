# Nazirlik AI Onboarding System - Production Deployment

## Environment Variables Required for Koyeb

### Required
- `SECRET_KEY`: Your Flask secret key for sessions (generate a secure one)
- `GEMINI_API_KEY`: Your Google Gemini API key

### Optional (with defaults)
- `FLASK_DEBUG`: Set to "False" for production
- `DATABASE_PATH`: SQLite database path (default: users.db)

## Demo Accounts
After deployment, you can login with these demo accounts:

- **Admin**: `admin` / `admin123`
- **Minister**: `nazir` / `nazir123`  
- **Analyst**: `analitik` / `data123`

## Features
- 🤖 AI-powered onboarding assistant using Gemini 2.5 Flash
- 📁 Document management system
- 🔍 Smart document search
- 👥 Role-based access control
- 📊 File statistics and management
- 🔒 Secure authentication system

## Production Notes
- Database: SQLite (persisted on Koyeb)
- File storage: Local filesystem (persisted on Koyeb)
- AI Model: Google Gemini 2.5 Flash
- Web server: Gunicorn

## Health Check
The application responds to health checks at the root URL `/`
