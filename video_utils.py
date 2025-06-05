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
    
    print(f"video_utils.py: Preparing to download from URL: {video_url}")
    print(f"video_utils.py: Using yt-dlp options: {ydl_opts}")
    print(f"video_utils.py: Output template: {output_template}")
    
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
                
                # Aggressive file checking after download attempt
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
                
                # Check for expected WAV file
                if os.path.exists(expected_wav_path):
                    wav_size = os.path.getsize(expected_wav_path)
                    print(f"video_utils.py: Final WAV file {expected_wav_path} EXISTS. Size: {wav_size} bytes.")
                    
                    if error_code == 0 and wav_size > 100:  # Basic sanity check for size
                        print(f"video_utils.py: SUCCESS - Returning WAV file: {expected_wav_path}")
                        return expected_wav_path
                    else:
                        print(f"video_utils.py: WAV file exists but error_code was {error_code} or size {wav_size} is too small.")
                        
                        # Still try to use it if size is reasonable, even with non-zero error code
                        if wav_size > 100:
                            print(f"video_utils.py: Attempting to use WAV file despite error_code {error_code}")
                            return expected_wav_path
                        else:
                            print(f"video_utils.py: WAV file too small ({wav_size} bytes), treating as failure")
                else:
                    print(f"video_utils.py: Final WAV file {expected_wav_path} DOES NOT EXIST.")
                    
                    # Try to find *any* .wav file that might have been created with a different name
                    if os.path.exists(output_dir):
                        wav_alternatives = []
                        for f_name in os.listdir(output_dir):
                            if f_name.lower().endswith(".wav"):
                                alt_wav_path = os.path.join(output_dir, f_name)
                                alt_size = os.path.getsize(alt_wav_path)
                                wav_alternatives.append((f_name, alt_wav_path, alt_size))
                                print(f"video_utils.py: Found alternative WAV file: {f_name}, Path: {alt_wav_path}, Size: {alt_size} bytes")
                        
                        # Use the largest WAV file if any exist
                        if wav_alternatives:
                            wav_alternatives.sort(key=lambda x: x[2], reverse=True)  # Sort by size, largest first
                            best_wav = wav_alternatives[0]
                            if best_wav[2] > 100:  # Check size is reasonable
                                print(f"video_utils.py: Using largest alternative WAV file: {best_wav[1]} ({best_wav[2]} bytes)")
                                return best_wav[1]
                            else:
                                print(f"video_utils.py: Largest alternative WAV file is too small: {best_wav[2]} bytes")
                        
                        # Look for other audio files that might need conversion
                        audio_extensions = ['.mp3', '.m4a', '.mp4', '.webm', '.ogg', '.flac']
                        audio_files = []
                        for f_name in os.listdir(output_dir):
                            if any(f_name.lower().endswith(ext) for ext in audio_extensions):
                                audio_path = os.path.join(output_dir, f_name)
                                audio_size = os.path.getsize(audio_path)
                                audio_files.append((f_name, audio_path, audio_size))
                                print(f"video_utils.py: Found non-WAV audio file: {f_name}, Size: {audio_size} bytes")
                        
                        if audio_files:
                            print(f"video_utils.py: Found {len(audio_files)} non-WAV audio files, attempting conversion...")
                            
                            # Try to convert the largest audio file
                            audio_files.sort(key=lambda x: x[2], reverse=True)  # Sort by size
                            largest_audio = audio_files[0]
                            
                            print(f"video_utils.py: Attempting ffmpeg conversion of: {largest_audio[1]}")
                            converted_path = prepare_audio_from_local_file(largest_audio[1], output_dir)
                            
                            if converted_path:
                                print(f"video_utils.py: FFMPEG_SUCCESS - Successfully converted to: {converted_path}")
                                return converted_path
                            else:
                                print("video_utils.py: FFMPEG_FAILED - Manual ffmpeg conversion also failed")
                        else:
                            print("video_utils.py: No audio files found at all for conversion")
                
                # If we reach here, no suitable audio file was found or created
                print(f"video_utils.py: No suitable audio output found despite error_code: {error_code}")
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