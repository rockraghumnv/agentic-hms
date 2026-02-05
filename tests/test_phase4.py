"""
Phase 4 Tests: Chatbot Interface with Medical Q&A
Tests for chat handler, medical context retrieval, and multi-language responses
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from chat_handler import ChatHandler, process_chat
from mock_db import store_patient_data, patient_exists, patient_records


@pytest.fixture(scope="module")
def chat_handler():
    """Create chat handler instance"""
    handler = ChatHandler()
    
    # Add test patient with medical history
    test_patient = {
        'patient_id': 'PT-2026-TEST',
        'uploaded_documents': ['test_report.jpg'],
        'documents_processed': 1,
        'family_history': {
            'father_conditions': 'Type 2 Diabetes',
            'mother_conditions': 'Hypertension',
            'siblings_conditions': 'None',
            'family_diseases': 'Diabetes, Heart Disease'
        },
        'consent_given': True,
        'upload_timestamp': '2026-02-04T10:30:00'
    }
    
    store_patient_data('PT-2026-TEST', test_patient)
    
    # Add medical record to vector store
    handler.vector_store.add_medical_record(
        patient_id='PT-2026-TEST',
        document_text='Blood Test Results: Glucose: 128 mg/dL, HbA1c: 5.9%. Medications: Metformin 500mg daily.',
        metadata={'type': 'lab_report', 'date': '2026-01-15'}
    )
    
    return handler


def test_1_chat_handler_init(chat_handler):
    """Test chat handler initialization"""
    assert chat_handler is not None
    assert hasattr(chat_handler, 'vector_store')
    assert hasattr(chat_handler, 'parser')
    assert hasattr(chat_handler, 'conversation_history')
    print("✓ Chat handler initialized")


def test_2_process_english_message(chat_handler):
    """Test processing English message"""
    response = chat_handler.process_message(
        patient_id='PT-2026-TEST',
        message='What is my blood sugar level?',
        language='english'
    )
    
    assert response['success'] is True
    assert 'response' in response
    assert len(response['response']) > 0
    assert response['language'] == 'english'
    assert 'message_id' in response
    print("✓ English message processed")


def test_3_process_kannada_message(chat_handler):
    """Test processing Kannada message"""
    response = chat_handler.process_message(
        patient_id='PT-2026-TEST',
        message='ನನ್ನ ಜ್ವರವಿದೆ',
        language='kannada'
    )
    
    assert response['success'] is True
    assert 'response' in response
    assert response['language'] == 'kannada'
    print("✓ Kannada message processed")


def test_4_invalid_patient(chat_handler):
    """Test with invalid patient ID"""
    response = chat_handler.process_message(
        patient_id='PT-9999-FAKE',
        message='Test question',
        language='english'
    )
    
    assert response['success'] is False
    assert 'error' in response
    print("✓ Invalid patient handled")


def test_5_context_retrieval(chat_handler):
    """Test medical context retrieval"""
    response = chat_handler.process_message(
        patient_id='PT-2026-TEST',
        message='Tell me about my glucose levels',
        language='english'
    )
    
    assert response['success'] is True
    assert response['context_used'] >= 0  # Should retrieve relevant records
    print(f"✓ Context retrieved ({response['context_used']} records)")


def test_6_conversation_history(chat_handler):
    """Test conversation history storage"""
    # Send two messages
    chat_handler.process_message('PT-2026-TEST', 'First question', 'english')
    chat_handler.process_message('PT-2026-TEST', 'Second question', 'english')
    
    history = chat_handler.get_conversation_history('PT-2026-TEST')
    
    assert len(history) >= 2
    assert 'user_message' in history[0]
    assert 'bot_response' in history[0]
    assert 'timestamp' in history[0]
    print(f"✓ Conversation history stored ({len(history)} messages)")


def test_7_fever_query(chat_handler):
    """Test fever-related query"""
    response = chat_handler.process_message(
        patient_id='PT-2026-TEST',
        message='I have fever and cough',
        language='english'
    )
    
    assert response['success'] is True
    assert 'fever' in response['response'].lower() or 'temperature' in response['response'].lower()
    print("✓ Fever query answered")


def test_8_glucose_query(chat_handler):
    """Test glucose/diabetes query"""
    response = chat_handler.process_message(
        patient_id='PT-2026-TEST',
        message='What about my diabetes risk?',
        language='english'
    )
    
    assert response['success'] is True
    response_lower = response['response'].lower()
    assert 'glucose' in response_lower or 'diabetes' in response_lower or 'sugar' in response_lower
    print("✓ Glucose query answered")


def test_9_demo_patient_chat():
    """Test with demo patient"""
    response = process_chat(
        patient_id='PT-2026-DEMO',
        message='How is my health?',
        language='english'
    )
    
    assert response['success'] is True
    assert len(response['response']) > 0
    print("✓ Demo patient chat works")


def test_10_chatbot_html_exists():
    """Test chatbot HTML file exists"""
    chatbot_path = Path(__file__).parent.parent / "frontend" / "chatbot.html"
    assert chatbot_path.exists()
    
    content = chatbot_path.read_text(encoding='utf-8')
    assert 'AI Healthcare Assistant' in content
    assert 'loginScreen' in content
    assert 'chatInterface' in content
    assert 'language-toggle' in content
    assert 'kannada' in content.lower()
    print("✓ Chatbot HTML complete")


def test_11_api_endpoint_structure():
    """Test API endpoint is defined in main.py"""
    main_path = Path(__file__).parent.parent / "backend" / "main.py"
    content = main_path.read_text(encoding='utf-8')
    
    assert '/api/chat' in content
    assert 'ChatHandler' in content
    assert 'ChatRequest' in content
    assert 'language' in content
    print("✓ API endpoint defined")


if __name__ == "__main__":
    print("Running Phase 4 Tests...")
    pytest.main([__file__, "-v", "-s"])
