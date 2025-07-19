from urllib.parse import quote_plus
from dotenv import load_dotenv
import requests
import os
from fastapi import FastAPI, HTTPException
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
from elevenlabs import ElevenLabs

load_dotenv()


class MCPOverloadedError(Exception):
    """Custom exception for MCP service overloads"""
    pass


def generate_valid_news_url(keyword: str) -> str:
    """
    Generate a Google News search URL for a keyword with optional sorting by latest
    
    Args:
        keyword: Search term to use in the news search
        
    Returns:
        str: Constructed Google News search URL
    """
    q = quote_plus(keyword)
    return f"https://news.google.com/search?q={q}&tbs=sbd:1"


def generate_news_urls_to_scrape(list_of_keywords):
    valid_urls_dict = {}
    for keyword in list_of_keywords:
        valid_urls_dict[keyword] = generate_valid_news_url(keyword)
    
    return valid_urls_dict


def scrape_with_brightdata(url: str) -> str:
    """Scrape a URL using BrightData MCP server or fallback to direct API"""
    try:
        # Try using MCP server first (if available)
        # This would be handled by the MCP integration in the calling code
        # For now, fallback to direct API call
        headers = {
            "Authorization": f"Bearer {os.getenv('BRIGHTDATA_API_KEY')}",
            "Content-Type": "application/json"
        }

        payload = {
            "zone": os.getenv('BRIGHTDATA_WEB_UNLOCKER_ZONE'),
            "url": url,
            "format": "raw"
        }
        
        response = requests.post("https://api.brightdata.com/request", json=payload, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"BrightData error: {str(e)}")


def clean_html_to_text(html_content: str) -> str:
    """Clean HTML content to plain text"""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator="\n")
    return text.strip()


def extract_headlines(cleaned_text: str) -> str:
    """
    Extract and concatenate headlines from cleaned news text content.
    
    Args:
        cleaned_text: Raw text from news page after HTML cleaning
        
    Returns:
        str: Combined headlines separated by newlines
    """
    headlines = []
    current_block = []
    
    # Split text into lines and remove empty lines
    lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
    
    # Process lines to find headline blocks
    for line in lines:
        if line == "More":
            if current_block:
                # First line of block is headline
                headlines.append(current_block[0])
                current_block = []
        else:
            current_block.append(line)
    
    # Add any remaining block at end of text
    if current_block:
        headlines.append(current_block[0])
    
    return "\n".join(headlines)


def summarize_with_ollama(headlines) -> str:
    """Summarize content using Ollama (fallback option - requires ollama to be installed)"""
    try:
        import ollama
        prompt = f"""You are my personal news editor. Summarize these headlines into a TV news script for me, focus on important headlines and remember that this text will be converted to audio:
        So no extra stuff other than text which the podcaster/newscaster should read, no special symbols or extra information in between and of course no preamble please.
        {headlines}
        News Script:"""

        client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        
        # Generate response using the Ollama client
        response = client.generate(
            model="llama3.2",
            prompt=prompt,
            options={
                "temperature": 0.4,
                "max_tokens": 800
            },
            stream=False
        )
        
        return response['response']
    except ImportError:
        raise HTTPException(status_code=500, detail="Ollama not installed. Please use Gemini instead.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")


def generate_broadcast_news(api_key, news_data, reddit_data, topics):
    # Updated system message with flexible source handling
    system_prompt = """
    You are broadcast_news_writer, a professional virtual news reporter. Generate natural, TTS-ready news reports.

    IMPORTANT: Even if specific current data is unavailable, you should create informative content about the topics based on your general knowledge.

    For each topic, create a professional news segment that includes:
    1. Current relevance and importance of the topic
    2. Key developments and trends in the field
    3. Why this topic matters to listeners
    4. Future outlook or implications

    If specific current data is provided, incorporate it. If not, use your knowledge to create valuable content.

    Formatting rules:
    - ALWAYS start directly with the content, NO INTRODUCTIONS
    - Keep audio length 60-120 seconds per topic
    - Use natural speech transitions between topics
    - Maintain professional, informative tone
    - End with "This concludes our coverage of [topic]"
    - Write in full paragraphs optimized for speech synthesis
    - Avoid markdown or special characters
    """

    try:
        # Check if we have any real data
        has_real_data = False
        topic_blocks = []
        
        for topic in topics:
            news_content = news_data.get("news_analysis", {}).get(topic) if news_data else ''
            reddit_content = reddit_data.get("reddit_analysis", {}).get(topic) if reddit_data else ''
            
            # Check if we have meaningful content (not error messages)
            has_news = news_content and not any(x in news_content.lower() for x in ['error', 'unavailable', 'unable to fetch'])
            has_reddit = reddit_content and not any(x in reddit_content.lower() for x in ['error', 'unavailable', 'unable to fetch'])
            
            context = []
            if has_news:
                context.append(f"CURRENT NEWS:\n{news_content}")
                has_real_data = True
            if has_reddit:
                context.append(f"ONLINE DISCUSSIONS:\n{reddit_content}")
                has_real_data = True
            
            # Always include the topic, even without current data
            topic_info = f"TOPIC: {topic}\n\n"
            if context:
                topic_info += "\n\n".join(context)
            else:
                topic_info += f"Create an informative news segment about {topic} based on general knowledge and current relevance."
            
            topic_blocks.append(topic_info)

        if has_real_data:
            user_prompt = (
                "Create broadcast segments for these topics using the provided current information:\n\n" +
                "\n\n--- NEW TOPIC ---\n\n".join(topic_blocks)
            )
        else:
            user_prompt = (
                f"Create professional news segments about these topics: {', '.join(topics)}. "
                "Even though current specific data isn't available, provide informative content about each topic's "
                "current relevance, recent developments, and why it matters. Make it sound like a real news broadcast."
            )

        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Try different models in order of preference (flash is free tier)
        models_to_try = ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.5-pro']
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                
                # Add generation config to be more conservative with API usage
                generation_config = {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1000,
                }
                
                response = model.generate_content(full_prompt, generation_config=generation_config)
                return response.text
            except Exception as model_error:
                print(f"Model {model_name} failed: {str(model_error)}")
                if "429" in str(model_error) or "quota" in str(model_error).lower():
                    continue  # Try next model
                else:
                    continue  # Try next model for any error
        
        # If all models fail, create a basic fallback
        print("All Gemini models failed, using fallback script")
        fallback_script = create_fallback_script(topics)
        return fallback_script

    except Exception as e:
        # Final fallback if everything fails
        return create_fallback_script(topics)

