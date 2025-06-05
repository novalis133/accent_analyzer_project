# IMPORTANT: This module requires ffmpeg to be installed and accessible in the system PATH
# Download ffmpeg from https://ffmpeg.org/download.html and ensure it's in your PATH

import os
import subprocess
import yt_dlp
import tempfile
import traceback
from typing import Optional

# VERSION STAMP - COMPREHENSIVE LOGGING FOR YOUTUBE DEBUGGING
print("VIDEO_UTILS_VERSION_CHECK: v3.0 - Enhanced YouTube Processing with Fallback Conversion Strategy - 2025-01-05")


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


def convert_any_audio_to_wav(input_audio_path: str, output_wav_path: str) -> Optional[str]:
    """
    Convert any audio file to WAV format using direct ffmpeg call.
    
    Args:
        input_audio_path: Path to input audio file (any format)
        output_wav_path: Desired path for output WAV file
        
    Returns:
        Path to converted WAV file or None if conversion failed
    """
    print(f"DEBUG_DIRECT_FFMPEG: Converting {input_audio_path} to {output_wav_path}")
    
    try:
        # Check input file exists
        if not os.path.exists(input_audio_path):
            print(f"DEBUG_DIRECT_FFMPEG_ERROR: Input file does not exist: {input_audio_path}")
            return None
            
        input_size = os.path.getsize(input_audio_path)
        print(f"DEBUG_DIRECT_FFMPEG_INPUT_SIZE: {input_size} bytes")
        
        # Construct ffmpeg command for WAV conversion
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_audio_path,
            '-vn',  # No video output
            '-acodec', 'pcm_s16le',  # WAV audio codec
            '-ar', '16000',  # Audio sample rate 16kHz for Azure
            '-ac', '1',  # Mono audio for Azure
            '-y',  # Overwrite output
            output_wav_path
        ]
        
        print(f"DEBUG_DIRECT_FFMPEG_COMMAND: {' '.join(ffmpeg_cmd)}")
        
        # Run ffmpeg command
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print(f"DEBUG_DIRECT_FFMPEG_RETURNCODE: {result.returncode}")
        if result.stdout:
            print(f"DEBUG_DIRECT_FFMPEG_STDOUT: {result.stdout}")
        if result.stderr:
            print(f"DEBUG_DIRECT_FFMPEG_STDERR: {result.stderr}")
        
        # Check if conversion succeeded
        if result.returncode == 0 and os.path.exists(output_wav_path):
            output_size = os.path.getsize(output_wav_path)
            print(f"DEBUG_DIRECT_FFMPEG_SUCCESS: Converted to WAV with size {output_size} bytes")
            return output_wav_path
        else:
            print(f"DEBUG_DIRECT_FFMPEG_FAILED: Conversion failed with return code {result.returncode}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"DEBUG_DIRECT_FFMPEG_TIMEOUT: Conversion timed out for {input_audio_path}")
        return None
    except Exception as e:
        print(f"DEBUG_DIRECT_FFMPEG_EXCEPTION: Error during conversion: {str(e)}")
        traceback.print_exc()
        return None


def download_and_extract_audio(video_url: str, output_dir: str) -> Optional[str]:
    """
    Download video from URL and extract audio to WAV format.
    Enhanced version with better yt-dlp configuration and fallback conversion.
    
    Args:
        video_url: URL of the video to download
        output_dir: Directory to save the extracted audio
        
    Returns:
        Path to extracted WAV file or None if failed
    """
    print(f"DEBUG_YTDLP_START: Starting video download and audio extraction")
    print(f"DEBUG_YTDLP_URL: {video_url}")
    print(f"DEBUG_YTDLP_OUTPUT_DIR: {output_dir}")
    
    # Define expected output filename and path
    base_filename = "youtube_audio"  # Simplified base name
    expected_wav_filename = f"{base_filename}.wav"
    expected_wav_path = os.path.join(output_dir, expected_wav_filename)
    
    print(f"DEBUG_YTDLP_EXPECTED_OUTPUT: {expected_wav_path}")
    
    # Enhanced yt-dlp options with better postprocessor configuration
    ydl_opts = {
        'format': 'bestaudio/best',  # Get the best quality audio stream
        'outtmpl': os.path.join(output_dir, base_filename),  # Base name without extension
        'noplaylist': True,  # Only download single video, not playlist
        'quiet': False,      # Show yt-dlp output for debugging
        'verbose': True,     # Enable verbose yt-dlp logging
        'noprogress': True,  # Suppress progress bar in logs
        'socket_timeout': 30,  # 30 second timeout for network operations
        'retries': 3,        # Retry on failures
        'fragment_retries': 3,  # Retry fragments
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',           # Request WAV output
            'preferredquality': '0',           # Best quality for WAV (lossless)
            'postprocessor_args': [
                '-acodec', 'pcm_s16le',  # Explicit WAV codec
                '-ar', '16000',          # 16kHz sample rate for Azure Speech Services
                '-ac', '1',              # Mono channel for Azure compatibility
                '-f', 'wav',             # Force WAV container format
            ],
        }],
        # Additional options for reliability
        'prefer_ffmpeg': True,    # Prefer ffmpeg over avconv
        'keepvideo': False,       # Don't keep the video file after audio extraction
    }
    
    print(f"video_utils.py: Preparing to download from URL: {video_url}")
    print(f"video_utils.py: Using enhanced yt-dlp options: {ydl_opts}")
    print(f"video_utils.py: Base filename: {base_filename}")
    
    # Ensure output directory exists
    print("DEBUG_YTDLP_PRE_DOWNLOAD: Ensuring output directory exists...")
    if not os.path.exists(output_dir):
        print("DEBUG_YTDLP_PRE_FILES: Output directory does not exist yet")
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"DEBUG_YTDLP_CREATED_DIR: Created output directory: {output_dir}")
        except Exception as mkdir_error:
            print(f"video_utils.py: FAILED to create output directory {output_dir}: {mkdir_error}")
            return None
    else:
        pre_files = os.listdir(output_dir)
        print(f"DEBUG_YTDLP_PRE_FILES: Files in output directory before download: {pre_files}")
    
    # Main yt-dlp processing with comprehensive error handling
    try:
        print("DEBUG_YTDLP_STARTING_DOWNLOAD: Creating YoutubeDL instance...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"video_utils.py: Attempting ydl.download() for {video_url}...")
            
            try:
                error_code = ydl.download([video_url])
                print(f"video_utils.py: ydl.download() completed with error_code: {error_code}")
                
                # Comprehensive file checking after download attempt
                print(f"video_utils.py: Checking contents of output_dir: {output_dir}")
                if os.path.exists(output_dir):
                    all_files = os.listdir(output_dir)
                    print(f"video_utils.py: Files in output_dir: {all_files}")
                    
                    # List detailed info for each file
                    for file_name in all_files:
                        file_path = os.path.join(output_dir, file_name)
                        if os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)
                            print(f"video_utils.py: File details - {file_name}: {file_size} bytes")
                else:
                    print(f"video_utils.py: output_dir {output_dir} does not exist after download attempt!")
                    return None
                
                print(f"video_utils.py: Expected final WAV path: {expected_wav_path}")
                
                # Primary check: Look for the expected WAV file
                if os.path.exists(expected_wav_path):
                    wav_size = os.path.getsize(expected_wav_path)
                    print(f"video_utils.py: Expected WAV file found with size: {wav_size} bytes")
                    
                    if wav_size > 1000:  # Reasonable size check
                        print(f"video_utils.py: PRIMARY SUCCESS - Returning WAV file: {expected_wav_path}")
                        return expected_wav_path
                    else:
                        print(f"video_utils.py: Expected WAV file too small ({wav_size} bytes), treating as failure")
                
                # Secondary check: Look for any WAV files with our base filename
                wav_files = []
                for f_name in all_files:
                    if f_name.lower().endswith('.wav') and base_filename in f_name:
                        wav_path = os.path.join(output_dir, f_name)
                        wav_size = os.path.getsize(wav_path)
                        wav_files.append((f_name, wav_path, wav_size))
                        print(f"video_utils.py: Found WAV file: {f_name}, Size: {wav_size} bytes")
                
                if wav_files:
                    # Use the largest valid WAV file
                    wav_files.sort(key=lambda x: x[2], reverse=True)  # Sort by size
                    best_wav = wav_files[0]
                    if best_wav[2] > 1000:
                        print(f"video_utils.py: SECONDARY SUCCESS - Using WAV file: {best_wav[1]}")
                        return best_wav[1]
                
                # Tertiary check: Look for intermediate audio files that need conversion
                print(f"video_utils.py: No suitable WAV file found. Looking for intermediate audio files...")
                audio_extensions = ['.m4a', '.mp4', '.webm', '.ogg', '.mp3', '.aac', '.opus']
                intermediate_files = []
                
                for f_name in all_files:
                    file_lower = f_name.lower()
                    if any(file_lower.endswith(ext) for ext in audio_extensions):
                        # Check if it matches our base filename pattern
                        if base_filename in f_name or any(f_name.startswith(base_filename + ext) for ext in ['', '.']):
                            audio_path = os.path.join(output_dir, f_name)
                            audio_size = os.path.getsize(audio_path)
                            intermediate_files.append((f_name, audio_path, audio_size))
                            print(f"video_utils.py: Found intermediate audio file: {f_name}, Size: {audio_size} bytes")
                
                if intermediate_files:
                    print(f"video_utils.py: Found {len(intermediate_files)} intermediate audio files, attempting fallback conversion...")
                    
                    # Try to convert the largest intermediate file
                    intermediate_files.sort(key=lambda x: x[2], reverse=True)  # Sort by size
                    largest_intermediate = intermediate_files[0]
                    
                    if largest_intermediate[2] > 1000:  # Reasonable size check
                        print(f"video_utils.py: Attempting fallback conversion of: {largest_intermediate[1]}")
                        
                        # Use our direct ffmpeg conversion function
                        fallback_wav_path = os.path.join(output_dir, f"{base_filename}_converted.wav")
                        converted_path = convert_any_audio_to_wav(largest_intermediate[1], fallback_wav_path)
                        
                        if converted_path and os.path.exists(converted_path):
                            converted_size = os.path.getsize(converted_path)
                            print(f"video_utils.py: FALLBACK SUCCESS - Converted to: {converted_path} ({converted_size} bytes)")
                            
                            # Clean up intermediate file
                            try:
                                os.remove(largest_intermediate[1])
                                print(f"video_utils.py: Cleaned up intermediate file: {largest_intermediate[1]}")
                            except Exception as cleanup_error:
                                print(f"video_utils.py: Warning - Could not clean up intermediate file: {cleanup_error}")
                            
                            return converted_path
                        else:
                            print("video_utils.py: FALLBACK FAILED - Direct ffmpeg conversion also failed")
                    else:
                        print(f"video_utils.py: Largest intermediate file too small ({largest_intermediate[2]} bytes)")
                else:
                    print("video_utils.py: No intermediate audio files found for conversion")
                
                # If we reach here, all strategies failed
                print(f"video_utils.py: All conversion strategies failed for URL: {video_url}")
                print(f"video_utils.py: yt-dlp error_code: {error_code}")
                return None
                
            except Exception as download_exception:
                print(f"video_utils.py: EXCEPTION during ydl.download() call!")
                print(f"video_utils.py: Download exception type: {type(download_exception)}")
                print(f"video_utils.py: Download exception message: {download_exception}")
                import traceback
                print("video_utils.py: Download exception traceback follows:")
                traceback.print_exc()
                return None
                
    except Exception as e:
        print(f"video_utils.py: EXCEPTION during yt-dlp processing for URL {video_url}!")
        print(f"video_utils.py: Exception type: {type(e)}")
        print(f"video_utils.py: Exception message: {e}")
        import traceback
        print("video_utils.py: Full traceback follows:")
        traceback.print_exc()
        return None
    
    # If code reaches here without returning, it means something went wrong
    print(f"video_utils.py: download_and_extract_audio falling through, returning None for URL {video_url}")
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