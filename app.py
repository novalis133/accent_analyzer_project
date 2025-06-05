import streamlit as st
import os
import tempfile
import shutil
from video_utils import download_and_extract_audio, prepare_audio_from_local_file, get_file_info
from azure_speech_client import analyze_audio_with_azure, get_azure_credentials
from accent_logic import determine_accent_and_confidence, get_accent_description, get_supported_accents


def check_azure_credentials():
    """Check if Azure credentials are available."""
    speech_key, speech_region = get_azure_credentials()
    return speech_key is not None and speech_region is not None


def main():
    # Page configuration
    st.set_page_config(
        page_title="Accent Analyzer",
        page_icon="🗣️",
        layout="wide"
    )
    
    # Header
    st.title("🗣️ REM Waste - Accent Analyzer")
    st.markdown("Analyze video URLs or upload files to determine the speaker's English accent using AI.")
    
    # Check credentials at startup and show warning if missing
    if not check_azure_credentials():
        st.error("🔑 **Azure Speech API credentials not configured!**")
        st.markdown("""
        **For local development:** Please ensure your `.env` file contains:
        ```
        AZURE_SPEECH_KEY="your_key_here"
        AZURE_SPEECH_REGION="your_region_here"
        ```
        
        **For deployed app:** Admin needs to configure secrets in Streamlit Cloud settings.
        """)
        st.info("The app will continue to function but accent analysis will fail without valid credentials.")
    
    # Sidebar with instructions
    with st.sidebar:
        st.header("📋 Instructions")
        st.markdown("""
        **Option 1: Video URL**
        1. Paste a video URL (YouTube, Loom, direct MP4, etc.)
        
        **Option 2: File Upload**
        1. Upload a video or audio file directly
        
        **Then:**
        2. Click 'Analyze Accent' to process
        3. View results including:
           - Accent classification
           - Confidence score
           - Transcript (if available)
        
        **Supported formats:**
        - YouTube videos
        - Loom recordings
        - Direct video links (MP4, etc.)
        - Uploaded files: MP4, MOV, AVI, MKV, WEBM, WAV, MP3, M4A, OGG
        """)
        
        st.header("🗺️ Supported Accents")
        for accent in get_supported_accents():
            st.write(f"• {accent}")
        
        st.header("🔧 Requirements")
        st.markdown("""
        - Azure Speech Services API key
        - FFmpeg installed on system
        - Internet connection
        """)
        
        # Credentials status
        st.header("🔑 Credentials Status")
        if check_azure_credentials():
            st.success("✅ Azure credentials configured")
        else:
            st.error("❌ Azure credentials missing")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎥 Input Options")
        
        # Option 1: Video URL input
        st.subheader("Option 1: Video URL")
        video_url = st.text_input(
            "Enter public video URL:",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste the URL of a public video containing speech"
        )
        
        st.markdown("**OR**")
        
        # Option 2: File upload
        st.subheader("Option 2: Upload File")
        uploaded_file = st.file_uploader(
            "Choose a video or audio file:",
            type=['mp4', 'mov', 'avi', 'mkv', 'webm', 'wav', 'mp3', 'm4a', 'ogg'],
            help="Upload a video or audio file containing speech"
        )
        
        # Display file info if uploaded
        if uploaded_file is not None:
            file_size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
            st.info(f"📎 **File:** {uploaded_file.name} ({file_size_mb:.1f} MB)")
        
        # Analyze button
        analyze_clicked = st.button("🔍 Analyze Accent", type="primary", use_container_width=True)
        
        if analyze_clicked:
            # Check for Azure credentials
            if not check_azure_credentials():
                st.error("❌ Azure Speech API credentials not found. Analysis cannot proceed.")
                st.info("Please configure your Azure Speech Services API key and region.")
                return
            
            # Validate input
            if not video_url.strip() and uploaded_file is None:
                st.warning("⚠️ Please provide a video URL or upload a file.")
                return
            
            if video_url.strip() and uploaded_file is not None:
                st.warning("⚠️ Please use either URL input OR file upload, not both.")
                return
            
            # Process the input
            if uploaded_file is not None:
                process_uploaded_file(uploaded_file)
            else:
                process_video_url(video_url)
    
    with col2:
        st.header("ℹ️ About")
        st.markdown("""
        This tool uses **Azure Speech Services** to:
        
        🎯 **Identify** English language variants
        
        🗺️ **Classify** regional accents
        
        📊 **Provide** confidence scores (0-100%)
        
        📝 **Generate** speech transcriptions
        
        🔄 **Support** multiple input methods:
        - Video URLs from popular platforms
        - Direct file uploads
        """)
        
        st.header("🔍 Processing Steps")
        st.markdown("""
        1. **Audio Extraction** - Extract/convert audio to WAV format
        2. **Speech Recognition** - Transcribe speech using Azure AI
        3. **Language Detection** - Identify English variants
        4. **Accent Classification** - Map to regional accents
        5. **Confidence Scoring** - Calculate accuracy metrics
        """)


