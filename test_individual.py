#!/usr/bin/env python3
"""
Individual component testing for NewsNinja
"""

import os
from dotenv import load_dotenv

def test_gemini():
    """Test Gemini API"""
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ Please set your GEMINI_API_KEY in .env file")
        print("   Get it from: https://aistudio.google.com/app/apikey")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Test with a simple prompt using the free model
        model = genai.GenerativeModel('gemini-1.5-flash')  # Use flash model (free tier)
        response = model.generate_content("Say 'Hello from Gemini!'")
        print(f"✓ Gemini API working: {response.text}")
        return True
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "quota" in error_str.lower():
            print("⚠️ Gemini API quota exceeded. Try again later or check your billing.")
            print("   You can also try using the free gTTS fallback for now.")
        elif "403" in error_str:
            print("❌ Gemini API key invalid or expired")
        else:
            print(f"❌ Gemini API error: {error_str}")
        return False

def test_elevenlabs():
    """Test ElevenLabs API"""
    load_dotenv()
    api_key = os.getenv('ELEVEN_API_KEY')
    
    if not api_key or api_key == 'your_elevenlabs_api_key_here':
        print("❌ Please set your ELEVEN_API_KEY in .env file")
        print("   Get it from: https://elevenlabs.io/app/settings/api-keys")
        return False
    
    try:
        from elevenlabs import ElevenLabs
        client = ElevenLabs(api_key=api_key)
        
        # Test by getting available voices
        voices = client.voices.get_all()
        print(f"✓ ElevenLabs API working: Found {len(voices.voices)} voices")
        return True
    except Exception as e:
        error_str = str(e)
        if "401" in error_str or "invalid_api_key" in error_str:
            print("❌ ElevenLabs API key is invalid")
            print("   Please check your API key at: https://elevenlabs.io/app/settings/api-keys")
        elif "403" in error_str:
            print("❌ ElevenLabs API access forbidden - check your account status")
        elif "429" in error_str:
            print("⚠️ ElevenLabs API rate limit exceeded - try again later")
        else:
            print(f"❌ ElevenLabs API error: {error_str}")
        return False

def test_basic_functionality():
    """Test basic functionality without external APIs"""
    print("🧪 Testing Basic Functionality...")
    
    # Test news URL generation
    from utils import generate_news_urls_to_scrape
    urls = generate_news_urls_to_scrape(["test topic"])
    print(f"✓ News URL generation: {urls}")
    
    # Test HTML cleaning
    from utils import clean_html_to_text
    test_html = "<html><body><h1>Test</h1><p>Content</p></body></html>"
    clean_text = clean_html_to_text(test_html)
    print(f"✓ HTML cleaning: {clean_text[:50]}...")
    
    return True

def main():
    print("🥷 NewsNinja Individual Component Test")
    print("=" * 50)
    
    # Test basic functionality first
    test_basic_functionality()
    
    print("\n🔑 API Testing...")
    print("-" * 30)
    
    # Test APIs
    gemini_ok = test_gemini()
    elevenlabs_ok = test_elevenlabs()
    
    print("\n📊 Results:")
    print(f"Gemini API: {'✓' if gemini_ok else '❌'}")
    print(f"ElevenLabs API: {'✓' if elevenlabs_ok else '❌'}")
    
    if gemini_ok and elevenlabs_ok:
        print("\n🎉 All APIs working! You can now run the full application:")
        print("1. python backend.py")
        print("2. streamlit run frontend.py")
    else:
        print("\n⚠️  Please configure your API keys in .env file")
        print("   Copy the keys from the respective websites and replace the placeholder values")

if __name__ == "__main__":
    main()