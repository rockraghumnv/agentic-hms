"""
Mock Database for Demo
Stores patient data temporarily in memory
In production, this would be replaced with a real database
"""
from typing import Dict, List, Optional
from datetime import datetime


# In-memory storage
patient_records: Dict[str, dict] = {}


def store_patient_data(patient_id: str, data: dict) -> bool:
    """
    Store patient data in mock database
    
    Args:
        patient_id: Unique patient identifier
        data: Patient data dictionary
        
    Returns:
        bool: True if successful
    """
    patient_records[patient_id] = {
        **data,
        'created_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat()
    }
    return True


def get_patient_data(patient_id: str) -> Optional[dict]:
    """
    Retrieve patient data from mock database
    
    Args:
        patient_id: Unique patient identifier
        
    Returns:
        dict: Patient data or None if not found
    """
    return patient_records.get(patient_id)


def update_patient_data(patient_id: str, updates: dict) -> bool:
    """
    Update existing patient data
    
    Args:
        patient_id: Unique patient identifier
        updates: Dictionary of fields to update
        
    Returns:
        bool: True if successful, False if patient not found
    """
    if patient_id not in patient_records:
        return False
    
    patient_records[patient_id].update(updates)
    patient_records[patient_id]['last_updated'] = datetime.now().isoformat()
    return True


def patient_exists(patient_id: str) -> bool:
    """
    Check if patient exists in database
    
    Args:
        patient_id: Unique patient identifier
        
    Returns:
        bool: True if patient exists
    """
    return patient_id in patient_records


def get_all_patients() -> List[str]:
    """
    Get list of all patient IDs
    
    Returns:
        List of patient IDs
    """
    return list(patient_records.keys())


def delete_patient(patient_id: str) -> bool:
    """
    Delete patient from database
    
    Args:
        patient_id: Unique patient identifier
        
    Returns:
        bool: True if deleted, False if not found
    """
    if patient_id in patient_records:
        del patient_records[patient_id]
        return True
    return False


# Mock patient history data for demo
DEMO_PATIENT_DATA = {
    "PT-2026-DEMO": {
        "name": "Demo Patient",
        "age": 44,
        "medical_history": [
            {
                "date": "2025-09-15",
                "type": "Blood Test",
                "findings": "Fasting glucose: 95 mg/dL, HbA1c: 5.4%"
            },
            {
                "date": "2025-12-10",
                "type": "Blood Test",
                "findings": "Fasting glucose: 110 mg/dL, HbA1c: 5.7%"
            }
        ],
        "family_history": {
            "father": "Type 2 Diabetes (onset age 45)",
            "mother": "Hypertension",
            "siblings": "None"
        },
        "current_medications": ["Metformin 500mg"],
        "allergies": ["Penicillin"],
        "created_at": "2026-01-15T10:30:00",
        "last_updated": "2026-02-04T09:00:00"
    }
}

# Initialize with demo data
patient_records.update(DEMO_PATIENT_DATA)


if __name__ == "__main__":
    # Test mock database
    print("Testing Mock Database...")
    
    # Test store
    test_id = "PT-2026-TEST"
    store_patient_data(test_id, {"name": "Test Patient", "age": 30})
    print(f"Stored: {test_id}")
    
    # Test retrieve
    data = get_patient_data(test_id)
    print(f"Retrieved: {data}")
    
    # Test exists
    print(f"Exists: {patient_exists(test_id)}")
    
    # Test all patients
    print(f"All patients: {get_all_patients()}")
