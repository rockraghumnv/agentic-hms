"""
Phase 5 Tests: Explainable AI Transparency Feature
Tests for AI explanation generation and transparency
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from explainer import AIExplainer, generate_explanation
from chat_handler import ChatHandler
from mock_db import store_patient_data


@pytest.fixture(scope="module")
def setup_test_data():
    """Setup test patient and chat history"""
    # Add test patient
    test_patient = {
        'patient_id': 'PT-2026-EXPL',
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
    
    store_patient_data('PT-2026-EXPL', test_patient)
    
    # Create chat handler and add medical record
    chat_handler = ChatHandler()
    chat_handler.vector_store.add_medical_record(
        patient_id='PT-2026-EXPL',
        document_text='Blood Test Results: Glucose: 128 mg/dL, HbA1c: 5.9%. Medications: Metformin 500mg daily.',
        metadata={'type': 'lab_report', 'date': '2026-01-15'}
    )
    
    # Generate a chat message
    response = chat_handler.process_message(
        patient_id='PT-2026-EXPL',
        message='What is my diabetes risk?',
        language='english'
    )
    
    return {
        'chat_handler': chat_handler,
        'message_id': response['message_id'],
        'user_query': 'What is my diabetes risk?',
        'bot_response': response['response']
    }


@pytest.fixture(scope="module")
def explainer():
    """Create AI explainer instance"""
    return AIExplainer()


def test_1_explainer_init(explainer):
    """Test explainer initialization"""
    assert explainer is not None
    assert hasattr(explainer, 'vector_store')
    print("✓ Explainer initialized")


def test_2_explain_response(explainer, setup_test_data):
    """Test basic explanation generation"""
    data = setup_test_data
    
    explanation = explainer.explain_response(
        patient_id='PT-2026-EXPL',
        message_id=data['message_id'],
        user_query=data['user_query'],
        bot_response=data['bot_response']
    )
    
    assert 'data_sources' in explanation
    assert 'patterns_detected' in explanation
    assert 'risk_factors' in explanation
    assert 'recommendation_logic' in explanation
    assert 'confidence_level' in explanation
    print("✓ Basic explanation generated")


def test_3_data_sources(explainer, setup_test_data):
    """Test data sources extraction"""
    data = setup_test_data
    
    explanation = explainer.explain_response(
        patient_id='PT-2026-EXPL',
        message_id=data['message_id'],
        user_query=data['user_query'],
        bot_response=data['bot_response']
    )
    
    sources = explanation['data_sources']
    assert 'family_history' in sources
    assert 'medical_records' in sources
    assert 'medications' in sources
    assert 'test_results' in sources
    
    # Check family history was extracted
    assert sources['family_history'] is not None
    assert len(sources['family_history']) > 0
    print(f"✓ Data sources extracted ({len(sources['family_history'])} family history items)")


def test_4_patterns_detection(explainer, setup_test_data):
    """Test pattern detection"""
    data = setup_test_data
    
    explanation = explainer.explain_response(
        patient_id='PT-2026-EXPL',
        message_id=data['message_id'],
        user_query='What about my glucose levels?',
        bot_response='Your glucose is trending upward...'
    )
    
    patterns = explanation['patterns_detected']
    assert isinstance(patterns, list)
    assert len(patterns) > 0
    
    # Check for diabetes-related patterns
    patterns_text = ' '.join(patterns).lower()
    assert any(keyword in patterns_text for keyword in ['glucose', 'diabetes', 'family'])
    print(f"✓ Patterns detected ({len(patterns)} patterns)")


def test_5_risk_factors(explainer, setup_test_data):
    """Test risk factor identification"""
    data = setup_test_data
    
    explanation = explainer.explain_response(
        patient_id='PT-2026-EXPL',
        message_id=data['message_id'],
        user_query=data['user_query'],
        bot_response=data['bot_response']
    )
    
    risk_factors = explanation['risk_factors']
    assert isinstance(risk_factors, list)
    assert len(risk_factors) > 0
    
    # Check risk factor structure
    first_risk = risk_factors[0]
    assert 'factor' in first_risk
    assert 'severity' in first_risk
    assert 'description' in first_risk
    assert 'mitigation' in first_risk
    
    # Check severity levels
    assert first_risk['severity'] in ['High', 'Medium', 'Low']
    print(f"✓ Risk factors identified ({len(risk_factors)} factors)")


def test_6_recommendation_logic(explainer, setup_test_data):
    """Test recommendation logic explanation"""
    data = setup_test_data
    
    explanation = explainer.explain_response(
        patient_id='PT-2026-EXPL',
        message_id=data['message_id'],
        user_query='I have fever',
        bot_response='Monitor your temperature for 24 hours...'
    )
    
    logic = explanation['recommendation_logic']
    assert 'decision_tree' in logic
    assert 'medical_guidelines' in logic
    assert 'personalization_factors' in logic
    
    assert isinstance(logic['decision_tree'], list)
    assert isinstance(logic['medical_guidelines'], list)
    assert isinstance(logic['personalization_factors'], list)
    print("✓ Recommendation logic explained")


def test_7_confidence_calculation(explainer, setup_test_data):
    """Test confidence level calculation"""
    data = setup_test_data
    
    explanation = explainer.explain_response(
        patient_id='PT-2026-EXPL',
        message_id=data['message_id'],
        user_query=data['user_query'],
        bot_response=data['bot_response']
    )
    
    confidence = explanation['confidence_level']
    assert 'level' in confidence
    assert 'percentage' in confidence
    assert 'reason' in confidence
    
    assert confidence['level'] in ['High', 'Medium', 'Low']
    assert 0 <= confidence['percentage'] <= 100
    print(f"✓ Confidence calculated ({confidence['level']} - {confidence['percentage']}%)")


def test_8_convenience_function():
    """Test convenience function"""
    explanation = generate_explanation(
        patient_id='PT-2026-DEMO',
        message_id='msg_test',
        user_query='Test query',
        bot_response='Test response'
    )
    
    assert 'data_sources' in explanation
    assert 'confidence_level' in explanation
    print("✓ Convenience function works")


def test_9_chat_handler_integration(setup_test_data):
    """Test chat handler integration for explanation"""
    data = setup_test_data
    chat_handler = data['chat_handler']
    
    # Get message by ID
    message = chat_handler.get_message_by_id('PT-2026-EXPL', data['message_id'])
    
    assert message is not None
    assert 'user_message' in message
    assert 'bot_response' in message
    assert message['message_id'] == data['message_id']
    print("✓ Chat handler integration works")


def test_10_html_modal_support():
    """Test chatbot HTML has explanation modal support"""
    chatbot_path = Path(__file__).parent.parent / "frontend" / "chatbot.html"
    content = chatbot_path.read_text(encoding='utf-8')
    
    assert 'explainResponse' in content
    assert 'showExplanationModal' in content
    assert 'formatDataSources' in content
    assert 'formatRiskFactors' in content
    assert '/api/explain' in content
    print("✓ HTML modal support present")


def test_11_api_endpoint():
    """Test API endpoint is defined"""
    main_path = Path(__file__).parent.parent / "backend" / "main.py"
    content = main_path.read_text(encoding='utf-8')
    
    assert '/api/explain' in content
    assert 'ExplainRequest' in content
    assert 'AIExplainer' in content
    assert 'explain_response' in content
    print("✓ API endpoint defined")


if __name__ == "__main__":
    print("Running Phase 5 Tests...")
    pytest.main([__file__, "-v", "-s"])
