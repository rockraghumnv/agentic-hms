"""
Gemini Vision OCR Processor
Uses Gemini-2.5-flash with Vision API to extract text from medical images
NOTE: Runs in MOCK MODE for Python 3.13 compatibility
"""
import os
from typing import List, Dict, Optional
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Gemini API
GENAI_AVAILABLE = False
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

try:
    from google import genai
    from google.genai import types
    if GEMINI_API_KEY:
        GENAI_AVAILABLE = True
    else:
        print("Warning: GEMINI_API_KEY not found in .env file")
except ImportError as e:
    print(f"Warning: google-genai not available: {e}")

print(f"Gemini Vision OCR: {'REAL MODE' if GENAI_AVAILABLE else 'MOCK MODE (Demo)'}")


class GeminiVisionOCR:
    """Gemini Vision API wrapper for medical document OCR"""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Initialize Gemini Vision OCR
        
        Args:
            model_name: Gemini model to use (default: gemini-2.5-flash)
        """
        self.model_name = model_name
        self.mock_mode = not GENAI_AVAILABLE
        self.client = None
        self._client_initialized = False
        
        if GENAI_AVAILABLE:
            print(f"Gemini Vision: REAL MODE ready (model: {model_name})")
        else:
            print("Running in MOCK MODE - using simulated medical data extraction")
    
    def _ensure_client(self):
        """Lazy initialization of Gemini client"""
        if not self._client_initialized and GENAI_AVAILABLE:
            from google import genai
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self._client_initialized = True
            print("Gemini client initialized")
        
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract all text from medical image using Gemini Vision
        
        Args:
            image_path: Path to image file
            
        Returns:
            str: Extracted text content
        """
        # Mock mode for demo/testing
        if not GENAI_AVAILABLE:
            return f"[MOCK MODE] Extracted text from {Path(image_path).name}:\nBlood Test Report\nDate: 2026-02-04\nGlucose: 110 mg/dL\nHbA1c: 5.7%\nCholesterol: Normal"
        
        # Ensure client is initialized
        self._ensure_client()
        
        try:
            # Load image
            image = Image.open(image_path)
            
            # Craft prompt for medical document extraction
            prompt = """
            You are a medical document OCR system. Extract ALL text from this medical image.
            Include:
            - Test names and values
            - Dates
            - Patient information (if visible)
            - Doctor notes
            - Medications and dosages
            - Lab results with units
            - Any other medical information
            
            Format the output clearly with proper structure.
            If this is not a medical document, state that clearly.
            """
            
            # Generate content with vision using new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, image]
            )
            
            return response.text
            
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def extract_structured_data(self, image_path: str) -> Dict[str, any]:
        """
        Extract structured medical data from image
        
        Args:
            image_path: Path to image file
            
        Returns:
            dict: Structured medical data
        """
        # Mock mode for demo/testing
        if not self.model:
            return {
                "raw_text": f"[MOCK] Medical document from {Path(image_path).name}\nTest results extracted successfully",
                "extraction_successful": True,
                "document_path": image_path,
                "mock_mode": True
            }
        
        try:
            image = Image.open(image_path)
            
            prompt = """
            Extract medical information from this document and return it in a structured format.
            
            Identify and extract:
            1. Document Type (Lab Report, Prescription, Consultation Note, etc.)
            2. Date of document
            3. Patient name (if visible)
            4. Test Results with values and units
            5. Medications with dosage
            6. Doctor's recommendations
            7. Diagnosis (if mentioned)
            8. Any concerning findings
            
            Format as clear key-value pairs.
            If information is not available, mark as "Not found".
            """
            
            response = self.model.generate_content([prompt, image])
            
            # Parse response into structured format
            # For demo, return text; in production, parse into proper dict
            return {
                "raw_text": response.text,
                "extraction_successful": True,
                "document_path": image_path
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "extraction_successful": False,
                "document_path": image_path
            }
    
    def batch_extract(self, image_paths: List[str]) -> List[Dict[str, any]]:
        """
        Extract text from multiple images
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of extraction results
        """
        results = []
        for image_path in image_paths:
            result = self.extract_structured_data(image_path)
            results.append(result)
        return results


# Convenience functions
def extract_from_image(image_path: str) -> str:
    """
    Quick function to extract text from single image
    
    Args:
        image_path: Path to image file
        
    Returns:
        str: Extracted text
    """
    ocr = GeminiVisionOCR()
    return ocr.extract_text_from_image(image_path)


def extract_structured(image_path: str) -> Dict[str, any]:
    """
    Quick function to extract structured data from single image
    
    Args:
        image_path: Path to image file
        
    Returns:
        dict: Structured medical data
    """
    ocr = GeminiVisionOCR()
    return ocr.extract_structured_data(image_path)


if __name__ == "__main__":
    # Test OCR
    print("Gemini Vision OCR Initialized")
    print("Note: Requires valid GEMINI_API_KEY in .env file")
    print("Ready to process medical images!")
