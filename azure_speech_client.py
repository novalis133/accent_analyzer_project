import os
import json
import traceback
from typing import Optional, Dict
import azure.cognitiveservices.speech as speechsdk
import streamlit as st
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()


def get_azure_credentials():
    """
    Get Azure credentials from Streamlit secrets (deployed) or environment variables (local).
    
    Returns:
        Tuple of (speech_key, speech_region) or (None, None) if not found
    """
    print("DEBUG_AZURE_CREDS: Getting Azure credentials...")
    
    # Try Streamlit secrets first (for deployed app)
    try:
        speech_key = st.secrets.get("AZURE_SPEECH_KEY")
        speech_region = st.secrets.get("AZURE_SPEECH_REGION")
        if speech_key and speech_region:
            print("DEBUG_AZURE_CREDS: Found credentials in Streamlit secrets")
            print(f"DEBUG_AZURE_CREDS: Region = {speech_region}")
            print(f"DEBUG_AZURE_CREDS: Key length = {len(speech_key) if speech_key else 0}")
            return speech_key, speech_region
    except Exception as e:
        print(f"DEBUG_AZURE_CREDS: st.secrets not available (local development): {e}")
    
    # Fallback to environment variables (for local development)
    speech_key = os.getenv('AZURE_SPEECH_KEY')
    speech_region = os.getenv('AZURE_SPEECH_REGION')
    
    if speech_key and speech_region:
        print("DEBUG_AZURE_CREDS: Found credentials in environment variables")
        print(f"DEBUG_AZURE_CREDS: Region = {speech_region}")
        print(f"DEBUG_AZURE_CREDS: Key length = {len(speech_key)}")
    else:
        print("DEBUG_AZURE_CREDS: No credentials found in environment variables")
    
    return speech_key, speech_region


def normalize_confidence_to_float(confidence_value) -> float:
    """
    Normalize confidence value to a float between 0.0 and 1.0.
    
    Args:
        confidence_value: Confidence value (float, string, or other)
        
    Returns:
        Normalized confidence as float between 0.0 and 1.0
    """
    if isinstance(confidence_value, str):
        confidence_map = {
            "high": 0.95,
            "medium": 0.70,
            "low": 0.40
        }
        return confidence_map.get(confidence_value.lower(), 0.5)
    
    elif isinstance(confidence_value, (int, float)):
        # Ensure it's between 0 and 1
        return max(0.0, min(1.0, float(confidence_value)))
    
    else:
        return 0.5  # Default moderate confidence


