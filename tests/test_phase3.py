"""
Phase 3 Tests: ChromaDB Storage and Gemini Parser - OPTIMIZED
"""
import pytest
import os
import sys
from pathlib import Path
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from vector_store import MedicalVectorStore
from gemini_parser import GeminiParser


@pytest.fixture(scope="module")
def vector_store():
    """Single vector store for all tests"""
    test_dir = "./test_chroma_db"
    if Path(test_dir).exists():
        shutil.rmtree(test_dir, ignore_errors=True)
    
    store = MedicalVectorStore(persist_directory=test_dir)
    yield store
    
    try:
        store.client.reset()
        del store
    except:
        pass
    shutil.rmtree(test_dir, ignore_errors=True)


@pytest.fixture(scope="module")
def parser():
    """Single parser for all tests"""
    return GeminiParser()


def test_1_init(vector_store):
    """Test vector store init"""
    assert vector_store is not None
    print("✓ Vector store OK")


def test_2_add_record(vector_store):
    """Test add record"""
    doc_id = vector_store.add_medical_record(
        "PT-2026-T1",
        "Glucose 110 mg/dL",
        {'type': 'lab'}
    )
    assert "PT-2026-T1" in doc_id
    print("✓ Add record OK")


def test_3_get_records(vector_store):
    """Test get records"""
    vector_store.add_medical_record("PT-2026-T2", "Record 1", {})
    vector_store.add_medical_record("PT-2026-T2", "Record 2", {})
    records = vector_store.get_patient_records("PT-2026-T2")
    assert len(records) >= 2
    print("✓ Get records OK")


def test_4_query(vector_store):
    """Test query"""
    vector_store.add_medical_record("PT-2026-T3", "Blood sugar glucose 120", {})
    results = vector_store.query_patient_history("PT-2026-T3", "glucose", 2)
    assert len(results) > 0
    print("✓ Query OK")


def test_5_family(vector_store):
    """Test family history"""
    doc_id = vector_store.add_family_history("PT-2026-T4", {"father": "Diabetes"})
    assert doc_id is not None
    print("✓ Family history OK")


def test_6_parser_init(parser):
    """Test parser init"""
    assert parser.mock_mode == True
    print("✓ Parser OK")


def test_7_parse(parser):
    """Test parse document"""
    parsed = parser.parse_medical_document("Glucose 110 mg/dL")
    assert 'document_type' in parsed
    print("✓ Parse OK")


def test_8_entities(parser):
    """Test extract entities"""
    entities = parser.extract_medical_entities("diabetes metformin fever")
    assert 'diabetes' in [e.lower() for e in entities['conditions']]
    print("✓ Entities OK")


def test_9_summary(parser):
    """Test summary"""
    summary = parser.generate_summary("Glucose 115")
    assert len(summary) > 0
    print("✓ Summary OK")


def test_10_integration(vector_store, parser):
    """Test integration"""
    text = "Glucose 115 mg/dL Metformin 500mg"
    parsed = parser.parse_medical_document(text)
    doc_id = vector_store.add_medical_record("PT-2026-T5", text, {'type': parsed['document_type']})
    records = vector_store.get_patient_records("PT-2026-T5")
    assert len(records) >= 1
    print("✓ Integration OK")


def test_11_stats(vector_store):
    """Test stats"""
    stats = vector_store.get_collection_stats()
    assert stats['total_documents'] > 0
    print(f"✓ Stats OK ({stats['total_documents']} docs)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