def create_fallback_script(topics):
    """Create a basic news script when AI fails"""
    script = "Good evening, and welcome to your personalized news briefing. "
    
    for i, topic in enumerate(topics, 1):
        script += f"In our {['first', 'second', 'third', 'fourth', 'fifth'][i-1] if i <= 5 else str(i)} story today, we focus on {topic}. "
        script += f"This topic continues to be of significant importance in today's rapidly evolving landscape. "
        script += f"Industry experts and researchers are actively monitoring developments in {topic}, "
        script += f"as it represents a key area of innovation and public interest. "
        script += f"The implications of advances in {topic} extend across multiple sectors, "
        script += f"affecting both policy makers and the general public. "
        script += f"This concludes our coverage of {topic}. "
    
    script += "Thank you for staying informed with NewsNinja. We'll continue to bring you the latest updates on these important topics."
    
    return script


def summarize_with_gemini_news_script(api_key: str, headlines: str) -> str:
    """
    Summarize multiple news headlines into a TTS-friendly broadcast news script using Gemini.
    """
    system_prompt = """
You are my personal news editor and scriptwriter for a news podcast. Your job is to turn raw headlines into a clean, professional, and TTS-friendly news script.

The final output will be read aloud by a news anchor or text-to-speech engine. So:
- Do not include any special characters, emojis, formatting symbols, or markdown.
- Do not add any preamble or framing like "Here's your summary" or "Let me explain".
- Write in full, clear, spoken-language paragraphs.
- Keep the tone formal, professional, and broadcast-style — just like a real TV news script.
- Focus on the most important headlines and turn them into short, informative news segments that sound natural when spoken.
- Start right away with the actual script, using transitions between topics if needed.

Remember: Your only output should be a clean script that is ready to be read out loud.
"""

    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        full_prompt = f"{system_prompt}\n\nHeadlines to summarize:\n{headlines}"
        response = model.generate_content(full_prompt)
        
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")


def text_to_audio_elevenlabs_sdk(
    text: str,
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb",
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
    output_dir: str = "audio",
    api_key: str = None,
    topic_name: str = None
) -> str:
    """
    Converts text to speech using ElevenLabs SDK and saves it to audio/ directory.

    Returns:
        str: Path to the saved audio file.
    """
    try:
        api_key = api_key or os.getenv("ELEVEN_API_KEY")
        if not api_key:
            raise ValueError("ElevenLabs API key is required.")

        # Initialize client
        client = ElevenLabs(api_key=api_key)

        # Get the audio generator
        audio_stream = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format
        )

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename based on topic or timestamp
        if topic_name:
            # Clean topic name for filename (remove special characters)
            clean_topic = "".join(c for c in topic_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_topic = clean_topic.replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{clean_topic}_{timestamp}.mp3"
        else:
            filename = f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        
        filepath = os.path.join(output_dir, filename)

        # Write audio chunks to file
        with open(filepath, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        return filepath

    except Exception as e:
        raise e

from pathlib import Path
from gtts import gTTS
AUDIO_DIR = Path("audio")
AUDIO_DIR.mkdir(exist_ok=True)  # Create directory if it doesn't exist
def tts_to_audio(text: str, language: str = 'en', topic_name: str = None) -> str:
    """
    Convert text to speech using gTTS (Google Text-to-Speech) and save to file.
    
    Args:
        text: Input text to convert
        language: Language code (default: 'en')
        topic_name: Optional topic name for filename
    
    Returns:
        str: Path to saved audio file
    
    Example:
        tts_to_audio("Hello world", "en", "AI_News")
    """
    try:
        # Generate filename based on topic or timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if topic_name:
            # Clean topic name for filename (remove special characters)
            clean_topic = "".join(c for c in topic_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_topic = clean_topic.replace(' ', '_')
            filename = AUDIO_DIR / f"{clean_topic}_{timestamp}.mp3"
        else:
            filename = AUDIO_DIR / f"tts_{timestamp}.mp3"
        
        # Create TTS object and save
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(str(filename))
        
        return str(filename)
    except Exception as e:
        print(f"gTTS Error: {str(e)}")
        return None