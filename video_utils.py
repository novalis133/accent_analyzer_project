# IMPORTANT: This module requires ffmpeg to be installed and accessible in the system PATH
# Download ffmpeg from https://ffmpeg.org/download.html and ensure it's in your PATH

import os
import subprocess
import yt_dlp
import tempfile
import traceback
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
    print(f"DEBUG_FFMPEG_START: Processing local file")
    print(f"DEBUG_FFMPEG_INPUT: input_filepath = {input_filepath}")
    print(f"DEBUG_FFMPEG_OUTPUT_DIR: output_dir = {output_dir}")
    
    try:
        # Check input file exists
        if not os.path.exists(input_filepath):
            print(f"DEBUG_FFMPEG_ERROR: Input file does not exist: {input_filepath}")
            return None
            
        input_size = os.path.getsize(input_filepath)
        print(f"DEBUG_FFMPEG_INPUT_SIZE: {input_size} bytes")
        
        # Define output path
        output_wav_path = os.path.join(output_dir, "processed_local_audio.wav")
        print(f"DEBUG_FFMPEG_TARGET_OUTPUT: {output_wav_path}")
        
        # Construct ffmpeg command
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
        
        print(f"DEBUG_FFMPEG_COMMAND: {' '.join(ffmpeg_cmd)}")
        
        # Run ffmpeg command
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout for large files
        )
        
        print(f"DEBUG_FFMPEG_RETURNCODE: {result.returncode}")
        print(f"DEBUG_FFMPEG_STDOUT: {result.stdout}")
        print(f"DEBUG_FFMPEG_STDERR: {result.stderr}")
        
        # Check if ffmpeg succeeded
        if result.returncode == 0:
            # Verify output file was created
            if os.path.exists(output_wav_path):
                output_size = os.path.getsize(output_wav_path)
                print(f"DEBUG_FFMPEG_SUCCESS: Output file created with size {output_size} bytes")
                print(f"DEBUG_FFMPEG_FINAL_PATH: {output_wav_path}")
                return output_wav_path
            else:
                print(f"DEBUG_FFMPEG_ERROR: Output file not found after successful ffmpeg: {output_wav_path}")
                return None
        else:
            print(f"DEBUG_FFMPEG_FAILED: ffmpeg failed with return code {result.returncode}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"DEBUG_FFMPEG_TIMEOUT: ffmpeg processing timed out for file: {input_filepath}")
        return None
    except FileNotFoundError:
        print("DEBUG_FFMPEG_NOT_FOUND: ffmpeg not found in system PATH. Please install ffmpeg.")
        return None
    except Exception as e:
        print(f"DEBUG_FFMPEG_EXCEPTION: Error processing local file: {str(e)}")
        traceback.print_exc()
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
    print(f"DEBUG_YTDLP_START: Starting video download and audio extraction")
    print(f"DEBUG_YTDLP_URL: {video_url}")
    print(f"DEBUG_YTDLP_OUTPUT_DIR: {output_dir}")
    
    try:
        # Configure yt-dlp options
        output_path = os.path.join(output_dir, 'audio')
        expected_wav_path = f'{output_path}.wav'
        
        print(f"DEBUG_YTDLP_EXPECTED_OUTPUT: {expected_wav_path}")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}.%(ext)s',
            'verbose': True,  # Enable verbose yt-dlp logging
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
        
        print(f"DEBUG_YTDLP_OPTIONS: {ydl_opts}")
        
        # Download and extract audio
        print("DEBUG_YTDLP_STARTING_DOWNLOAD: Creating YoutubeDL instance...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("DEBUG_YTDLP_CALLING_DOWNLOAD: Calling ydl.download()...")
            error_code = ydl.download([video_url])
            print(f"DEBUG_YTDLP_DOWNLOAD_RESULT: ydl.download() returned error_code = {error_code}")
        
        print("DEBUG_YTDLP_DOWNLOAD_COMPLETE: yt-dlp download call finished")
        
        # Check what files were actually created
        print("DEBUG_YTDLP_CHECKING_FILES: Listing all files in output directory:")
        if os.path.exists(output_dir):
            all_files = os.listdir(output_dir)
            print(f"DEBUG_YTDLP_FILES_FOUND: {all_files}")
            
            # Check for the expected WAV file
            if os.path.exists(expected_wav_path):
                file_size = os.path.getsize(expected_wav_path)
                print(f"DEBUG_YTDLP_SUCCESS: Expected WAV file found with size {file_size} bytes")
                print(f"DEBUG_YTDLP_FINAL_PATH: {expected_wav_path}")
                return expected_wav_path
            else:
                print(f"DEBUG_YTDLP_EXPECTED_MISSING: Expected WAV file not found: {expected_wav_path}")
                
                # Look for any WAV files as fallback
                wav_files = [f for f in all_files if f.endswith('.wav')]
                if wav_files:
                    fallback_wav = os.path.join(output_dir, wav_files[0])
                    fallback_size = os.path.getsize(fallback_wav)
                    print(f"DEBUG_YTDLP_FALLBACK_FOUND: Found WAV file: {fallback_wav} with size {fallback_size} bytes")
                    return fallback_wav
                else:
                    print("DEBUG_YTDLP_NO_WAV_FOUND: No WAV files found in output directory")
                    return None
        else:
            print(f"DEBUG_YTDLP_NO_OUTPUT_DIR: Output directory does not exist: {output_dir}")
            return None
            
    except Exception as e:
        print(f"DEBUG_YTDLP_EXCEPTION: Error in download_and_extract_audio: {str(e)}")
        traceback.print_exc()
        return None


def cleanup_temp_files(file_path: str):
    """Clean up temporary files."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"DEBUG_CLEANUP: Removed file: {file_path}")
    except Exception as e:
        print(f"DEBUG_CLEANUP_ERROR: Error cleaning up file {file_path}: {str(e)}")


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