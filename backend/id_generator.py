"""
Patient ID Generator
Generates unique patient IDs in format: PT-YYYY-XXXX
"""
import random
import string
from datetime import datetime


def generate_patient_id() -> str:
    """
    Generate a unique patient ID
    Format: PT-YYYY-XXXX where XXXX is random alphanumeric
    
    Returns:
        str: Unique patient ID (e.g., PT-2026-A7B3)
    """
    year = datetime.now().year
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    patient_id = f"PT-{year}-{random_part}"
    return patient_id


def validate_patient_id(patient_id: str) -> bool:
    """
    Validate patient ID format
    
    Args:
        patient_id: Patient ID string to validate
        
    Returns:
        bool: True if valid format, False otherwise
    """
    if not patient_id:
        return False
    
    parts = patient_id.split('-')
    if len(parts) != 3:
        return False
    
    if parts[0] != 'PT':
        return False
    
    if not parts[1].isdigit() or len(parts[1]) != 4:
        return False
    
    if len(parts[2]) != 4:
        return False
    
    return True


if __name__ == "__main__":
    # Test ID generation
    for _ in range(5):
        patient_id = generate_patient_id()
        print(f"Generated ID: {patient_id} - Valid: {validate_patient_id(patient_id)}")
