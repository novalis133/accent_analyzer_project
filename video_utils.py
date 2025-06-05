# IMPORTANT: This module requires ffmpeg to be installed and accessible in the system PATH
# Download ffmpeg from https://ffmpeg.org/download.html and ensure it's in your PATH

import os
import subprocess
import yt_dlp
import tempfile
from typing import Optional


def prepare_audio_from_local_file(input_filepath: str, output_dir: str) -> Optional[str]:
    """
    Process a local video/audio file and convert it to standardized WAV format using ffmpeg.
    
    Args:
        input_filepath: Absolute path to the input video/audio file
        output_dir: Directory where the processed WAV file should be saved
        
    Returns:
        Path to processed WAV file or None if processing failed
    """
    try:
        # Define output path
        output_wav_path = os.path.join(output_dir, "processed_local_audio.wav")
        
        # Construct ffmpeg command
        # -i: input file
        # -vn: no video output (audio only)
        # -acodec pcm_s16le: WAV audio codec
        # -ar 16000: audio sample rate 16kHz (optimal for speech recognition)
        # -ac 1: mono audio (single channel)
        # -y: overwrite output file if it exists
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_filepath,
            '-vn',  # No video output
            '-acodec', 'pcm_s16le',  # WAV audio codec
            '-ar', '16000',  # Audio sample rate 16kHz
            '-ac', '1',  # Mono audio
            '-y',  # Overwrite output
            output_wav_path
        ]
        
        print(f"Processing local file with ffmpeg: {input_filepath}")
        
        # Run ffmpeg command
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout for large files
        )
        
        # Check if ffmpeg succeeded
        if result.returncode == 0:
            # Verify output file was created
            if os.path.exists(output_wav_path) and os.path.getsize(output_wav_path) > 0:
                print(f"Successfully processed local file to: {output_wav_path}")
                return output_wav_path
            else:
                print(f"ffmpeg completed but output file not found or empty: {output_wav_path}")
                return None
        else:
            print(f"ffmpeg failed with return code {result.returncode}")
            print(f"ffmpeg stderr: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"ffmpeg processing timed out for file: {input_filepath}")
        return None
    except FileNotFoundError:
        print("ffmpeg not found in system PATH. Please install ffmpeg and ensure it's accessible.")
        return None
    except Exception as e:
        print(f"Error processing local file with ffmpeg: {str(e)}")
        return None


def download_and_extract_audio(video_url: str, output_dir: str) -> Optional[str]:
    """
    Download video from URL and extract audio to WAV format.
    
    Args:
        video_url: URL of the video to download
        output_dir: Directory to save the extracted audio
        
    Returns:
        Path to extracted WAV file or None if failed
    """
    try:
        # Configure yt-dlp options
        output_path = os.path.join(output_dir, 'audio')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'postprocessor_args': [
                '-ar', '16000',  # 16kHz sample rate for Azure Speech
                '-ac', '1',      # Mono channel
            ],
        }
        
        # Download and extract audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        # Check if WAV file was created
        wav_path = f'{output_path}.wav'
        if os.path.exists(wav_path):
            return wav_path
        else:
            print(f"WAV file not found at expected path: {wav_path}")
            return None
            
    except Exception as e:
        print(f"Error downloading and extracting audio: {str(e)}")
        return None


def cleanup_temp_files(file_path: str):
    """Clean up temporary files."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {str(e)}")


def get_file_info(filepath: str) -> dict:
    """
    Get basic information about a file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Dictionary with file information
    """
    try:
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            file_name = os.path.basename(filepath)
            file_ext = os.path.splitext(filepath)[1].lower()
            
            return {
                "name": file_name,
                "size": file_size,
                "extension": file_ext,
                "size_mb": round(file_size / (1024 * 1024), 2)
            }
        else:
            return {"error": "File not found"}
    except Exception as e:
        return {"error": str(e)} 