from fastapi import FastAPI, HTTPException, File, Response
from fastapi.responses import FileResponse
import os
from pathlib import Path
from dotenv import load_dotenv

from models import NewsRequest
from utils import generate_broadcast_news, text_to_audio_elevenlabs_sdk, tts_to_audio
from news_scraper import NewsScraper
from reddit_scraper import scrape_reddit_topics

app = FastAPI()
load_dotenv()


@app.post("/generate-news-audio")
async def generate_news_audio(request: NewsRequest):
    try:
        # Validate API keys
        if not os.getenv("GEMINI_API_KEY"):
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        if not os.getenv("ELEVEN_API_KEY"):
            raise HTTPException(status_code=500, detail="ELEVEN_API_KEY not configured")
            
        results = {}
        
        # Scrape news if requested
        if request.source_type in ["news", "both"]:
            try:
                news_scraper = NewsScraper()
                results["news"] = await news_scraper.scrape_news(request.topics)
            except Exception as e:
                print(f"News scraping failed: {str(e)}")
                results["news"] = {"news_analysis": {topic: f"News unavailable for {topic}" for topic in request.topics}}
        
        # Scrape Reddit if requested
        if request.source_type in ["reddit", "both"]:
            try:
                results["reddit"] = await scrape_reddit_topics(request.topics)
            except Exception as e:
                print(f"Reddit scraping failed: {str(e)}")
                results["reddit"] = {"reddit_analysis": {topic: f"Reddit discussions unavailable for {topic}" for topic in request.topics}}

        # Generate news summary
        news_data = results.get("news", {})
        reddit_data = results.get("reddit", {})
        
        if not news_data and not reddit_data:
            raise HTTPException(status_code=500, detail="No data sources available")
            
        news_summary = generate_broadcast_news(
            api_key=os.getenv("GEMINI_API_KEY"),
            news_data=news_data,
            reddit_data=reddit_data,
            topics=request.topics
        )

        if not news_summary or len(news_summary.strip()) < 10:
            raise HTTPException(status_code=500, detail="Failed to generate meaningful content")

        # Generate audio - try ElevenLabs first, fallback to gTTS
        audio_path = None
        
        # Create topic name for filename
        topic_name = "_".join(request.topics) if len(request.topics) <= 3 else f"{len(request.topics)}_topics"
        
        # Try ElevenLabs first
        if os.getenv("ELEVEN_API_KEY") and os.getenv("ELEVEN_API_KEY") != 'your_elevenlabs_api_key_here':
            try:
                audio_path = text_to_audio_elevenlabs_sdk(
                    text=news_summary,
                    voice_id="JBFqnCBsd6RMkjVDRZzb",
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128",
                    output_dir="audio",
                    topic_name=topic_name
                )
                print("✓ Used ElevenLabs for audio generation")
            except Exception as e:
                print(f"ElevenLabs failed: {str(e)}, falling back to gTTS")
                audio_path = None
        
        # Fallback to gTTS if ElevenLabs fails
        if not audio_path:
            try:
                audio_path = tts_to_audio(text=news_summary, language='en', topic_name=topic_name)
                print("✓ Used gTTS for audio generation")
            except Exception as e:
                print(f"gTTS also failed: {str(e)}")
                raise HTTPException(status_code=500, detail="Both audio services failed")

        if audio_path and Path(audio_path).exists():
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            return Response(
                content=audio_bytes,
                media_type="audio/mpeg",
                headers={"Content-Disposition": "attachment; filename=news-summary.mp3"}
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate audio file")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=1234,
        reload=True
    )