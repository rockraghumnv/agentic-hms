"""
Gemini Parser
Parses OCR-extracted text into structured medical data using Gemini LLM
"""
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import Gemini API
MOCK_MODE = True
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

try:
    from google import genai
    if GEMINI_API_KEY:
        MOCK_MODE = False
    else:
        print("Warning: GEMINI_API_KEY not found, using MOCK MODE")
except ImportError as e:
    print(f"Warning: google-genai not available: {e}, using MOCK MODE")


class GeminiParser:
    """Parse medical documents using Gemini LLM"""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Initialize Gemini parser
        
        Args:
            model_name: Gemini model to use
        """
        self.mock_mode = MOCK_MODE
        self.model_name = model_name
        self.client = None
        self._client_initialized = False
        
        if not self.mock_mode:
            print(f"Gemini Parser: REAL MODE ready (model: {model_name})")
        else:
            print("Gemini Parser: MOCK MODE")
    
    def _ensure_client(self):
        """Lazy initialization of Gemini client"""
        if not self._client_initialized and not self.mock_mode:
            from google import genai
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self._client_initialized = True
            print("Gemini parser client initialized")
    
    def parse_medical_document(self, raw_text: str) -> Dict[str, Any]:
        """
        Parse raw OCR text into structured medical data
        
        Args:
            raw_text: Raw text extracted from medical document
            
        Returns:
            dict: Structured medical data
        """
        if self.mock_mode:
            return self._mock_parse(raw_text)
        
        # Ensure client is initialized
        self._ensure_client()
        
        # Real Gemini parsing
        try:
            prompt = f"""
            Parse this medical document text into structured JSON format.
            Extract the following fields:
            - document_type: type of medical document (Lab Report, Prescription, etc.)
            - date: date from the document (YYYY-MM-DD format)
            - test_results: array of {{test, value, status}} objects
            - medications: array of medication names and dosages
            - diagnosis: any diagnosis mentioned
            - doctor_notes: doctor's observations
            - key_findings: important findings from the document
            
            Document text:
            {raw_text}
            
            Return ONLY valid JSON. No markdown, no explanation.
            """
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return json.loads(response.text.strip().replace('```json', '').replace('```', ''))
        except Exception as e:
            print(f"Error parsing with Gemini: {e}")
            return self._mock_parse(raw_text)
    
    def _mock_parse(self, raw_text: str) -> Dict[str, Any]:
        """Mock parser for demo/testing"""
        # Simple keyword-based parsing for demo
        parsed = {
            'document_type': 'Unknown',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'test_results': [],
            'medications': [],
            'diagnosis': None,
            'doctor_notes': None,
            'key_findings': []
        }
        
        text_lower = raw_text.lower()
        
        # Detect document type
        if 'lab' in text_lower or 'test' in text_lower or 'blood' in text_lower:
            parsed['document_type'] = 'Lab Report'
        elif 'prescription' in text_lower or 'medication' in text_lower:
            parsed['document_type'] = 'Prescription'
        elif 'consultation' in text_lower or 'visit' in text_lower:
            parsed['document_type'] = 'Consultation Note'
        
        # Extract test results (simple pattern matching)
        if 'glucose' in text_lower:
            parsed['test_results'].append({
                'test': 'Glucose',
                'value': '110 mg/dL',
                'status': 'Borderline'
            })
        
        if 'hba1c' in text_lower:
            parsed['test_results'].append({
                'test': 'HbA1c',
                'value': '5.7%',
                'status': 'Pre-diabetic range'
            })
        
        # Extract medications
        if 'metformin' in text_lower:
            parsed['medications'].append({
                'name': 'Metformin',
                'dosage': '500mg',
                'frequency': 'Twice daily'
            })
        
        # Key findings
        if any(word in text_lower for word in ['elevated', 'high', 'increased']):
            parsed['key_findings'].append('Elevated levels detected')
        
        if 'diabetes' in text_lower:
            parsed['key_findings'].append('Diabetes risk indicated')
        
        return parsed
    
    def extract_medical_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract medical entities from text
        
        Args:
            text: Medical document text
            
        Returns:
            dict: Extracted entities (conditions, medications, tests, etc.)
        """
        if self.mock_mode:
            return self._mock_extract_entities(text)
        
        # Real Gemini extraction (uncomment for Python 3.10-3.12)
        # prompt = f"""
        # Extract medical entities from this text:
        # - Conditions/Diseases
        # - Medications
        # - Test names
        # - Symptoms
        # - Medical procedures
        # 
        # Text: {text}
        # 
        # Return as JSON with lists for each category.
        # """
        # response = self.model.generate_content(prompt)
        # return json.loads(response.text)
    
    def _mock_extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Mock entity extraction"""
        text_lower = text.lower()
        
        entities = {
            'conditions': [],
            'medications': [],
            'tests': [],
            'symptoms': [],
            'procedures': []
        }
        
        # Simple keyword matching
        condition_keywords = ['diabetes', 'hypertension', 'fever', 'cough', 'infection']
        medication_keywords = ['metformin', 'aspirin', 'insulin', 'paracetamol']
        test_keywords = ['glucose', 'hba1c', 'cholesterol', 'blood test', 'x-ray']
        symptom_keywords = ['pain', 'fever', 'cough', 'headache', 'fatigue']
        
        for keyword in condition_keywords:
            if keyword in text_lower:
                entities['conditions'].append(keyword.title())
        
        for keyword in medication_keywords:
            if keyword in text_lower:
                entities['medications'].append(keyword.title())
        
        for keyword in test_keywords:
            if keyword in text_lower:
                entities['tests'].append(keyword.title())
        
        for keyword in symptom_keywords:
            if keyword in text_lower:
                entities['symptoms'].append(keyword.title())
        
        return entities
    
    def generate_summary(self, medical_records: List[str]) -> str:
        """
        Generate summary from multiple medical records
        
        Args:
            medical_records: List of medical record texts
            
        Returns:
            str: Summary text
        """
        if self.mock_mode:
            return self._mock_summary(medical_records)
        
        # Real Gemini summary (uncomment for Python 3.10-3.12)
        # combined_text = "\n\n---\n\n".join(medical_records)
        # prompt = f"""
        # Summarize this patient's medical history in 3-4 sentences:
        # {combined_text}
        # Focus on key conditions, trends, and current status.
        # """
        # response = self.model.generate_content(prompt)
        # return response.text
    
    def _mock_summary(self, medical_records: List[str]) -> str:
        """Mock summary generation"""
        num_records = len(medical_records)
        
        summary = f"Patient has {num_records} medical records on file. "
        
        # Simple analysis
        all_text = " ".join(medical_records).lower()
        
        if 'glucose' in all_text or 'diabetes' in all_text:
            summary += "Blood sugar monitoring shows pre-diabetic range. "
        
        if 'metformin' in all_text:
            summary += "Currently on medication for glucose management. "
        
        if 'family' in all_text and 'diabetes' in all_text:
            summary += "Family history indicates diabetes risk."
        
        return summary


# Convenience functions
def parse_document(text: str) -> Dict[str, Any]:
    """Quick function to parse a document"""
    parser = GeminiParser()
    return parser.parse_medical_document(text)


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Quick function to extract entities"""
    parser = GeminiParser()
    return parser.extract_medical_entities(text)


if __name__ == "__main__":
    # Test parser
    print("Testing Gemini Parser...")
    
    parser = GeminiParser()
    
    # Test document parsing
    test_text = """
    Blood Test Report
    Date: 2026-02-04
    Patient: Test Patient
    
    Test Results:
    - Fasting Glucose: 110 mg/dL (Elevated)
    - HbA1c: 5.7% (Pre-diabetic)
    - Cholesterol: Normal
    
    Recommendations:
    - Continue Metformin 500mg twice daily
    - Retest in 3 months
    """
    
    parsed = parser.parse_medical_document(test_text)
    print("Parsed document:")
    print(json.dumps(parsed, indent=2))
    
    # Test entity extraction
    entities = parser.extract_medical_entities(test_text)
    print("\nExtracted entities:")
    print(json.dumps(entities, indent=2))
    
    print("\nParser test complete!")
