#!/usr/bin/env bash
# Deployment script for Koyeb

echo "🚀 Starting Enhanced AI Onboarding System deployment..."

# Create necessary directories
mkdir -p documents temp logs templates static/css static/js

# Initialize database if it doesn't exist
if [ ! -f "users.db" ]; then
    echo "📊 Initializing database..."
    python -c "
from models import UserManager
from file_manager import FileManager

# Initialize components
user_manager = UserManager()
file_manager = FileManager()

# Add demo users
user_manager.add_demo_users()
print('✓ Database initialized with demo users')
"
fi

echo "✅ Deployment preparation complete!"
