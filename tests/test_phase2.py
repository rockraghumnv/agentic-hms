"""
Phase 2 Tests: Upload Portal with Gemini Vision OCR
"""
import pytest
import os
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from id_generator import generate_patient_id, validate_patient_id
from mock_db import store_patient_data, get_patient_data, patient_exists


def test_id_generator():
    """Test patient ID generation"""
    patient_id = generate_patient_id()
    
    # Check format PT-YYYY-XXXX
    assert patient_id.startswith("PT-"), "ID should start with PT-"
    parts = patient_id.split('-')
    assert len(parts) == 3, "ID should have 3 parts"
    assert parts[1] == "2026", "Year should be 2026"
    assert len(parts[2]) == 4, "Random part should be 4 characters"


def test_id_validation():
    """Test patient ID validation"""
    # Valid IDs
    assert validate_patient_id("PT-2026-A7B3") == True
    assert validate_patient_id("PT-2025-XY12") == True
    
    # Invalid IDs
    assert validate_patient_id("") == False
    assert validate_patient_id("PT-26-A7B3") == False
    assert validate_patient_id("XX-2026-A7B3") == False
    assert validate_patient_id("PT-2026-A7") == False
    assert validate_patient_id("PT-2026") == False


def test_mock_db_store():
    """Test storing patient data in mock database"""
    patient_id = "PT-2026-TEST1"
    test_data = {
        "name": "Test Patient",
        "age": 30,
        "family_history": {"father": "None"}
    }
    
    result = store_patient_data(patient_id, test_data)
    assert result == True, "Store should return True"
    
    # Verify storage
    stored_data = get_patient_data(patient_id)
    assert stored_data is not None, "Data should be retrievable"
    assert stored_data["name"] == "Test Patient"
    assert stored_data["age"] == 30


def test_mock_db_retrieve():
    """Test retrieving patient data"""
    patient_id = "PT-2026-TEST2"
    test_data = {"name": "Another Patient", "age": 45}
    
    store_patient_data(patient_id, test_data)
    retrieved = get_patient_data(patient_id)
    
    assert retrieved is not None
    assert retrieved["name"] == "Another Patient"
    assert "created_at" in retrieved, "Should have timestamp"


def test_mock_db_exists():
    """Test patient existence check"""
    patient_id = "PT-2026-TEST3"
    
    # Should not exist initially
    assert patient_exists(patient_id) == False
    
    # Store data
    store_patient_data(patient_id, {"name": "Test"})
    
    # Should exist now
    assert patient_exists(patient_id) == True


def test_mock_db_nonexistent():
    """Test retrieving non-existent patient"""
    result = get_patient_data("PT-2026-NONEXISTENT")
    assert result is None, "Should return None for non-existent patient"


def test_upload_directory_structure():
    """Test that upload directory structure is valid"""
    backend_dir = Path(__file__).parent.parent / "backend"
    
    # Check key files exist
    assert (backend_dir / "main.py").exists(), "main.py should exist"
    assert (backend_dir / "gemini_vision.py").exists(), "gemini_vision.py should exist"
    assert (backend_dir / "id_generator.py").exists(), "id_generator.py should exist"
    assert (backend_dir / "mock_db.py").exists(), "mock_db.py should exist"


def test_frontend_upload_page():
    """Test that upload.html exists"""
    frontend_dir = Path(__file__).parent.parent / "frontend"
    upload_page = frontend_dir / "upload.html"
    
    assert upload_page.exists(), "upload.html should exist"
    
    # Check content has required elements
    content = upload_page.read_text(encoding='utf-8')
    assert "family" in content.lower(), "Should mention family history"
    assert "consent" in content.lower(), "Should have consent section"
    assert "upload" in content.lower(), "Should have upload functionality"


def test_env_example_has_gemini_key():
    """Test that .env.example includes Gemini API key"""
    env_example = Path(__file__).parent.parent / ".env.example"
    content = env_example.read_text()
    
    assert "GEMINI_API_KEY" in content, "Should have GEMINI_API_KEY"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
