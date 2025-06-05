#!/usr/bin/env python3
"""
Local Test Script for video_utils.py YouTube Processing

This script tests the download_and_extract_audio function with various
YouTube URLs to identify the root cause of processing failures.

Usage: python test_video_utils.py
"""

import os
import sys
import tempfile
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our function to test
try:
    from video_utils import download_and_extract_audio, get_file_info
    print("✅ Successfully imported video_utils functions")
except ImportError as e:
    print(f"❌ Failed to import video_utils: {e}")
    sys.exit(1)

# Test URL definitions with descriptions
TEST_CASES = [
    {
        "name": "Short English Speech (Working Test)",
        "url": "https://www.youtube.com/watch?v=ZbZSe6N_BXs",  # Sample short public domain speech
        "expected": "SUCCESS",
        "description": "A short, simple video that should work reliably"
    },
    {
        "name": "Previously Failing URL from Logs",
        "url": "https://youtu.be/TkyeUckXc-0?si=7agVr2hjn66mSc2J",
        "expected": "INVESTIGATE",
        "description": "The specific URL that was failing with 0% confidence"
    },
    {
        "name": "Popular Music Video (Different Audio Codec)",
        "url": "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Despacito - common test video
        "expected": "SUCCESS",
        "description": "Popular video likely using AAC/Opus audio codec"
    },
    {
        "name": "Educational/Documentary Content",
        "url": "https://www.youtube.com/watch?v=sTANio_2E0Q",  # TED-Ed or similar
        "expected": "SUCCESS", 
        "description": "Educational content with clear speech"
    },
    {
        "name": "Invalid Video ID",
        "url": "https://www.youtube.com/watch?v=INVALIDID123",
        "expected": "FAIL_GRACEFULLY",
        "description": "Should fail gracefully with invalid video ID"
    },
    {
        "name": "Malformed YouTube URL",
        "url": "https://ww.youtube.com/invalid-format",
        "expected": "FAIL_GRACEFULLY", 
        "description": "Should handle malformed URLs gracefully"
    },
    {
        "name": "Very Short Video",
        "url": "https://www.youtube.com/watch?v=hFZFjoX2cGg",  # Very short video
        "expected": "SUCCESS",
        "description": "Test handling of very short audio clips"
    }
]

def validate_wav_file(file_path: str) -> Dict[str, any]:
    """
    Validate a WAV file and return detailed information.
    
    Args:
        file_path: Path to the WAV file
        
    Returns:
        Dictionary with validation results
    """
    validation = {
        "exists": False,
        "size_bytes": 0,
        "is_wav": False,
        "is_readable": False,
        "duration_estimate": 0,
        "error": None
    }
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            validation["error"] = "File does not exist"
            return validation
            
        validation["exists"] = True
        validation["size_bytes"] = os.path.getsize(file_path)
        
        # Check file extension
        if file_path.lower().endswith('.wav'):
            validation["is_wav"] = True
            
        # Try to read file header to validate it's actually a WAV
        try:
            with open(file_path, 'rb') as f:
                header = f.read(12)
                if len(header) >= 12:
                    # Check for RIFF header and WAVE format
                    if header[:4] == b'RIFF' and header[8:12] == b'WAVE':
                        validation["is_readable"] = True
                        
                        # Rough duration estimate (16kHz mono, 16-bit = 32000 bytes/second)
                        if validation["size_bytes"] > 44:  # WAV header is ~44 bytes
                            audio_bytes = validation["size_bytes"] - 44
                            validation["duration_estimate"] = audio_bytes / 32000  # Rough estimate
                            
        except Exception as read_error:
            validation["error"] = f"Failed to read file header: {read_error}"
            
    except Exception as e:
        validation["error"] = f"Validation error: {e}"
        
    return validation

