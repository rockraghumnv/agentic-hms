"""
Chat Handler for Medical Q&A
Handles patient queries using medical history and Gemini LLM
"""
import os
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

from vector_store import MedicalVectorStore
from gemini_parser import GeminiParser
from mock_db import get_patient_data, patient_exists

load_dotenv()

# Import Gemini for chat responses
GEMINI_AVAILABLE = False
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

try:
    from google import genai
    if GEMINI_API_KEY:
        GEMINI_AVAILABLE = True
except ImportError:
    pass


class ChatHandler:
    """Handle medical chat conversations with context"""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """Initialize chat handler with vector store and parser"""
        self.vector_store = MedicalVectorStore()
        self.parser = GeminiParser()
        self.conversation_history = {}  # Store by patient_id
        self.model_name = model_name
        self.gemini_client = None
        self._client_initialized = False
        
        if GEMINI_AVAILABLE:
            print(f"ChatHandler: REAL MODE ready (model: {model_name})")
        else:
            print("ChatHandler: Using MOCK MODE")
    
    def _ensure_client(self):
        """Lazy initialization of Gemini client"""
        if not self._client_initialized and GEMINI_AVAILABLE:
            from google import genai
            self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
            self._client_initialized = True
            print("Chat client initialized")
        
    def process_message(
        self,
        patient_id: str,
        message: str,
        language: str = 'english'
    ) -> Dict:
        """
        Process patient message and generate response
        
        Args:
            patient_id: Unique patient identifier
            message: User's message
            language: Response language ('english' or 'kannada')
            
        Returns:
            dict: Response data with message and metadata
        """
        # Verify patient exists
        if not patient_exists(patient_id):
            return {
                'success': False,
                'error': 'Patient not found',
                'response': 'Patient ID not found in our records.'
            }
        
        # Get patient medical history from vector store
        patient_records = self.vector_store.get_patient_records(patient_id)
        
        # Query relevant history using semantic search
        relevant_records = self.vector_store.query_patient_history(
            patient_id=patient_id,
            query_text=message,
            n_results=5
        )
        
        # Get patient data from mock DB
        patient_data = get_patient_data(patient_id)
        
        # Build context
        context = self._build_context(patient_data, relevant_records)
        
        # Generate response (mock mode)
        response_text = self._generate_response(
            message=message,
            context=context,
            language=language
        )
        
        # Store in conversation history
        message_id = self._store_conversation(patient_id, message, response_text)
        
        return {
            'success': True,
            'response': response_text,
            'message_id': message_id,
            'language': language,
            'context_used': len(relevant_records)
        }
    
    def _build_context(self, patient_data: Dict, relevant_records: List[Dict]) -> str:
        """
        Build context string from patient data and relevant records
        
        Args:
            patient_data: Patient information from database
            relevant_records: Relevant medical records from vector search
            
        Returns:
            str: Formatted context
        """
        context = "Patient Medical History:\n\n"
        
        # Add family history if available
        if patient_data and 'family_history' in patient_data:
            context += "Family History:\n"
            for relation, condition in patient_data['family_history'].items():
                if condition and condition.lower() != 'none':
                    context += f"- {relation}: {condition}\n"
            context += "\n"
        
        # Add relevant medical records
        if relevant_records:
            context += "Recent Medical Records:\n"
            for record in relevant_records[:3]:  # Top 3 most relevant
                context += f"- {record['text']}\n"
            context += "\n"
        
        # Add uploaded documents info
        if patient_data and 'uploaded_documents' in patient_data:
            doc_count = patient_data['documents_processed']
            context += f"Total medical documents on file: {doc_count}\n"
        
        return context
    
    def _generate_response(
        self,
        message: str,
        context: str,
        language: str
    ) -> str:
        """
        Generate response using Gemini LLM (or mock)
        
        Args:
            message: User's question
            context: Patient medical context
            language: Response language
            
        Returns:
            str: Generated response
        """
        # Use real Gemini if available
        if GEMINI_AVAILABLE:
            # Ensure client is initialized
            self._ensure_client()
            
            try:
                prompt = f"""You are a helpful medical AI assistant. Based on the patient's medical context, provide clear, helpful guidance.

Patient Medical Context:
{context}

Patient Question: {message}

Instructions:
- Provide medical guidance in {language} language
- Be clear, compassionate, and helpful
- Reference specific data from the context when relevant
- Always recommend consulting a doctor for serious concerns
- If asking about symptoms, provide monitoring guidelines
- If asking about test results, explain what they mean
- Keep response concise but informative

Response:"""
                
                response = self.gemini_client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                print(f"Gemini API error: {e}, falling back to mock")
                # Fall through to mock mode on error
        
        # MOCK MODE RESPONSE (fallback)
        message_lower = message.lower()
        
        # Mock responses based on common queries
        if language == 'kannada':
            if 'fever' in message_lower or 'ಜ್ವರ' in message_lower:
                return "ನಿಮ್ಮ ವೈದ್ಯಕೀಯ ಇತಿಹಾಸದ ಆಧಾರದ ಮೇಲೆ, ನಿಮ್ಮ ಜ್ವರವು ಸೌಮ್ಯವಾಗಿ ಕಂಡುಬರುತ್ತದೆ. ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ, ಸಾಕಷ್ಟು ನೀರು ಕುಡಿಯಿರಿ ಮತ್ತು 24 ಗಂಟೆಗಳ ಕಾಲ ತಾಪಮಾನವನ್ನು ಮೇಲ್ವಿಚಾರಣೆ ಮಾಡಿ."
            elif 'glucose' in message_lower or 'sugar' in message_lower:
                return "ನಿಮ್ಮ ಕೊನೆಯ ರಕ್ತ ಪರೀಕ್ಷೆಯು ಗ್ಲೂಕೋಸ್ ಮಟ್ಟವು ಸ್ವಲ್ಪ ಹೆಚ್ಚಾಗಿದೆ ಎಂದು ತೋರಿಸುತ್ತದೆ. ನಿಮ್ಮ ಕುಟುಂಬದ ಇತಿಹಾಸದಲ್ಲಿ ಮಧುಮೇಹವಿದೆ. ಆರೋಗ್ಯಕರ ಆಹಾರವನ್ನು ಮುಂದುವರಿಸಿ ಮತ್ತು ನಿಯಮಿತವಾಗಿ ವ್ಯಾಯಾಮ ಮಾಡಿ."
            else:
                return "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ನಾನು ಅರ್ಥಮಾಡಿಕೊಂಡಿದ್ದೇನೆ. ನಿಮ್ಮ ವೈದ್ಯಕೀಯ ಇತಿಹಾಸವನ್ನು ಆಧರಿಸಿ, ನಿಮ್ಮ ಸ್ಥಿತಿ ಸ್ಥಿರವಾಗಿದೆ. ಯಾವುದೇ ಕಾಳಜಿ ಇದ್ದರೆ, ದಯವಿಟ್ಟು ನಿಮ್ಮ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ."
        else:  # English
            if 'fever' in message_lower and 'cough' in message_lower:
                response = "Based on your medical history, I see you're experiencing mild fever and cough.\n\n"
                response += "Analysis:\n"
                response += "- No history of respiratory issues in your records\n"
                response += "- Your immunity markers were normal in last test\n"
                response += "- You're currently on Metformin for pre-diabetes\n\n"
                response += "Recommendations:\n"
                response += "1. Monitor temperature for 24 hours\n"
                response += "2. Stay hydrated (8-10 glasses of water)\n"
                response += "3. Rest adequately\n"
                response += "4. Avoid sugar intake\n\n"
                response += "⚠️ Consult doctor if:\n"
                response += "- Fever >101°F or persists >3 days\n"
                response += "- Difficulty breathing\n"
                response += "- Severe chest pain"
                return response
            
            elif 'glucose' in message_lower or 'sugar' in message_lower or 'diabetes' in message_lower:
                response = "Regarding your blood sugar concerns:\n\n"
                response += "From your medical history:\n"
                response += "- Recent glucose levels show upward trend (95 → 110 → 128 mg/dL over 6 months)\n"
                response += "- HbA1c: 5.9% (pre-diabetic range)\n"
                response += "- Family history: Father has Type 2 Diabetes (onset age 45)\n"
                response += "- You're age 44 (high-risk age)\n\n"
                response += "Recommendations:\n"
                response += "1. Continue current medication (Metformin)\n"
                response += "2. Schedule HbA1c retest in 3 months\n"
                response += "3. Maintain low-carb diet\n"
                response += "4. Regular exercise (30 min daily)\n"
                response += "5. Monitor fasting glucose weekly"
                return response
            
            elif 'medication' in message_lower or 'medicine' in message_lower:
                return "Your current medications:\n\n- Metformin 500mg (for blood sugar management)\n\nReminder: You have 3 days of medication remaining. Please refill soon.\n\nImportant: Take after meals to avoid stomach upset. Let me know if you experience any side effects."
            
            elif 'appointment' in message_lower:
                return "Based on your health profile, I recommend scheduling:\n\n1. HbA1c test (due in 1 month)\n2. Eye checkup (recommended for diabetes risk)\n\nWould you like me to help book an appointment?"
            
            else:
                return f"I understand your concern about: {message}\n\nBased on your medical history, your overall health status is stable. Your recent tests show normal ranges for most parameters.\n\nIf you have specific concerns, please describe your symptoms in detail, or consult your doctor for personalized advice."
    
    def _store_conversation(
        self,
        patient_id: str,
        message: str,
        response: str
    ) -> str:
        """
        Store conversation in history
        
        Args:
            patient_id: Patient identifier
            message: User message
            response: Bot response
            
        Returns:
            str: Message ID
        """
        if patient_id not in self.conversation_history:
            self.conversation_history[patient_id] = []
        
        message_id = f"msg_{len(self.conversation_history[patient_id])}"
        
        self.conversation_history[patient_id].append({
            'message_id': message_id,
            'user_message': message,
            'bot_response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        return message_id
    
    def get_conversation_history(self, patient_id: str) -> List[Dict]:
        """
        Get conversation history for a patient
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            List of conversation messages
        """
        return self.conversation_history.get(patient_id, [])
    
    def get_message_by_id(self, patient_id: str, message_id: str) -> Optional[Dict]:
        """
        Get specific message from conversation history
        
        Args:
            patient_id: Patient identifier
            message_id: Message ID to retrieve
            
        Returns:
            Message dict or None if not found
        """
        history = self.conversation_history.get(patient_id, [])
        for msg in history:
            if msg['message_id'] == message_id:
                return msg
        return None


# Convenience function
def process_chat(patient_id: str, message: str, language: str = 'english') -> Dict:
    """Quick chat processing function"""
    handler = ChatHandler()
    return handler.process_message(patient_id, message, language)


if __name__ == "__main__":
    # Test chat handler
    print("Testing Chat Handler...")
    
    handler = ChatHandler()
    
    # Test message
    response = handler.process_message(
        patient_id="PT-2026-DEMO",
        message="I have mild fever and cough",
        language="english"
    )
    
    print(f"Response: {response['response']}")
    print("\nChat handler test complete!")
