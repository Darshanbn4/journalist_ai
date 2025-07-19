#!/usr/bin/env python3
"""
Test script to verify NewsNinja setup
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_environment():
    """Test environment variables"""
    load_dotenv()
    
    required_vars = [
        'GEMINI_API_KEY',
        'ELEVEN_API_KEY',
        'BRIGHTDATA_API_KEY',
        'BRIGHTDATA_WEB_UNLOCKER_ZONE'
    ]
    
    print("🔍 Testing Environment Variables...")
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * (len(value) - 4) + value[-4:]}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def test_imports():
    """Test if all required packages can be imported"""
    print("\n📦 Testing Package Imports...")
    
    packages = [
        ('fastapi', 'FastAPI'),
        ('streamlit', 'Streamlit'),
        ('google.generativeai', 'Google Generative AI'),
        ('elevenlabs', 'ElevenLabs'),
        ('requests', 'Requests'),
        ('bs4', 'BeautifulSoup4'),
        ('aiolimiter', 'AsyncLimiter'),
        ('tenacity', 'Tenacity'),
        ('pydantic', 'Pydantic'),
        ('dotenv', 'Python-dotenv')
    ]
    
    failed_imports = []
    
    for package, name in packages:
        try:
            __import__(package.split('.')[0])
            print(f"✓ {name}")
        except ImportError:
            print(f"❌ {name}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

def test_directories():
    """Test if required directories exist"""
    print("\n📁 Testing Directories...")
    
    directories = ['audio', '.kiro', '.kiro/settings']
    missing_dirs = []
    
    for directory in directories:
        if Path(directory).exists():
            print(f"✓ {directory}")
        else:
            print(f"❌ {directory}")
            missing_dirs.append(directory)
    
    return len(missing_dirs) == 0

def test_files():
    """Test if required files exist"""
    print("\n📄 Testing Files...")
    
    files = [
        '.env',
        'requirements.txt',
        '.kiro/settings/mcp.json',
        'backend.py',
        'frontend.py'
    ]
    
    missing_files = []
    
    for file in files:
        if Path(file).exists():
            print(f"✓ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    return len(missing_files) == 0

def test_api_connections():
    """Test basic API connections (without making actual calls)"""
    print("\n🌐 Testing API Configuration...")
    
    load_dotenv()
    
    success_count = 0
    
    # Test Gemini
    try:
        import google.generativeai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key != 'your_gemini_api_key_here':
            genai.configure(api_key=api_key)
            print("✓ Gemini API configured")
            success_count += 1
        else:
            print("❌ Gemini API key missing or not configured")
    except Exception as e:
        print(f"❌ Gemini API error: {str(e)}")
    
    # Test ElevenLabs
    try:
        from elevenlabs import ElevenLabs
        api_key = os.getenv('ELEVEN_API_KEY')
        if api_key and api_key != 'your_elevenlabs_api_key_here':
            client = ElevenLabs(api_key=api_key)
            print("✓ ElevenLabs API configured")
            success_count += 1
        else:
            print("❌ ElevenLabs API key missing or not configured")
    except Exception as e:
        print(f"❌ ElevenLabs API error: {str(e)}")
    
    return success_count >= 2

def main():
    print("🥷 NewsNinja Setup Test")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Package Imports", test_imports),
        ("Directories", test_directories),
        ("Files", test_files),
        ("API Configuration", test_api_connections)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result if result is not None else False)
        except Exception as e:
            print(f"❌ {test_name} failed with error: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 Next steps:")
        print("1. Run: python backend.py")
        print("2. Run: streamlit run frontend.py")
        print("3. Open: http://localhost:8501")
    else:
        print(f"⚠️  {passed}/{total} tests passed. Please fix the issues above.")
        
        if not results[0]:  # Environment test failed
            print("\n💡 Quick fix for environment variables:")
            print("1. Copy .env.example to .env")
            print("2. Fill in your API keys")
        
        if not results[1]:  # Import test failed
            print("\n💡 Quick fix for missing packages:")
            print("Run: pip install -r requirements.txt")

if __name__ == "__main__":
    main()