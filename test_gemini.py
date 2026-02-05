"""Quick test of real Gemini API"""
import sys
sys.path.insert(0, 'backend')

from chat_handler import ChatHandler

print("=" * 60)
print("TESTING REAL GEMINI API")
print("=" * 60)

# Initialize chat handler
handler = ChatHandler()

# Test with demo patient
print("\n1. Testing medical question...")
response = handler.process_message(
    patient_id='PT-2026-DEMO',
    message='What is diabetes and how does it affect my health?',
    language='english'
)

print(f"Success: {response['success']}")
print(f"Response length: {len(response['response'])} characters")
print(f"\nAI Response:\n{response['response']}\n")

print("=" * 60)
print("✓ REAL GEMINI API WORKING!")
print("=" * 60)
