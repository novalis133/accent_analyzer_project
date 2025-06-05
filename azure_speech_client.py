import os
import json
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
    # Try Streamlit secrets first (for deployed app)
    try:
        speech_key = st.secrets.get("AZURE_SPEECH_KEY")
        speech_region = st.secrets.get("AZURE_SPEECH_REGION")
        if speech_key and speech_region:
            return speech_key, speech_region
    except Exception:
        # st.secrets not available (local development)
        pass
    
    # Fallback to environment variables (for local development)
    speech_key = os.getenv('AZURE_SPEECH_KEY')
    speech_region = os.getenv('AZURE_SPEECH_REGION')
    
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
    try:
        # Get Azure credentials
        speech_key, speech_region = get_azure_credentials()
        
        if not speech_key or not speech_region:
            print("Azure Speech API key or region not found")
            return {
                "detected_locale": None,
                "transcription_confidence": 0.0,
                "transcript_text": "",
                "error": "Azure Speech API credentials not configured. Please check your secrets/environment variables."
            }
        
        # Verify audio file exists and is not empty
        if not os.path.exists(audio_filepath):
            print(f"Audio file not found: {audio_filepath}")
            return None
            
        if os.path.getsize(audio_filepath) == 0:
            print(f"Audio file is empty: {audio_filepath}")
            return None
        
        print(f"Analyzing audio file: {audio_filepath}")
        
        # Configure Speech SDK
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        
        # Enable detailed output format
        speech_config.set_property_by_name("speechsdk.speech.recognition.outputFormat", "Detailed")
        
        # Configure Language Identification for English variants
        auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=["en-US", "en-GB", "en-AU", "en-CA", "en-IN", "en-NZ", "en-ZA"]
        )
        
        # Create audio configuration
        audio_input = speechsdk.audio.AudioConfig(filename=audio_filepath)
        
        # Create speech recognizer with language detection
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            auto_detect_source_language_config=auto_detect_source_language_config,
            audio_config=audio_input
        )
        
        print("Starting Azure Speech recognition...")
        
        # Perform recognition
        result = speech_recognizer.recognize_once()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Speech recognition successful")
            
            # Get detected language
            auto_detect_result = speechsdk.AutoDetectSourceLanguageResult(result)
            detected_language = auto_detect_result.language if auto_detect_result else None
            
            # Extract confidence from detailed JSON if available
            confidence = 0.0
            try:
                if result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_Json):
                    json_result = json.loads(result.properties[speechsdk.PropertyId.SpeechServiceResponse_Json])
                    
                    # Try to extract confidence from different possible locations in the JSON
                    if 'NBest' in json_result and len(json_result['NBest']) > 0:
                        raw_confidence = json_result['NBest'][0].get('Confidence', 0.0)
                        confidence = normalize_confidence_to_float(raw_confidence)
                    elif 'confidence' in json_result:
                        raw_confidence = json_result['confidence']
                        confidence = normalize_confidence_to_float(raw_confidence)
                    else:
                        # Default confidence based on result reason
                        confidence = 0.85  # High confidence for successful recognition
                        
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Could not parse confidence from JSON: {e}")
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
            print("No speech could be recognized")
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
            print(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
            return {
                "detected_locale": None,
                "transcription_confidence": 0.0,
                "transcript_text": "",
                "error": f"Recognition canceled: {cancellation_details.reason}",
                "error_details": cancellation_details.error_details if cancellation_details.reason == speechsdk.CancellationReason.Error else None
            }
            
    except Exception as e:
        print(f"Error in Azure Speech analysis: {str(e)}")
        return {
            "detected_locale": None,
            "transcription_confidence": 0.0,
            "transcript_text": "",
            "error": str(e)
        }


def normalize_confidence(confidence_value) -> float:
    """
    Legacy function for backward compatibility.
    Use normalize_confidence_to_float instead.
    """
    return normalize_confidence_to_float(confidence_value) 