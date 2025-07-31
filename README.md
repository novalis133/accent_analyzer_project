# Accent Analyzer Tool

*A Streamlit-based tool for analyzing English accents in videos or audio files using Azure Speech Services.*

This repository provides a user-friendly tool for detecting English accent variants (e.g., American, British, Australian) in video URLs or uploaded files. It integrates Azure Speech Services for speech-to-text and accent detection, yt-dlp for video downloading, and FFmpeg for audio processing, making it ideal for linguists, educators, and developers.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/) 
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/) 
[![Azure](https://img.shields.io/badge/Azure_Speech-0089D6?logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/) 
[![FFmpeg](https://img.shields.io/badge/FFmpeg-4.4+-007808?logo=ffmpeg&logoColor=white)](https://ffmpeg.org/) 
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📚 Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Supported Input Methods](#supported-input-methods)
- [Setup Instructions](#setup-instructions)
- [Deployment](#deployment)
- [Usage Guide](#usage-guide)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Performance Notes](#performance-notes)
- [Contributing](#contributing)
- [Status](#status)
- [Contact](#contact)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## ✨ Features

| Feature | Description | Use Case |
|---------|-------------|----------|
| **Accent Detection** | Identifies English accent variants (e.g., American, British, Australian). | Linguistic research, education |
| **Confidence Scores** | Provides 0-100% confidence for accent classification. | Quality assessment |
| **Speech Transcription** | Generates accurate text transcripts of spoken content. | Content analysis, subtitles |
| **Multi-Platform Support** | Processes videos from YouTube, Loom, and other platforms via yt-dlp. | Flexible input sources |
| **File Upload** | Supports direct uploads of video (MP4, MOV) and audio (WAV, MP3) files. | Offline analysis |
| **Streamlit Interface** | Modern, interactive UI for easy use. | User-friendly experience |
| **Debug Metrics** | Provides processing quality and diagnostic information. | Development and troubleshooting |

---

## 🔍 How It Works

The tool processes video/audio inputs to detect English accents using a streamlined pipeline:

![Processing Pipeline](https://via.placeholder.com/600x300.png?text=Accent+Analyzer+Pipeline)

1. **Input Handling**:
   - **yt-dlp**: Downloads videos from URLs (e.g., YouTube, Loom) and extracts audio.
   - **File Upload**: Processes uploaded video/audio files directly.
2. **Audio Processing**:
   - **FFmpeg**: Converts audio to standardized WAV format (16kHz, mono).
3. **Speech Analysis**:
   - **Azure Speech Services**: Performs speech-to-text and detects language variants (e.g., en-US, en-GB).
4. **Accent Classification**:
   - Custom logic maps Azure language codes to human-readable accents with confidence scores.

---

## 📥 Supported Input Methods

| Method | Supported Formats | Notes |
|--------|-------------------|-------|
| **Video URLs** | YouTube, Loom, MP4 links, yt-dlp supported platforms | Requires internet access |
| **File Upload** | **Video**: MP4, MOV, AVI, MKV, WEBM<br>**Audio**: WAV, MP3, M4A, OGG | Max size: 100MB, processed locally |

---

## 🛠️ Setup Instructions

### 1. Prerequisites
- **Python**: 3.8 or higher
- **FFmpeg**: 4.4 or higher (critical for audio processing)
- **Azure Speech Services**: Subscription with API key and region
- **Dependencies**: Listed in `requirements.txt` (e.g., Streamlit, yt-dlp, azure-cognitiveservices-speech)

### 2. Install FFmpeg (Required)
**Windows**:
- Download from [ffmpeg.org](https://ffmpeg.org/download.html).
- Extract and add `ffmpeg.exe` to system PATH.
- Verify: `ffmpeg -version`

**macOS**:
```bash
brew install ffmpeg
```

**Linux**:
```bash
sudo apt update && sudo apt install ffmpeg
```

**Verify**:
```bash
ffmpeg -version
```

### 3. Project Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Novalis133/accent-analyzer.git
   cd accent-analyzer
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Azure Credentials**:
   - Copy `env.example` to `.env`:
     ```bash
     cp env.example .env
     ```
   - Edit `.env` with your Azure credentials:
     ```env
     AZURE_SPEECH_KEY=your_azure_speech_key_here
     AZURE_SPEECH_REGION=your_azure_region_here  # e.g., eastus
     ```
   - Get credentials from [Azure Portal](https://portal.azure.com) under Speech Services.

5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```
   Access at `http://localhost:8501`.

**Troubleshooting**:
- **FFmpeg Error**: Ensure FFmpeg is in PATH (`echo $PATH` or `where ffmpeg`).
- **Azure Error**: Verify `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION` in `.env`.
- **Dependency Issues**: Try `pip install -r requirements.txt --no-cache-dir`.

---

## 🚀 Deployment

Deploy the tool on **Streamlit Community Cloud** for public access.

### Required Files
- `requirements.txt`: Python dependencies
- `packages.txt`: System packages (`ffmpeg`)
- `app.py`, `video_utils.py`, `azure_speech_client.py`, `accent_logic.py`

### Deployment Steps
1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [streamlit.io/cloud](https://streamlit.io/cloud).
   - Click "New app" → "Deploy from GitHub".
   - Select your repository and branch (`main`).
   - Set main file: `app.py`.
   - Add secrets in Advanced Settings:
     ```toml
     [secrets]
     AZURE_SPEECH_KEY = "your_azure_speech_key_here"
     AZURE_SPEECH_REGION = "your_azure_region_here"
     ```

3. **Monitor Deployment**:
   - Check build logs for errors.
   - Test the deployed app thoroughly.

**Live Application**: [Insert link after deployment]

---

## 🎮 Usage Guide

### Option 1: Video URL Analysis
1. Open `http://localhost:8501`.
2. Enter a video URL (e.g., YouTube, Loom) in the "Video URL" field.
3. Click "Analyze Accent".
4. View results: Accent, confidence score, transcript, and debug info.

### Option 2: File Upload Analysis
1. Open `http://localhost:8501`.
2. Click "Choose a video or audio file".
3. Upload a supported file (e.g., MP4, WAV).
4. Click "Analyze Accent".
5. View results.

**Example Output**:
- **Accent**: British English
- **Confidence Score**: 92%
- **Transcript**: "Hello, welcome to our presentation."
- **Processing Quality**: High
- **Debug Info**: [Processing time, audio quality metrics]

**Screenshot**: [Placeholder: Add screenshot of UI](./images/streamlit-ui-screenshot.png)

---

## 🧪 Testing

### Sample Inputs
| Type | Example | Notes |
|------|---------|-------|
| **Video URL** | YouTube: American news, BBC clips, Australian vlogs | Clear speech required |
| **File Upload** | MP4 (talk show), WAV (speech), MP3 (podcast) | Max 100MB |

### Test Cases
1. **American Accent**: YouTube video of a U.S. speaker.
2. **British Accent**: BBC news video.
3. **Australian Accent**: Australian content creator video.
4. **Large File**: 100MB MP4 to test processing limits.
5. **Non-English Audio**: Test language detection fallback.

### Run Tests
```bash
pip install pytest
pytest tests/
```

**Expected Results**:
- Accurate accent classification (e.g., "en-US" → "American English").
- Confidence scores above 80% for clear audio.
- Complete transcripts with minimal errors.

**Troubleshooting**:
- **FFmpeg Not Found**: Verify PATH (`ffmpeg -version`).
- **Azure Errors**: Check credentials in `.env` or Streamlit secrets.
- **Download Failures**: Ensure URL is accessible and yt-dlp is updated.
- **Low Confidence**: Use clearer audio or longer clips.

---

## 📂 Project Structure

```
accent-analyzer/
├── app.py                     # Streamlit application entry point
├── video_utils.py             # Video/audio downloading and processing
├── azure_speech_client.py     # Azure Speech Services integration
├── accent_logic.py            # Accent detection and mapping logic
├── requirements.txt           # Python dependencies
├── packages.txt               # System packages (ffmpeg)
├── env.example               # Environment variables template
├── tests/                    # Unit and integration tests
├── images/                   # Screenshots and assets (optional)
└── README.md                 # Project documentation
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Streamlit | Interactive web interface |
| **Video Processing** | yt-dlp, FFmpeg | Video downloading and audio extraction |
| **Speech Analysis** | Azure Speech Services | Transcription and accent detection |
| **Backend** | Python 3.8+ | Core logic and integration |
| **Deployment** | Streamlit Community Cloud | Public hosting |

---

## ⚡ Performance Notes

- **File Upload**: Faster for small files (<10MB, ~5s processing).
- **URL Processing**: Slower due to download time (e.g., 10-30s for YouTube videos).
- **Large Files**: Processing time scales with size (e.g., 100MB ~1min).
- **Azure Limits**: Subject to API quotas; monitor usage in Azure Portal.
- **Optimization**: Use 16kHz WAV for fastest processing.

---

## 🤝 Contributing

Contributions are welcome! Follow these steps:
1. **Fork the Repository**:
   ```bash
   git fork https://github.com/Novalis133/accent-analyzer.git
   ```

2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Commit Changes**:
   Use [Conventional Commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m "feat: add support for additional accent variants"
   ```

4. **Run Tests and Linting**:
   ```bash
   pytest tests/
   black .
   flake8 .
   ```

5. **Submit a Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```
   Open a PR with a detailed description.

**Guidelines**:
- Follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).
- Ensure tests pass and code is formatted with Black.
- Update documentation in `README.md` or `docs/`.

---

## 📈 Status

- **Core Functionality**: Stable, supports URL and file inputs.
- **Accent Detection**: Accurate for clear speech, improving edge cases.
- **Deployment**: Ready for Streamlit Cloud.

[![Build Status](https://img.shields.io/badge/Build-Passing-green)](https://github.com/Novalis133/accent-analyzer/actions)

---

## 📫 Contact

For questions or collaboration:
- **Email**: osama1339669@gmail.com
- **LinkedIn**: [Osama](https://www.linkedin.com/in/osamat339669/)
- **GitHub Issues**: Open an issue on this repository

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Azure Speech Services](https://azure.microsoft.com/) for accent detection and transcription.
- [Streamlit](https://streamlit.io/) for rapid UI development.
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for video downloading.
- [FFmpeg](https://ffmpeg.org/) for audio processing.
