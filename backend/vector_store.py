"""
ChromaDB Vector Store
Handles storage and retrieval of medical records with embeddings
"""
import os
from typing import List, Dict, Optional, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
import json

load_dotenv()

# Configuration
CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')


class MedicalVectorStore:
    """Vector store for medical records using ChromaDB"""
    
    def __init__(self, persist_directory: str = CHROMA_PERSIST_DIR):
        """
        Initialize ChromaDB vector store
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        Path(persist_directory).mkdir(exist_ok=True)
        
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection for medical records
        self.collection = self.client.get_or_create_collection(
            name="medical_records",
            metadata={"description": "Patient medical records and history"}
        )
        
        print(f"ChromaDB initialized: {self.collection.count()} documents")
    
    def add_medical_record(
        self,
        patient_id: str,
        document_text: str,
        metadata: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> str:
        """
        Add a medical record to vector store
        
        Args:
            patient_id: Unique patient identifier
            document_text: Extracted text from medical document
            metadata: Additional metadata (date, type, etc.)
            document_id: Optional custom document ID
            
        Returns:
            str: Document ID
        """
        if not document_id:
            import uuid
            document_id = f"{patient_id}_{uuid.uuid4().hex[:8]}"
        
        # Add patient_id to metadata for filtering
        metadata['patient_id'] = patient_id
        
        # Add document to collection
        self.collection.add(
            documents=[document_text],
            metadatas=[metadata],
            ids=[document_id]
        )
        
        return document_id
    
    def get_patient_records(
        self,
        patient_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all medical records for a patient
        
        Args:
            patient_id: Unique patient identifier
            limit: Maximum number of records to return
            
        Returns:
            List of medical records with metadata
        """
        try:
            results = self.collection.get(
                where={"patient_id": patient_id},
                limit=limit
            )
            
            if not results or not results['ids']:
                return []
            
            # Format results
            records = []
            for i in range(len(results['ids'])):
                records.append({
                    'id': results['ids'][i],
                    'text': results['documents'][i] if results.get('documents') else None,
                    'metadata': results['metadatas'][i] if results.get('metadatas') else {}
                })
            
            return records
            
        except Exception as e:
            print(f"Error retrieving records: {e}")
            return []
    
    def query_patient_history(
        self,
        patient_id: str,
        query_text: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query patient's medical history using semantic search
        
        Args:
            patient_id: Unique patient identifier
            query_text: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant medical records
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={"patient_id": patient_id}
            )
            
            if not results or not results['ids']:
                return []
            
            # Format results
            records = []
            for i in range(len(results['ids'][0])):
                records.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i] if results.get('documents') else None,
                    'metadata': results['metadatas'][0][i] if results.get('metadatas') else {},
                    'distance': results['distances'][0][i] if results.get('distances') else None
                })
            
            return records
            
        except Exception as e:
            print(f"Error querying history: {e}")
            return []
    
    def add_family_history(
        self,
        patient_id: str,
        family_data: Dict[str, str]
    ) -> str:
        """
        Add family medical history to vector store
        
        Args:
            patient_id: Unique patient identifier
            family_data: Dictionary with family history
            
        Returns:
            str: Document ID
        """
        # Convert family history to text for embedding
        family_text = f"""
        Family Medical History for {patient_id}:
        Father: {family_data.get('father', 'None')}
        Mother: {family_data.get('mother', 'None')}
        Siblings: {family_data.get('siblings', 'None')}
        Family Diseases: {family_data.get('family_diseases', 'None')}
        Additional: {family_data.get('additional', 'None')}
        """
        
        metadata = {
            'patient_id': patient_id,
            'type': 'family_history',
            'date': 'N/A',
            **family_data
        }
        
        return self.add_medical_record(
            patient_id=patient_id,
            document_text=family_text,
            metadata=metadata,
            document_id=f"{patient_id}_family_history"
        )
    
    def get_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        """
        Get comprehensive summary of patient's data
        
        Args:
            patient_id: Unique patient identifier
            
        Returns:
            dict: Patient summary with all records
        """
        records = self.get_patient_records(patient_id, limit=100)
        
        # Categorize records
        family_history = []
        lab_reports = []
        prescriptions = []
        other_docs = []
        
        for record in records:
            doc_type = record['metadata'].get('type', 'other')
            if doc_type == 'family_history':
                family_history.append(record)
            elif 'lab' in doc_type.lower():
                lab_reports.append(record)
            elif 'prescription' in doc_type.lower():
                prescriptions.append(record)
            else:
                other_docs.append(record)
        
        return {
            'patient_id': patient_id,
            'total_records': len(records),
            'family_history': family_history,
            'lab_reports': lab_reports,
            'prescriptions': prescriptions,
            'other_documents': other_docs
        }
    
    def delete_patient_records(self, patient_id: str) -> int:
        """
        Delete all records for a patient
        
        Args:
            patient_id: Unique patient identifier
            
        Returns:
            int: Number of records deleted
        """
        records = self.get_patient_records(patient_id, limit=1000)
        
        if not records:
            return 0
        
        ids_to_delete = [r['id'] for r in records]
        self.collection.delete(ids=ids_to_delete)
        
        return len(ids_to_delete)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store
        
        Returns:
            dict: Collection statistics
        """
        return {
            'total_documents': self.collection.count(),
            'collection_name': self.collection.name,
            'persist_directory': self.persist_directory
        }


# Convenience functions
def get_vector_store() -> MedicalVectorStore:
    """Get singleton instance of vector store"""
    return MedicalVectorStore()


if __name__ == "__main__":
    # Test vector store
    print("Testing ChromaDB Vector Store...")
    
    store = MedicalVectorStore()
    print(f"Stats: {store.get_collection_stats()}")
    
    # Test adding a record
    test_patient_id = "PT-2026-TEST"
    doc_id = store.add_medical_record(
        patient_id=test_patient_id,
        document_text="Blood test results: Glucose 110 mg/dL, HbA1c 5.7%",
        metadata={'type': 'lab_report', 'date': '2026-02-04'}
    )
    print(f"Added document: {doc_id}")
    
    # Test retrieval
    records = store.get_patient_records(test_patient_id)
    print(f"Retrieved {len(records)} records")
    
    # Test query
    results = store.query_patient_history(test_patient_id, "blood sugar")
    print(f"Query results: {len(results)} matches")
    
    print("ChromaDB test complete!")
