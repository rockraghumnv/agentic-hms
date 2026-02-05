"""
FastAPI Backend for AI Healthcare Assistant
Main API server handling upload, chat, and autonomous features
"""
import os
import shutil
from typing import List
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Import local modules
from id_generator import generate_patient_id
from mock_db import store_patient_data, get_patient_data, patient_exists
from gemini_vision import GeminiVisionOCR
from vector_store import MedicalVectorStore
from gemini_parser import GeminiParser
from chat_handler import ChatHandler
from explainer import AIExplainer

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Healthcare Assistant API",
    description="Backend API for personalized healthcare chatbot",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize services
ocr_processor = GeminiVisionOCR()
vector_store = MedicalVectorStore()
gemini_parser = GeminiParser()
chat_handler = ChatHandler()
ai_explainer = AIExplainer()


# Pydantic models
class ChatRequest(BaseModel):
    patient_id: str
    message: str
    language: str = 'english'


class ExplainRequest(BaseModel):
    patient_id: str
    message_id: str


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - serve upload page"""
    frontend_path = Path(__file__).parent.parent / "frontend" / "upload.html"
    if frontend_path.exists():
        return frontend_path.read_text()
    return "<h1>AI Healthcare Assistant API</h1><p>Upload page not found. Please access /docs for API documentation.</p>"


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Healthcare Assistant API",
        "version": "1.0.0"
    }


@app.get("/chatbot")
async def serve_chatbot():
    """Serve chatbot HTML page"""
    chatbot_path = Path(__file__).parent.parent / "frontend" / "chatbot.html"
    
    if not chatbot_path.exists():
        raise HTTPException(status_code=404, detail="Chatbot page not found")
    
    return FileResponse(chatbot_path)


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint for medical Q&A
    
    Args:
        request: Chat request with patient_id, message, and language
        
    Returns:
        dict: Response with answer and metadata
    """
    try:
        # Process chat message
        response = chat_handler.process_message(
            patient_id=request.patient_id,
            message=request.message,
            language=request.language
        )
        
        if not response['success']:
            raise HTTPException(status_code=404, detail=response['error'])
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/explain")
async def explain(request: ExplainRequest):
    """
    Explain AI response with transparency details
    
    Args:
        request: Explain request with patient_id and message_id
        
    Returns:
        dict: Detailed explanation of AI reasoning
    """
    try:
        # Get message from conversation history
        message = chat_handler.get_message_by_id(
            patient_id=request.patient_id,
            message_id=request.message_id
        )
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Generate explanation
        explanation = ai_explainer.explain_response(
            patient_id=request.patient_id,
            message_id=request.message_id,
            user_query=message['user_message'],
            bot_response=message['bot_response']
        )
        
        return {
            'success': True,
            'explanation': explanation
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_medical_records(
    files: List[UploadFile] = File(...),
    fatherHistory: str = Form(...),
    motherHistory: str = Form(...),
    siblingHistory: str = Form(...),
    familyDiseases: str = Form(...),
    additionalHistory: str = Form("")
):
    """
    Upload medical documents and family history
    Generates unique patient ID and processes images with Gemini Vision
    
    Args:
        files: List of medical document images
        fatherHistory: Father's medical history
        motherHistory: Mother's medical history
        siblingHistory: Siblings' medical history
        familyDiseases: Family disease history
        additionalHistory: Additional notes (optional)
        
    Returns:
        JSON with patient_id and processing status
    """
    try:
        # Validate files
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")
        
        # Validate all files are images
        for file in files:
            if not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} is not an image"
                )
        
        # Generate unique patient ID
        patient_id = generate_patient_id()
        
        # Create patient directory
        patient_dir = UPLOAD_DIR / patient_id
        patient_dir.mkdir(exist_ok=True)
        
        # Process each uploaded file
        processed_documents = []
        for idx, file in enumerate(files):
            # Save file
            file_path = patient_dir / f"doc_{idx}_{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract text using Gemini Vision OCR
            try:
                extracted_data = ocr_processor.extract_structured_data(str(file_path))
                
                # Parse extracted text with Gemini Parser
                if extracted_data.get("extraction_successful"):
                    raw_text = extracted_data.get("raw_text", "")
                    parsed_data = gemini_parser.parse_medical_document(raw_text)
                    
                    # Store in ChromaDB
                    doc_id = vector_store.add_medical_record(
                        patient_id=patient_id,
                        document_text=raw_text,
                        metadata={
                            'filename': file.filename,
                            'type': parsed_data.get('document_type', 'Unknown'),
                            'date': parsed_data.get('date', 'Unknown'),
                            'upload_date': datetime.now().isoformat()
                        }
                    )
                    
                    processed_documents.append({
                        "filename": file.filename,
                        "file_path": str(file_path),
                        "extracted_data": extracted_data,
                        "parsed_data": parsed_data,
                        "chroma_doc_id": doc_id,
                        "processed": True
                    })
                else:
                    processed_documents.append({
                        "filename": file.filename,
                        "file_path": str(file_path),
                        "extracted_data": extracted_data,
                        "processed": False
                    })
                    
            except Exception as e:
                processed_documents.append({
                    "filename": file.filename,
                    "file_path": str(file_path),
                    "error": str(e),
                    "processed": False
                })
        
        # Store family history in ChromaDB
        family_history_data = {
            "father": fatherHistory,
            "mother": motherHistory,
            "siblings": siblingHistory,
            "family_diseases": familyDiseases,
            "additional": additionalHistory
        }
        
        family_doc_id = vector_store.add_family_history(
            patient_id=patient_id,
            family_data=family_history_data
        )
        
        # Compile patient data
        patient_data = {
            "patient_id": patient_id,
            "family_history": {
                "father": fatherHistory,
                "mother": motherHistory,
                "siblings": siblingHistory,
                "family_diseases": familyDiseases,
                "additional": additionalHistory
            },
            "uploaded_documents": processed_documents,
            "total_documents": len(files),
            "documents_processed": sum(1 for doc in processed_documents if doc.get("processed", False))
        }
        
        # Store in mock database
        store_patient_data(patient_id, patient_data)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "patient_id": patient_id,
                "message": "Medical records uploaded and processed successfully",
                "documents_processed": patient_data["documents_processed"],
                "total_documents": patient_data["total_documents"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/patient/{patient_id}/history")
async def get_patient_history(patient_id: str):
    """
    Get patient's complete medical history from ChromaDB
    
    Args:
        patient_id: Unique patient identifier
        
    Returns:
        Patient medical history with all records
    """
    if not patient_exists(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get summary from ChromaDB
    summary = vector_store.get_patient_summary(patient_id)
    
    return {
        "patient_id": patient_id,
        "summary": summary,
        "total_records": summary['total_records']
    }


@app.post("/api/query")
async def query_patient_records(
    patient_id: str = Form(...),
    query: str = Form(...)
):
    """
    Query patient's medical records using semantic search
    
    Args:
        patient_id: Unique patient identifier
        query: Search query
        
    Returns:
        Relevant medical records
    """
    if not patient_exists(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Semantic search in ChromaDB
    results = vector_store.query_patient_history(
        patient_id=patient_id,
        query_text=query,
        n_results=5
    )
    
    return {
        "patient_id": patient_id,
        "query": query,
        "results": results,
        "count": len(results)
    }


@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics"""
    chroma_stats = vector_store.get_collection_stats()
    
    return {
        "vector_store": chroma_stats,
        "mock_mode": ocr_processor.mock_mode,
        "patients_count": len(get_all_patients())
    }


# Import get_all_patients from mock_db
from mock_db import get_all_patients


@app.get("/api/patient/{patient_id}")
async def get_patient_info(patient_id: str):
    """
    Retrieve patient information
    
    Args:
        patient_id: Unique patient identifier
        
    Returns:
        Patient data or 404 if not found
    """
    if not patient_exists(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient_data = get_patient_data(patient_id)
    
    # Remove sensitive file paths from response
    safe_data = patient_data.copy()
    if "uploaded_documents" in safe_data:
        for doc in safe_data["uploaded_documents"]:
            doc.pop("file_path", None)
    
    return safe_data


@app.get("/api/patient/{patient_id}/verify")
async def verify_patient(patient_id: str):
    """
    Verify if patient ID exists
    
    Args:
        patient_id: Unique patient identifier
        
    Returns:
        Verification status
    """
    exists = patient_exists(patient_id)
    return {
        "patient_id": patient_id,
        "exists": exists,
        "message": "Patient found" if exists else "Patient not found"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("🏥 AI Healthcare Assistant API")
    print("=" * 50)
    print("Starting server...")
    print("Upload page: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="info"
    )
