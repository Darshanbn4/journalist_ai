from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
import os
from pathlib import Path
from dotenv import load_dotenv

from models import NewsRequest
from utils import tts_to_audio, generate_news_urls_to_scrape, clean_html_to_text, extract_headlines

app = FastAPI()
load_dotenv()

def create_simple_news_script(topics, news_data=None, reddit_data=None):
    """Create a simple news script without AI when APIs are unavailable"""
    
    script = "Good evening, and welcome to your personalized news summary. "
    
    if len(topics) == 1:
        script += f"Today we're focusing on {topics[0]}. "
    else:
        script += f"Today we're covering {len(topics)} important topics. "
    
    for i, topic in enumerate(topics, 1):
        script += f"In story number {i}, we examine the latest developments in {topic}. "
        
        # Add any available news data
        if news_data and news_data.get("news_analysis", {}).get(topic):
            news_content = news_data["news_analysis"][topic]
            if not news_content.startswith("Error") and not news_content.startswith("Unable"):
                script += f"Recent reports indicate significant activity in {topic} research and development. "
        
        # Add any available reddit data
        if reddit_data and reddit_data.get("reddit_analysis", {}).get(topic):
            script += f"Online discussions show growing public interest in {topic}. "
        
        script += f"Experts continue to monitor trends and developments in the {topic} sector. "
    
    script += "That concludes today's news summary. Thank you for staying informed with NewsNinja."
    
    return script

@app.post("/generate-news-audio")
async def generate_news_audio(request: NewsRequest):
    try:
        print(f"Processing request for topics: {request.topics}")
        
        # Try to get some basic news data (without premium APIs)
        results = {}
        
        # For now, we'll create a basic script without scraping
        # You can enable scraping later when BrightData is configured
        
        # Generate a simple but informative script
        news_summary = create_simple_news_script(
            topics=request.topics,
            news_data=results.get("news", {}),
            reddit_data=results.get("reddit", {})
        )
        
        print(f"Generated script: {news_summary[:100]}...")

        # Use free gTTS for audio generation
        audio_path = tts_to_audio(
            text=news_summary,
            language='en'
        )

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
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "NewsNinja Fallback API is running"}

if __name__ == "__main__":
    import uvicorn
    print("🥷 Starting NewsNinja Fallback Server...")
    print("This version uses free alternatives and doesn't require premium API keys")
    uvicorn.run(
        "backend_fallback:app",
        host="0.0.0.0",
        port=1234,
        reload=True
    )