def process_uploaded_file(uploaded_file):
    """Process uploaded file and analyze accent."""
    
    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text(f"📁 Processing uploaded file: {uploaded_file.name}")
        progress_bar.progress(10)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file to temporary location
            temp_input_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(temp_input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            status_text.text("🔊 Converting audio with ffmpeg...")
            progress_bar.progress(30)
            
            # Process the local file
            audio_path = prepare_audio_from_local_file(temp_input_path, temp_dir)
            
            if not audio_path:
                st.error("❌ Failed to process the uploaded file. Ensure it's a valid video/audio format and ffmpeg is working.")
                return
            
            # Continue with Azure analysis
            status_text.text("🧠 Analyzing speech with Azure AI...")
            progress_bar.progress(60)
            
            azure_result = analyze_audio_with_azure(audio_path)
            
            if not azure_result:
                st.error("❌ Failed to analyze audio with Azure Speech Services. Please check your API credentials.")
                return
            
            # Check for errors in Azure result
            if azure_result.get("error"):
                st.error(f"❌ Azure Speech Services error: {azure_result['error']}")
                return
            
            # Determine accent and confidence
            status_text.text("🎯 Determining accent classification...")
            progress_bar.progress(80)
            
            final_result = determine_accent_and_confidence(azure_result)
            
            # Display results
            status_text.text("✅ Analysis complete!")
            progress_bar.progress(100)
            
            display_results(final_result, input_type="file", input_name=uploaded_file.name)
            
    except Exception as e:
        st.error(f"❌ An error occurred while processing the uploaded file: {str(e)}")
    finally:
        # Clean up progress indicators
        progress_bar.empty()
        status_text.empty()


def process_video_url(video_url: str):
    """Process video URL and analyze accent."""
    
    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text(f"🔽 Downloading video from URL...")
        progress_bar.progress(20)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = download_and_extract_audio(video_url, temp_dir)
            
            if not audio_path:
                st.error("❌ Failed to download video or extract audio. Please check the URL and try again.")
                return
            
            # Continue with Azure analysis
            status_text.text("🧠 Analyzing speech with Azure AI...")
            progress_bar.progress(60)
            
            azure_result = analyze_audio_with_azure(audio_path)
            
            if not azure_result:
                st.error("❌ Failed to analyze audio with Azure Speech Services. Please check your API credentials.")
                return
            
            # Check for errors in Azure result
            if azure_result.get("error"):
                st.error(f"❌ Azure Speech Services error: {azure_result['error']}")
                return
            
            # Determine accent and confidence
            status_text.text("🎯 Determining accent classification...")
            progress_bar.progress(80)
            
            final_result = determine_accent_and_confidence(azure_result)
            
            # Display results
            status_text.text("✅ Analysis complete!")
            progress_bar.progress(100)
            
            display_results(final_result, input_type="url", input_name=video_url)
            
    except Exception as e:
        st.error(f"❌ An error occurred while processing the video URL: {str(e)}")
    finally:
        # Clean up progress indicators
        progress_bar.empty()
        status_text.empty()


def display_results(result: dict, input_type: str = "unknown", input_name: str = ""):
    """Display the analysis results in a formatted way."""
    
    st.header("📊 Analysis Results")
    
    # Input source info
    if input_type == "file":
        st.info(f"📁 **Source:** Uploaded file - {input_name}")
    elif input_type == "url":
        st.info(f"🔗 **Source:** Video URL - {input_name[:60]}{'...' if len(input_name) > 60 else ''}")
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎯 Accent Classification",
            value=result["accent_classification"]
        )
    
    with col2:
        confidence = result["confidence_in_english_accent"]
        st.metric(
            label="📈 Confidence in English",
            value=f"{confidence}%"
        )
    
    with col3:
        # Color code confidence
        if confidence >= 80:
            confidence_label = "🟢 High"
        elif confidence >= 50:
            confidence_label = "🟡 Medium"
        else:
            confidence_label = "🔴 Low"
        
        st.metric(
            label="🎚️ Confidence Level",
            value=confidence_label
        )
    
    with col4:
        processing_quality = result.get("processing_quality", "Unknown")
        st.metric(
            label="⚡ Processing Quality",
            value=processing_quality.split(" - ")[0]  # Just the rating part
        )
    
    # Detailed explanation
    st.subheader("📝 Summary")
    st.info(result["summary_explanation"])
    
    # Processing quality details
    if result.get("processing_quality"):
        quality_color = {
            "Excellent": "🟢",
            "Very Good": "🟢", 
            "Good": "🟡",
            "Fair": "🟡",
            "Poor": "🔴"
        }
        quality_rating = result["processing_quality"].split(" - ")[0]
        quality_icon = quality_color.get(quality_rating, "⚪")
        st.write(f"{quality_icon} **Processing Quality:** {result['processing_quality']}")
    
    # Accent description
    if result["accent_classification"] not in ["Undetermined", "Non-English", "Analysis Failed"]:
        description = get_accent_description(result["accent_classification"])
        st.subheader("🌍 About This Accent")
        st.write(description)
    
    # Transcript
    if result.get("transcript_text") and result["transcript_text"].strip():
        st.subheader("📜 Transcript")
        with st.expander("Click to view full transcript"):
            st.text_area(
                label="Transcribed speech:",
                value=result["transcript_text"],
                height=150,
                disabled=True
            )
    
    # Technical details
    with st.expander("🔧 Technical Details"):
        st.json({
            "Accent Classification": result["accent_classification"],
            "Confidence Score": f"{result['confidence_in_english_accent']}%",
            "Processing Quality": result.get("processing_quality", "Unknown"),
            "Transcript Length": len(result.get("transcript_text", "")),
            "Word Count": len(result.get("transcript_text", "").split()) if result.get("transcript_text") else 0,
            "Input Type": input_type.title()
        })
    
    # Debug information
    if result.get("debug_info"):
        with st.expander("🐛 Debug Information"):
            debug_info = result["debug_info"]
            st.json(debug_info)


if __name__ == "__main__":
    # Load environment variables for local development
    from dotenv import load_dotenv
    load_dotenv()
    
    main() 