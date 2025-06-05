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
        # Define expected output filename and path
        expected_wav_filename = "processed_youtube_audio.wav"
        expected_wav_path = os.path.join(output_dir, expected_wav_filename)
        
        print(f"DEBUG_YTDLP_EXPECTED_OUTPUT: {expected_wav_path}")
        
        # Configure yt-dlp options with proper postprocessor configuration
        base_filename = os.path.splitext(expected_wav_filename)[0]  # "processed_youtube_audio"
        output_template = os.path.join(output_dir, base_filename)   # Full path without extension
        
        ydl_opts = {
            'format': 'bestaudio/best',  # Get the best quality audio stream
            'outtmpl': f'{output_template}.%(ext)s',  # yt-dlp will replace %(ext)s with actual extension
            'noplaylist': True,  # Only download single video, not playlist
            'quiet': False,      # Show yt-dlp output for debugging
            'verbose': True,     # Enable verbose yt-dlp logging
            'noprogress': True,  # Suppress progress bar in logs
            'socket_timeout': 30,  # 30 second timeout for network operations
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',           # Request WAV output
                'preferredquality': '192',         # Audio quality (not critical for WAV)
                'postprocessor_args': [
                    '-ar', '16000',  # 16kHz sample rate for Azure Speech Services
                    '-ac', '1',      # Mono channel for Azure compatibility
                    '-acodec', 'pcm_s16le',  # Explicit WAV codec
                ],
            }],
        }
        
        print(f"DEBUG_YTDLP_OPTIONS: {ydl_opts}")
        print(f"DEBUG_YTDLP_OUTPUT_TEMPLATE: {output_template}")
        
        # List files before download for comparison
        print("DEBUG_YTDLP_PRE_DOWNLOAD: Files in output directory before download:")
        if os.path.exists(output_dir):
            pre_files = os.listdir(output_dir)
            print(f"DEBUG_YTDLP_PRE_FILES: {pre_files}")
        else:
            print("DEBUG_YTDLP_PRE_FILES: Output directory does not exist yet")
            os.makedirs(output_dir, exist_ok=True)
            print(f"DEBUG_YTDLP_CREATED_DIR: Created output directory: {output_dir}")
        
        # Download and extract audio
        print("DEBUG_YTDLP_STARTING_DOWNLOAD: Creating YoutubeDL instance...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("DEBUG_YTDLP_CALLING_DOWNLOAD: Calling ydl.download()...")
            try:
                error_code = ydl.download([video_url])
                print(f"DEBUG_YTDLP_DOWNLOAD_RESULT: ydl.download() returned error_code = {error_code}")
                
                if error_code != 0:
                    print(f"DEBUG_YTDLP_ERROR: yt-dlp returned non-zero error code: {error_code}")
                    return None
                    
            except Exception as ydl_exception:
                print(f"DEBUG_YTDLP_DOWNLOAD_EXCEPTION: Exception during yt-dlp download: {str(ydl_exception)}")
                traceback.print_exc()
                return None
        
        print("DEBUG_YTDLP_DOWNLOAD_COMPLETE: yt-dlp download call finished")
        
        # Check what files were actually created
        print("DEBUG_YTDLP_CHECKING_FILES: Listing all files in output directory after download:")
        if os.path.exists(output_dir):
            all_files = os.listdir(output_dir)
            print(f"DEBUG_YTDLP_FILES_FOUND: {all_files}")
            
            # Check for the expected WAV file first
            if os.path.exists(expected_wav_path):
                file_size = os.path.getsize(expected_wav_path)
                print(f"DEBUG_YTDLP_SUCCESS: Expected WAV file found with size {file_size} bytes")
                
                if file_size > 0:
                    print(f"DEBUG_YTDLP_FINAL_PATH: {expected_wav_path}")
                    return expected_wav_path
                else:
                    print(f"DEBUG_YTDLP_EMPTY_FILE: Expected WAV file is empty (0 bytes)")
                    
            else:
                print(f"DEBUG_YTDLP_EXPECTED_MISSING: Expected WAV file not found: {expected_wav_path}")
                
            # Look for any WAV files as fallback
            wav_files = [f for f in all_files if f.endswith('.wav')]
            if wav_files:
                print(f"DEBUG_YTDLP_FOUND_WAV_FILES: Found {len(wav_files)} WAV files: {wav_files}")
                
                # Try each WAV file and return the first non-empty one
                for wav_file in wav_files:
                    fallback_wav = os.path.join(output_dir, wav_file)
                    fallback_size = os.path.getsize(fallback_wav)
                    print(f"DEBUG_YTDLP_CHECKING_WAV: {wav_file} - size: {fallback_size} bytes")
                    
                    if fallback_size > 0:
                        print(f"DEBUG_YTDLP_FALLBACK_SUCCESS: Using WAV file: {fallback_wav}")
                        return fallback_wav
                        
                print("DEBUG_YTDLP_ALL_WAV_EMPTY: All found WAV files are empty")
            else:
                print("DEBUG_YTDLP_NO_WAV_FOUND: No WAV files found in output directory")
                
                # Look for any audio files that might need conversion
                audio_extensions = ['.mp3', '.m4a', '.mp4', '.webm', '.ogg', '.flac']
                audio_files = [f for f in all_files if any(f.lower().endswith(ext) for ext in audio_extensions)]
                
                if audio_files:
                    print(f"DEBUG_YTDLP_FOUND_AUDIO_FILES: Found non-WAV audio files: {audio_files}")
                    print("DEBUG_YTDLP_CONVERSION_NEEDED: yt-dlp postprocessor may have failed, audio files need manual conversion")
                    
                    # Try to convert the first audio file using our ffmpeg function
                    first_audio = os.path.join(output_dir, audio_files[0])
                    print(f"DEBUG_YTDLP_TRYING_FFMPEG_CONVERSION: Attempting to convert {first_audio}")
                    
                    converted_path = prepare_audio_from_local_file(first_audio, output_dir)
                    if converted_path:
                        print(f"DEBUG_YTDLP_FFMPEG_SUCCESS: Successfully converted to: {converted_path}")
                        return converted_path
                    else:
                        print("DEBUG_YTDLP_FFMPEG_FAILED: Manual ffmpeg conversion also failed")
                else:
                    print("DEBUG_YTDLP_NO_AUDIO_FILES: No audio files found at all")
                    
            return None
            
        else:
            print(f"DEBUG_YTDLP_NO_OUTPUT_DIR: Output directory does not exist after download: {output_dir}")
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