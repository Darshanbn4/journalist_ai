#!/usr/bin/env python3
"""
Test NewsNinja with free fallback options
"""

import os
from dotenv import load_dotenv

def test_gtts_fallback():
    """Test Google Text-to-Speech fallback"""
    print("🔊 Testing gTTS (Free Text-to-Speech)...")
    
    try:
        from utils import tts_to_audio
        
        # Test with a simple text
        test_text = "Hello, this is a test of the free text-to-speech system."
        audio_path = tts_to_audio(test_text)
        
        if audio_path and os.path.exists(audio_path):
            print(f"✓ gTTS working: Audio saved to {audio_path}")
            return True
        else:
            print("❌ gTTS failed to create audio file")
            return False
    except Exception as e:
        print(f"❌ gTTS error: {str(e)}")
        return False

def test_basic_news_processing():
    """Test basic news processing without premium APIs"""
    print("📰 Testing Basic News Processing...")
    
    try:
        from utils import generate_news_urls_to_scrape, clean_html_to_text, extract_headlines
        
        # Test URL generation
        topics = ["artificial intelligence"]
        urls = generate_news_urls_to_scrape(topics)
        print(f"✓ Generated URLs: {list(urls.keys())}")
        
        # Test HTML processing with sample data
        sample_html = """
        <html>
        <body>
        <h1>AI Breakthrough in 2024</h1>
        <p>Scientists announce major advancement</p>
        <h2>Tech Giants Invest Billions</h2>
        <p>Major investment in AI research</p>
        More
        <h3>Future of Work</h3>
        <p>How AI will change employment</p>
        More
        </body>
        </html>
        """
        
        clean_text = clean_html_to_text(sample_html)
        headlines = extract_headlines(clean_text)
        
        print(f"✓ Extracted headlines: {headlines[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Basic processing error: {str(e)}")
        return False

def create_simple_news_script():
    """Create a simple news script without AI"""
    print("📝 Testing Simple News Script Generation...")
    
    try:
        # Simple template-based news script
        topics = ["Artificial Intelligence", "Climate Change"]
        
        script = "Good evening, here are today's top stories. "
        
        for i, topic in enumerate(topics, 1):
            script += f"In story number {i}, we're covering developments in {topic}. "
            script += f"Experts are closely monitoring the latest trends in {topic} research and policy. "
        
        script += "That concludes our news summary for today. Thank you for listening."
        
        print(f"✓ Generated script: {script[:100]}...")
        
        # Test with gTTS
        from utils import tts_to_audio
        audio_path = tts_to_audio(script)
        
        if audio_path and os.path.exists(audio_path):
            print(f"✓ Audio created: {audio_path}")
            return True
        else:
            print("❌ Failed to create audio")
            return False
            
    except Exception as e:
        print(f"❌ Script generation error: {str(e)}")
        return False

def main():
    print("🥷 NewsNinja Fallback Test (Free Options)")
    print("=" * 50)
    
    print("This test uses only free services and doesn't require premium API keys.\n")
    
    # Test components
    tests = [
        ("Basic News Processing", test_basic_news_processing),
        ("Free Text-to-Speech (gTTS)", test_gtts_fallback),
        ("Simple News Script", create_simple_news_script)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 Fallback Test Results")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All fallback options working!")
        print("\n🚀 You can run a basic version of NewsNinja:")
        print("1. Use gTTS for text-to-speech (free)")
        print("2. Use simple template-based scripts")
        print("3. Basic news URL generation works")
        
        print("\n💡 To upgrade:")
        print("- Fix your Gemini API key for better AI summaries")
        print("- Fix your ElevenLabs API key for professional voice")
    else:
        print(f"⚠️  {passed}/{total} fallback tests passed")
        print("Some basic functionality may not work properly")

if __name__ == "__main__":
    main()