from typing import Dict
from azure_speech_client import normalize_confidence_to_float


def determine_accent_and_confidence(azure_analysis_result: Dict) -> Dict:
    """
    Determine accent classification and confidence based on Azure analysis results.
    
    Args:
        azure_analysis_result: Dictionary from Azure Speech analysis
        
    Returns:
        Dictionary with accent classification, confidence, summary, and debug info
    """
    
    # Locale to accent mapping
    locale_to_accent = {
        "en-US": "American English",
        "en-GB": "British English", 
        "en-AU": "Australian English",
        "en-CA": "Canadian English",
        "en-IN": "Indian English",
        "en-NZ": "New Zealand English",
        "en-ZA": "South African English",
        "en-IE": "Irish English",
        "en-SG": "Singaporean English"
    }
    
    detected_locale = azure_analysis_result.get("detected_locale")
    transcription_confidence = azure_analysis_result.get("transcription_confidence", 0.0)
    transcript_text = azure_analysis_result.get("transcript_text", "")
    error_info = azure_analysis_result.get("error")
    
    # Normalize confidence to 0.0-1.0 range (should already be normalized from Azure client)
    normalized_confidence = normalize_confidence_to_float(transcription_confidence)
    
    # Create debug info
    debug_info = {
        "raw_detected_locale": detected_locale,
        "raw_transcription_confidence": transcription_confidence,
        "normalized_confidence": normalized_confidence,
        "transcript_length": len(transcript_text) if transcript_text else 0,
        "azure_error": error_info,
        "raw_azure_response": azure_analysis_result.get("raw_azure_response")
    }
    
    # Handle error cases first
    if error_info:
        accent_classification = "Analysis Failed"
        confidence_in_english_accent = 0
        summary_explanation = f"Analysis failed: {error_info}"
        
    # Determine accent classification
    elif not detected_locale:
        accent_classification = "Undetermined"
        confidence_in_english_accent = 0
        summary_explanation = "Could not detect any speech or language."
        
    elif detected_locale == "en":
        # Generic English without regional specification
        accent_classification = "English (Undetermined Region)"
        confidence_in_english_accent = int(normalized_confidence * 100)
        summary_explanation = f"Detected generic English. Confidence in English: {confidence_in_english_accent}%. Language code: {detected_locale}."
        
    elif detected_locale.startswith("en-"):
        # English with regional specification
        if detected_locale in locale_to_accent:
            accent_classification = locale_to_accent[detected_locale]
        else:
            # Handle unknown English variants
            region_code = detected_locale.split("-")[1] if "-" in detected_locale else "Unknown"
            accent_classification = f"English (Other Regional - {region_code})"
        
        confidence_in_english_accent = int(normalized_confidence * 100)
        summary_explanation = f"Detected accent: {accent_classification}. Confidence in English: {confidence_in_english_accent}%. Language code: {detected_locale}."
        
    else:
        # Non-English language detected
        accent_classification = "Non-English"
        confidence_in_english_accent = max(0, min(10, int(normalized_confidence * 10)))  # Very low confidence for English
        summary_explanation = f"Detected non-English language. Language code: {detected_locale}. This tool is designed for English accent analysis."
    
    # Additional context if we have transcript
    if transcript_text and len(transcript_text.strip()) > 0:
        word_count = len(transcript_text.split())
        summary_explanation += f" Transcript contains {word_count} words."
        debug_info["word_count"] = word_count
    
    # Calculate processing quality score
    processing_quality = calculate_processing_quality(
        confidence_in_english_accent, 
        len(transcript_text) if transcript_text else 0,
        detected_locale
    )
    
    return {
        "accent_classification": accent_classification,
        "confidence_in_english_accent": confidence_in_english_accent,
        "summary_explanation": summary_explanation,
        "transcript_text": transcript_text,
        "processing_quality": processing_quality,
        "debug_info": debug_info
    }


def calculate_processing_quality(confidence: int, transcript_length: int, locale: str) -> str:
    """
    Calculate an overall processing quality assessment.
    
    Args:
        confidence: Confidence score (0-100)
        transcript_length: Length of transcript text
        locale: Detected locale
        
    Returns:
        Quality assessment string
    """
    if confidence == 0:
        return "Poor - No speech detected"
    elif confidence < 30:
        return "Poor - Low confidence"
    elif confidence < 60:
        if transcript_length < 10:
            return "Fair - Moderate confidence, short audio"
        else:
            return "Good - Moderate confidence"
    elif confidence < 80:
        if transcript_length > 50:
            return "Very Good - High confidence, sufficient audio"
        else:
            return "Good - High confidence"
    else:
        if transcript_length > 50:
            return "Excellent - Very high confidence, sufficient audio"
        else:
            return "Very Good - Very high confidence"


def get_accent_description(accent_classification: str) -> str:
    """
    Get a brief description of the accent type.
    
    Args:
        accent_classification: The classified accent
        
    Returns:
        Description string
    """
    descriptions = {
        "American English": "North American English, commonly heard in the United States. Features rhotic pronunciation and distinctive vowel patterns.",
        "British English": "English as spoken in the United Kingdom, including Received Pronunciation and regional variants. Often non-rhotic with distinct vowel sounds.",
        "Australian English": "English as spoken in Australia, with distinctive vowel sounds and unique pronunciation patterns influenced by British English.",
        "Canadian English": "North American English with some British influences, spoken in Canada. Similar to American English but with some distinct features.",
        "Indian English": "English as spoken in India, influenced by local languages. Features unique pronunciation patterns and vocabulary.",
        "New Zealand English": "English as spoken in New Zealand, similar to Australian but with distinct characteristics, particularly in vowel pronunciation.",
        "South African English": "English as spoken in South Africa, with unique characteristics influenced by Afrikaans and local languages.",
        "Irish English": "English as spoken in Ireland, with Celtic influences and distinctive pronunciation patterns.",
        "Singaporean English": "English as spoken in Singapore, influenced by various local languages and featuring unique pronunciation patterns."
    }
    
    return descriptions.get(accent_classification, "Regional variant of English with unique characteristics.")


def get_supported_accents() -> list:
    """
    Get list of supported accent classifications.
    
    Returns:
        List of supported accent names
    """
    return [
        "American English",
        "British English", 
        "Australian English",
        "Canadian English",
        "Indian English",
        "New Zealand English",
        "South African English",
        "Irish English",
        "Singaporean English"
    ] 