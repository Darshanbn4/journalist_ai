#!/usr/bin/env python3
"""
Setup script for NewsNinja - News & Reddit Audio Summarizer
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = ['audio', '.kiro', '.kiro/settings']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_env_file():
    """Check if .env file exists and guide user"""
    if not Path('.env').exists():
        print("\n⚠️  .env file not found!")
        print("Please create a .env file based on .env.example with your API keys:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your API keys:")
        print("   - GEMINI_API_KEY (from Google AI Studio)")
        print("   - ELEVEN_API_KEY (from ElevenLabs)")
        print("   - BRIGHTDATA_API_KEY (from BrightData)")
        print("   - BRIGHTDATA_WEB_UNLOCKER_ZONE (from BrightData)")
        return False
    else:
        print("✓ .env file found")
        return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    print("✓ Dependencies installed")

def main():
    print("🥷 NewsNinja Setup")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Check environment file
    env_exists = check_env_file()
    
    # Install dependencies
    install_dependencies()
    
    print("\n🎉 Setup complete!")
    
    if env_exists:
        print("\n🚀 You can now run the application:")
        print("1. Backend: python backend.py")
        print("2. Frontend: streamlit run frontend.py")
    else:
        print("\n⚠️  Please configure your .env file before running the application")
    
    print("\n📖 Quick Start Guide:")
    print("1. Get API keys:")
    print("   - Gemini: https://aistudio.google.com/app/apikey")
    print("   - ElevenLabs: https://elevenlabs.io/app/settings/api-keys")
    print("   - BrightData: https://brightdata.com/")
    print("2. Configure .env file with your keys")
    print("3. Run: python backend.py (in one terminal)")
    print("4. Run: streamlit run frontend.py (in another terminal)")

if __name__ == "__main__":
    main()