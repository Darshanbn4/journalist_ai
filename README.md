# 🥷 NewsNinja - News & Reddit Audio Summarizer

A powerful tool that converts news articles and Reddit discussions into professional audio summaries using AI.

## 🌟 Features

- **Multi-Source Analysis**: Scrape news from Google News and discussions from Reddit
- **AI-Powered Summarization**: Uses Google Gemini to create professional broadcast-style summaries
- **High-Quality Audio**: Converts text to natural-sounding speech using ElevenLabs
- **Web Interface**: Clean Streamlit frontend for easy interaction
- **MCP Integration**: Model Context Protocol server for enhanced scraping capabilities

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **AI**: Google Gemini (Generative AI)
- **Audio**: ElevenLabs TTS
- **Scraping**: BrightData + MCP Server
- **Async**: aiolimiter, tenacity for robust operations

## 🚀 Quick Start

### 1. Setup
```bash
python setup.py
```

### 2. Configure Environment
Copy `.env.example` to `.env` and fill in your API keys:

```env
# Required API Keys
GEMINI_API_KEY=your_gemini_api_key_here
ELEVEN_API_KEY=your_elevenlabs_api_key_here

# BrightData Configuration
BRIGHTDATA_API_KEY=your_brightdata_api_key_here
BRIGHTDATA_WEB_UNLOCKER_ZONE=your_brightdata_zone_here

# MCP Configuration
API_TOKEN=your_brightdata_api_token_here
WEB_UNLOCKER_ZONE=your_brightdata_zone_here
```

### 3. Get API Keys

#### Google Gemini API
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy to `GEMINI_API_KEY` in your `.env`

#### ElevenLabs API
1. Visit [ElevenLabs API Keys](https://elevenlabs.io/app/settings/api-keys)
2. Create a new API key
3. Copy to `ELEVEN_API_KEY` in your `.env`

#### BrightData
1. Sign up at [BrightData](https://brightdata.com/)
2. Get your API key and Web Unlocker zone
3. Add to `.env` file

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
python backend.py
```

**Terminal 2 - Frontend:**
```bash
streamlit run frontend.py
```

### 5. Use the App
1. Open your browser to `http://localhost:8501`
2. Enter a topic (e.g., "Artificial Intelligence")
3. Select your data source (News, Reddit, or Both)
4. Click "Generate Summary"
5. Listen to your personalized news audio!

## 📁 Project Structure

```
NewsNinja/
├── backend.py              # FastAPI server
├── frontend.py             # Streamlit web interface
├── models.py               # Pydantic data models
├── news_scraper.py         # News scraping logic
├── reddit_scraper.py       # Reddit scraping with MCP
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
├── setup.py               # Setup script
├── .env.example           # Environment template
├── .kiro/settings/mcp.json # MCP server configuration
└── audio/                 # Generated audio files
```

## 🔧 Configuration

### MCP Server
The project includes MCP (Model Context Protocol) server configuration for enhanced Reddit scraping. The configuration is in `.kiro/settings/mcp.json`.

### Audio Settings
- **Voice**: Professional news anchor voice (JBFqnCBsd6RMkjVDRZzb)
- **Model**: ElevenLabs Multilingual v2
- **Format**: MP3, 44.1kHz, 128kbps

## 🐛 Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not configured"**
   - Make sure your `.env` file exists and contains valid API keys

2. **"Connection Error: Could not reach the backend server"**
   - Ensure the backend is running on port 1234
   - Check if `python backend.py` is running without errors

3. **"BrightData error"**
   - Verify your BrightData API key and zone configuration
   - Check your BrightData account limits

4. **Audio generation fails**
   - Verify your ElevenLabs API key
   - Check your ElevenLabs account credits

### Debug Mode
Run with debug logging:
```bash
FASTMCP_LOG_LEVEL=DEBUG python backend.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Gemini for AI summarization
- ElevenLabs for high-quality TTS
- BrightData for reliable web scraping
- Streamlit for the beautiful web interface