def test_single_url(test_case: Dict[str, str], test_number: int, total_tests: int) -> Dict[str, any]:
    """
    Test a single YouTube URL with the download_and_extract_audio function.
    
    Args:
        test_case: Dictionary containing test case information
        test_number: Current test number
        total_tests: Total number of tests
        
    Returns:
        Dictionary with test results
    """
    print(f"\n{'='*80}")
    print(f"TEST {test_number}/{total_tests}: {test_case['name']}")
    print(f"URL: {test_case['url']}")
    print(f"Expected: {test_case['expected']}")
    print(f"Description: {test_case['description']}")
    print(f"{'='*80}")
    
    result = {
        "test_name": test_case['name'],
        "url": test_case['url'],
        "expected": test_case['expected'],
        "success": False,
        "output_file": None,
        "error_message": None,
        "execution_time": 0,
        "file_validation": None
    }
    
    start_time = time.time()
    
    try:
        # Create temporary directory for this test
        with tempfile.TemporaryDirectory(prefix=f"test_ytdlp_{test_number}_") as temp_dir:
            print(f"\n🔄 Testing with temporary directory: {temp_dir}")
            print(f"⏰ Starting download at {time.strftime('%H:%M:%S')}")
            
            # Call the function under test
            output_file_path = download_and_extract_audio(test_case['url'], temp_dir)
            
            end_time = time.time()
            result["execution_time"] = end_time - start_time
            
            print(f"\n📁 Contents of temp directory after processing:")
            try:
                temp_files = os.listdir(temp_dir)
                if temp_files:
                    for file_name in temp_files:
                        file_path = os.path.join(temp_dir, file_name)
                        file_size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
                        print(f"  📄 {file_name}: {file_size} bytes")
                else:
                    print("  🔍 No files found in temp directory")
            except Exception as list_error:
                print(f"  ❌ Error listing temp directory: {list_error}")
            
            # Analyze results
            if output_file_path is None:
                print(f"\n❌ Function returned None (processing failed)")
                result["success"] = False
                result["error_message"] = "Function returned None"
                
                if test_case['expected'] == "FAIL_GRACEFULLY":
                    print(f"✅ Expected graceful failure - TEST PASSED")
                    result["success"] = True
                    
            else:
                print(f"\n✅ Function returned file path: {output_file_path}")
                result["output_file"] = output_file_path
                
                # Validate the output file
                validation = validate_wav_file(output_file_path)
                result["file_validation"] = validation
                
                print(f"\n📊 File Validation Results:")
                print(f"  Exists: {validation['exists']}")
                print(f"  Size: {validation['size_bytes']} bytes")
                print(f"  Is WAV: {validation['is_wav']}")
                print(f"  Is Readable: {validation['is_readable']}")
                print(f"  Duration Estimate: {validation['duration_estimate']:.2f} seconds")
                
                if validation['error']:
                    print(f"  ⚠️  Validation Error: {validation['error']}")
                
                # Determine if test passed
                if validation['exists'] and validation['size_bytes'] > 1000 and validation['is_readable']:
                    print(f"✅ File validation PASSED - TEST SUCCESSFUL")
                    result["success"] = True
                else:
                    print(f"❌ File validation FAILED")
                    result["success"] = False
                    result["error_message"] = "Invalid or corrupted output file"
                    
                # Copy file to persistent location for manual inspection
                try:
                    import shutil
                    persistent_name = f"test_output_{test_number}_{test_case['name'].replace(' ', '_').replace('/', '_')}.wav"
                    persistent_path = os.path.join(os.getcwd(), persistent_name)
                    shutil.copy2(output_file_path, persistent_path)
                    print(f"📋 Copied output file to: {persistent_path}")
                    result["persistent_copy"] = persistent_path
                except Exception as copy_error:
                    print(f"⚠️  Could not copy file for inspection: {copy_error}")
            
            print(f"\n⏱️  Execution time: {result['execution_time']:.2f} seconds")
            
    except Exception as e:
        end_time = time.time()
        result["execution_time"] = end_time - start_time
        result["success"] = False
        result["error_message"] = str(e)
        print(f"\n💥 EXCEPTION during test: {e}")
        import traceback
        traceback.print_exc()
        
        if test_case['expected'] == "FAIL_GRACEFULLY":
            print(f"✅ Expected graceful failure - TEST PASSED")
            result["success"] = True
    
    return result

def run_ffmpeg_check():
    """Check if ffmpeg is available and working."""
    print("🔧 Checking ffmpeg availability...")
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ ffmpeg found: {version_line}")
            return True
        else:
            print(f"❌ ffmpeg returned error code: {result.returncode}")
            return False
    except FileNotFoundError:
        print("❌ ffmpeg not found in PATH")
        return False
    except Exception as e:
        print(f"❌ Error checking ffmpeg: {e}")
        return False

def main():
    """Main test runner."""
    print("🚀 YouTube URL Processing Test Suite")
    print("="*80)
    
    # Check prerequisites
    if not run_ffmpeg_check():
        print("\n⚠️  WARNING: ffmpeg not available. Tests may fail.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    print(f"\n📋 Running {len(TEST_CASES)} test cases...")
    
    results = []
    start_time = time.time()
    
    # Run all tests
    for i, test_case in enumerate(TEST_CASES, 1):
        try:
            result = test_single_url(test_case, i, len(TEST_CASES))
            results.append(result)
        except KeyboardInterrupt:
            print(f"\n⚠️  Test interrupted by user")
            break
        except Exception as e:
            print(f"\n💥 Critical error in test {i}: {e}")
            import traceback
            traceback.print_exc()
    
    # Print summary
    total_time = time.time() - start_time
    print(f"\n{'='*80}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total Time: {total_time:.2f} seconds")
    
    print(f"\n📝 Detailed Results:")
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        time_str = f"{result['execution_time']:.1f}s"
        print(f"  {status} {result['test_name']} ({time_str})")
        if result['error_message']:
            print(f"      Error: {result['error_message']}")
        if result.get('persistent_copy'):
            print(f"      Output: {result['persistent_copy']}")
    
    # Specific analysis for failing cases
    failing_results = [r for r in results if not r['success'] and r['expected'] != "FAIL_GRACEFULLY"]
    if failing_results:
        print(f"\n🔍 ANALYSIS OF FAILURES:")
        for result in failing_results:
            print(f"\n❌ {result['test_name']}:")
            print(f"   URL: {result['url']}")
            print(f"   Error: {result['error_message']}")
            if result['file_validation']:
                v = result['file_validation']
                print(f"   File exists: {v['exists']}, Size: {v['size_bytes']}, Readable: {v['is_readable']}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    if failed > 0:
        print("- Check the detailed console output above for specific yt-dlp errors")
        print("- Examine any persistent output files created in the current directory")
        print("- Look for patterns in which types of videos fail vs succeed")
        print("- Pay attention to yt-dlp verbose output and ffmpeg postprocessor messages")
    else:
        print("- All tests passed! The issue may be specific to the Streamlit Cloud environment")
        print("- Consider network, permissions, or dependency version differences")

if __name__ == "__main__":
    main() 