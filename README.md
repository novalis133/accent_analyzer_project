# Accent Analyzer Tool

This tool analyzes video URLs or uploaded files to determine the speaker's English accent using Azure Speech Services and Streamlit.

## Features
- 🎯 Analyzes English accent variants (American, British, Australian, etc.)
- 📊 Provides confidence scores (0-100%)
- 📝 Generates speech transcriptions
- 🌐 Supports multiple video platforms (YouTube, Loom, direct MP4, etc.)
- 📁 **NEW: Direct file upload support** for video and audio files
- 🎨 Modern, user-friendly Streamlit interface
- 🔍 Debug information and processing quality metrics

## How It Works

This application combines several powerful technologies:

1. **yt-dlp**: Downloads videos from various platforms and extracts audio
2. **FFmpeg**: Converts and standardizes audio to WAV format (16kHz, mono)
3. **Azure Speech Services**: 
   - Performs speech-to-text transcription
   - Detects language variants (en-US, en-GB, en-AU, etc.)
   - Provides confidence scores
4. **Custom Logic**: Maps Azure language codes to human-readable accent classifications

## Supported Input Methods

### 1. Video URLs
- YouTube videos
- Loom recordings
- Direct MP4/video links
- Most video platforms supported by yt-dlp

### 2. File Upload (NEW!)
- **Video formats:** MP4, MOV, AVI, MKV, WEBM
- **Audio formats:** WAV, MP3, M4A, OGG
- Maximum recommended size: 100MB
- Processed locally with ffmpeg

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- **FFmpeg installed and accessible in system PATH** (CRITICAL REQUIREMENT)
- Azure Speech Services subscription

### 2. Install FFmpeg (REQUIRED)
**⚠️ FFmpeg is absolutely required for both URL processing and file uploads**

**Windows:**
- Download from https://ffmpeg.org/download.html
- Extract and add to system PATH
- Test: Open Command Prompt and run `ffmpeg -version`

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Verify Installation:**
```bash
ffmpeg -version
```

### 3. Project Setup
```bash
# Clone/download this repository
cd accent-analyzer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Azure Credentials
1. Copy `env.example` to `.env`:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your Azure credentials:
   ```
   AZURE_SPEECH_KEY="your_azure_speech_key_here"
   AZURE_SPEECH_REGION="your_azure_region_here"
   ```

3. Get Azure Speech Services credentials:
   - Go to [Azure Portal](https://portal.azure.com)
   - Create a Speech Services resource
   - Copy the Key and Region from the resource

### 5. Run the Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Deployment

This application is designed to be deployed on **Streamlit Community Cloud**.

### Required Files for Deployment:
- `requirements.txt` - Python dependencies
- `packages.txt` - System packages (contains `ffmpeg`)
- All source code files (`app.py`, `video_utils.py`, etc.)

### Deployment Steps:

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [streamlit.io/cloud](https://streamlit.io/cloud)
   - Click "New app" → "Deploy from GitHub"
   - Select your repository and branch
   - Set main file: `app.py`
   - Configure secrets in Advanced Settings:
     - `AZURE_SPEECH_KEY`: Your Azure Speech API key
     - `AZURE_SPEECH_REGION`: Your Azure region (e.g., "eastus")

3. **Monitor Deployment:**
   - Watch build logs for any errors
   - Test thoroughly once deployed

### Secrets Configuration:
API keys (`AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`) must be configured in the Streamlit Cloud app settings under 'Secrets'. The application automatically detects whether it's running locally (uses `.env`) or deployed (uses `st.secrets`).

### Live Application:
*[Link to be filled in after deployment]*

## Usage Guide

### Option 1: Video URL Analysis
1. Paste a video URL in the "Video URL" field
2. Click "Analyze Accent"
3. Wait for processing and view results

### Option 2: File Upload Analysis
1. Click "Choose a video or audio file"
2. Select a supported file (MP4, WAV, MP3, etc.)
3. Click "Analyze Accent"
4. Wait for processing and view results

### Results Include:
- ✅ Accent classification (e.g., "American English", "British English")
- ✅ Confidence score (0-100%)
- ✅ Processing quality assessment
- ✅ Speech transcript
- ✅ Summary explanation
- ✅ Debug information (expandable)

## Testing

### Sample URLs for Testing:
1. **American Accent:** Any YouTube video with clear American English speech
2. **British Accent:** BBC news videos or UK content creators
3. **Australian Accent:** Australian news or content creators
4. **Loom Videos:** Any public Loom recording with English speech
5. **Direct MP4:** Any direct link to video file with English speech

### Sample Files for Testing:
1. **MP4 video files** with clear English speech
2. **WAV audio recordings** of conversations
3. **MP3 audio files** with different accents
4. **Large files** (test processing time and memory)
5. **Short clips** (test minimum duration handling)
6. **Non-English content** (test language detection)

### Expected Results:
- ✅ Accent classification
- ✅ Confidence score (0-100%)
- ✅ Processing quality rating
- ✅ Speech transcript
- ✅ Summary explanation

### Troubleshooting:
- **"FFmpeg not found"**: Ensure FFmpeg is installed and in PATH
- **"Azure credentials not found"**: Check your `.env` file (local) or Streamlit secrets (deployed)
- **"Failed to download video"**: Try a different video URL
- **"Failed to process uploaded file"**: Check file format and ffmpeg installation
- **Low confidence scores**: Try videos/files with clearer speech
- **Large file processing**: May take longer, be patient
- **Empty results**: Check if audio contains speech

## Project Structure
```
accent-analyzer/
├── app.py                     # Main Streamlit application
├── video_utils.py             # Video/audio processing (yt-dlp + ffmpeg)
├── azure_speech_client.py     # Azure Speech Services integration
├── accent_logic.py            # Accent classification logic
├── requirements.txt           # Python dependencies
├── packages.txt               # System packages (ffmpeg)
├── env.example               # Environment variables template
└── README.md                 # This file
```

## Technology Stack
- **Frontend:** Streamlit
- **Video Processing:** yt-dlp + FFmpeg
- **Audio Processing:** FFmpeg (direct subprocess calls)
- **Speech Analysis:** Azure Speech Services
- **Language:** Python 3.8+
- **Deployment:** Streamlit Community Cloud

## Performance Notes
- **File Upload:** Processed locally, faster for small files
- **URL Processing:** Requires download, may be slower
- **Large Files:** Processing time increases with file size
- **Azure Limits:** Subject to Azure Speech Services quotas 