def analyze_audio_with_azure(audio_filepath: str) -> Optional[Dict]:
    """
    Analyze audio using Azure Speech Services with Language Identification.
    
    Args:
        audio_filepath: Path to the WAV audio file
        
    Returns:
        Dictionary with analysis results or None if failed
    """
    print(f"DEBUG_AZURE_START: Starting Azure Speech analysis")
    print(f"DEBUG_AZURE_INPUT_FILE: audio_filepath = {audio_filepath}")
    
    try:
        # Verify audio file exists and get info
        if not os.path.exists(audio_filepath):
            print(f"DEBUG_AZURE_ERROR: Audio file does not exist: {audio_filepath}")
            return {
                "detected_locale": None,
                "transcription_confidence": 0.0,
                "transcript_text": "",
                "error": f"Audio file not found: {audio_filepath}"
            }
            
        file_size = os.path.getsize(audio_filepath)
        print(f"DEBUG_AZURE_FILE_SIZE: {file_size} bytes")
        
        if file_size == 0:
            print(f"DEBUG_AZURE_ERROR: Audio file is empty: {audio_filepath}")
            return {
                "detected_locale": None,
                "transcription_confidence": 0.0,
                "transcript_text": "",
                "error": f"Audio file is empty: {audio_filepath}"
            }
        
        # Get Azure credentials
        speech_key, speech_region = get_azure_credentials()
        
        if not speech_key or not speech_region:
            print("DEBUG_AZURE_ERROR: Azure credentials not found")
            return {
                "detected_locale": None,
                "transcription_confidence": 0.0,
                "transcript_text": "",
                "error": "Azure Speech API credentials not configured. Please check your secrets/environment variables."
            }
        
        print(f"DEBUG_AZURE_CONFIG: Configuring Speech SDK...")
        
        # Configure Speech SDK
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        
        # Enable detailed output format
        speech_config.set_property_by_name("speechsdk.speech.recognition.outputFormat", "Detailed")
        
        print(f"DEBUG_AZURE_LANGUAGE_CONFIG: Setting up language identification...")
        
        # Configure Language Identification for English variants
        # NOTE: Azure Speech Services DetectAudioAtStart mode supports maximum 4 languages
        auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=["en-US", "en-GB", "en-AU", "en-CA"]  # Reduced to 4 languages as per Azure limitation
        )
        print(f"DEBUG_AZURE_LANGUAGE_LIST: Using 4 languages: en-US, en-GB, en-AU, en-CA")
        
        print(f"DEBUG_AZURE_AUDIO_CONFIG: Creating audio configuration...")
        
        # Create audio configuration
        audio_input = speechsdk.audio.AudioConfig(filename=audio_filepath)
        
        print(f"DEBUG_AZURE_RECOGNIZER: Creating speech recognizer...")
        
        # Create speech recognizer with language detection
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            auto_detect_source_language_config=auto_detect_source_language_config,
            audio_config=audio_input
        )
        
        print("DEBUG_AZURE_RECOGNITION: Starting Azure Speech recognition...")
        
        # Perform recognition
        result = speech_recognizer.recognize_once()
        
        print(f"DEBUG_AZURE_RESULT_REASON: result.reason = {result.reason}")
        print(f"DEBUG_AZURE_RESULT_ID: result.result_id = {result.result_id}")
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("DEBUG_AZURE_SUCCESS: Speech recognition successful")
            print(f"DEBUG_AZURE_TRANSCRIPT_LENGTH: {len(result.text)} characters")
            
            # Get detected language
            auto_detect_result = speechsdk.AutoDetectSourceLanguageResult(result)
            detected_language = auto_detect_result.language if auto_detect_result else None
            print(f"DEBUG_AZURE_DETECTED_LANGUAGE: {detected_language}")
            
            # Extract confidence from detailed JSON if available
            confidence = 0.0
            try:
                if result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_Json):
                    json_result = json.loads(result.properties[speechsdk.PropertyId.SpeechServiceResponse_Json])
                    print(f"DEBUG_AZURE_JSON_RESPONSE: {json.dumps(json_result, indent=2)}")
                    
                    # Try to extract confidence from different possible locations in the JSON
                    if 'NBest' in json_result and len(json_result['NBest']) > 0:
                        raw_confidence = json_result['NBest'][0].get('Confidence', 0.0)
                        confidence = normalize_confidence_to_float(raw_confidence)
                        print(f"DEBUG_AZURE_CONFIDENCE_NBEST: raw={raw_confidence}, normalized={confidence}")
                    elif 'confidence' in json_result:
                        raw_confidence = json_result['confidence']
                        confidence = normalize_confidence_to_float(raw_confidence)
                        print(f"DEBUG_AZURE_CONFIDENCE_DIRECT: raw={raw_confidence}, normalized={confidence}")
                    else:
                        # Default confidence based on result reason
                        confidence = 0.85  # High confidence for successful recognition
                        print(f"DEBUG_AZURE_CONFIDENCE_DEFAULT: {confidence}")
                        
            except (json.JSONDecodeError, KeyError) as e:
                print(f"DEBUG_AZURE_JSON_ERROR: Could not parse confidence from JSON: {e}")
                confidence = 0.80  # Default moderate-high confidence
            
            return {
                "detected_locale": detected_language,
                "transcription_confidence": confidence,  # Always a float 0.0-1.0
                "transcript_text": result.text,
                "raw_azure_response": {
                    "reason": str(result.reason),
                    "result_id": result.result_id
                }
            }
            
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("DEBUG_AZURE_NO_MATCH: No speech could be recognized")
            if result.no_match_details:
                print(f"DEBUG_AZURE_NO_MATCH_DETAILS: {result.no_match_details}")
            
            return {
                "detected_locale": None,
                "transcription_confidence": 0.0,
                "transcript_text": "",
                "raw_azure_response": {
                    "reason": str(result.reason),
                    "no_match_details": str(result.no_match_details) if result.no_match_details else None
                }
            }
            
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"DEBUG_AZURE_CANCELED: Speech Recognition canceled")
            print(f"DEBUG_AZURE_CANCEL_REASON: {cancellation_details.reason}")
            
            error_details_str = None
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                error_details_str = str(cancellation_details.error_details) if cancellation_details.error_details else "No error details available"
                # This is the key line for debugging - using distinct prefix
                print(f"AZURE_SPEECH_CANCELLATION_ERROR_DETAILS: {error_details_str}")
            
            return {
                "detected_locale": None,
                "transcription_confidence": 0.0,
                "transcript_text": "",
                "error": f"Azure recognition canceled. Reason: {cancellation_details.reason}. Details: {error_details_str if error_details_str else 'N/A'}",
                "azure_error_details_debug": error_details_str,
                "cancellation_reason": str(cancellation_details.reason)
            }
        else:
            print(f"DEBUG_AZURE_UNKNOWN_REASON: Unknown result reason: {result.reason}")
            return {
                "detected_locale": None,
                "transcription_confidence": 0.0,
                "transcript_text": "",
                "error": f"Unknown Azure result reason: {result.reason}"
            }
            
    except Exception as e:
        print(f"DEBUG_AZURE_EXCEPTION: Error in Azure Speech analysis: {str(e)}")
        traceback.print_exc()
        return {
            "detected_locale": None,
            "transcription_confidence": 0.0,
            "transcript_text": "",
            "error": str(e),
            "exception_details": traceback.format_exc()
        }


def normalize_confidence(confidence_value) -> float:
    """
    Legacy function for backward compatibility.
    Use normalize_confidence_to_float instead.
    """
    return normalize_confidence_to_float(confidence_value) 