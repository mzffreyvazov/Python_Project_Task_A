#!/usr/bin/env python3
"""
Setup script for the Enhanced AI Onboarding System
"""

import os
import sys
import subprocess
from pathlib import Path


def create_directories():
    """Create necessary directories"""
    directories = [
        'templates',
        'static/css',
        'static/js',
        'documents',
        'temp',
        'logs'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ All packages installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True


def create_env_file():
    """Create .env file template"""
    env_content = """# Enhanced AI Onboarding System Configuration
# Copy this file to .env and update with your values

# Flask Configuration
SECRET_KEY=nazirlik_ai_secret_key_2025
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
DATABASE_PATH=users.db

# File Management
MAX_UPLOAD_SIZE=50MB
ALLOWED_EXTENSIONS=pdf,docx,xlsx,txt,md,html
"""

    if not os.path.exists('.env'):
        with open('.env.example', 'w') as f:
            f.write(env_content)
        print("✓ Created .env.example file")
    else:
        print("✓ .env file already exists")


def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")

    required_modules = [
        'flask',
        'google.generativeai',
        'PyPDF2',
        'docx',
        'openpyxl',
        'bs4',
        'markdown'
    ]

    failed_imports = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)

    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False

    print("✓ All modules imported successfully")
    return True


def create_sample_files():
    """Create sample document files for testing"""
    sample_dir = Path('sample_documents')
    sample_dir.mkdir(exist_ok=True)

    # Sample markdown file
    sample_md = """# Nazirlik Qaydaları

## İş Saatları
- Başlama: 09:00
- Bitmə: 18:00  
- Nahar fasiləsi: 13:00-14:00

## Məzuniyyət Qaydaları
İllik məzuniyyət hüququ 21 iş günüdür.

## Əlaqə Məlumatları
HR Şöbəsi: +994-12-555-0102
"""

    with open(sample_dir / 'nazirlik_qaydalar.md', 'w', encoding='utf-8') as f:
        f.write(sample_md)

    # Sample text file
    sample_txt = """Ezamiyyə Qaydaları

1. Ezamiyyə ərizəsi minimum 3 gün əvvəl təqdim edilməlidir
2. Günlük yemək pulu: 25 AZN
3. Yaşayış xərci: 50 AZN
4. Nəqliyyat xərci faktiki hesablanır

Əlaqə: Maliyyə Şöbəsi - samad.aliyev@nazirlik.gov.az
"""

    with open(sample_dir / 'ezamiyye_qaydalari.txt', 'w', encoding='utf-8') as f:
        f.write(sample_txt)

    print("✓ Created sample documents")


def main():
    """Main setup function"""
    print("🚀 Setting up Enhanced AI Onboarding System...\n")

    # Create directories
    create_directories()
    print()

    # Install requirements
    if not install_requirements():
        print("❌ Setup failed at package installation")
        return
    print()

    # Test imports
    if not test_imports():
        print("❌ Setup failed at import testing")
        return
    print()

    # Create env file
    create_env_file()
    print()

    # Create sample files
    create_sample_files()
    print()

    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your Gemini API key in .env file")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:5000")
    print("4. Login with: admin/admin123")
    print("5. Upload your documents in the Documents section")

    print("\n📁 File structure:")
    print("├── app.py              # Main Flask application")
    print("├── models.py           # Enhanced models with AI")
    print("├── file_manager.py     # Document processing system")
    print("├── config.py           # Configuration management")
    print("├── documents/          # Uploaded documents storage")
    print("├── sample_documents/   # Sample files for testing")
    print("└── templates/          # HTML templates")


if __name__ == '__main__':
    main()