from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add the nlp-service directory to the path to import the new modular service
sys.path.append(os.path.join(os.path.dirname(__file__), 'nlp-service'))

try:
    from nlp_service import nlp_service
except ImportError as e:
    print(f"Error importing NLP service: {e}")
    print("Please ensure the nlp-service directory and modules are in the correct location")
    raise

app = FastAPI(title="Healthcare Query Tool API", version="1.0.0")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    condition_query: Optional[str] = None
    patient_query: str
    success: bool
    error: Optional[str] = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Healthcare Query Tool API is running",
        "status": "healthy",
        "nlp_service": "available"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "nlp_service_status": "available",
        "version": "1.0.0"
    }

@app.post("/nlp", response_model=QueryResponse)
async def process_nlp_query(request: QueryRequest):
    """
    Process natural language query and convert to FHIR query
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(
                status_code=400, 
                detail="Query cannot be empty"
            )
        
        # Process the query using NLP service
        # Returns a dictionary with condition and patient queries
        query_result = nlp_service.process_query(request.query.strip())
        
        patient_query = query_result.get("patient_query")
        if not patient_query:
            return QueryResponse(
                patient_query="No FHIR patient query generated",
                success=False,
                error="Unable to generate FHIR patient query from the input"
            )
        
        return QueryResponse(
            condition_query=query_result.get("condition_query"),
            patient_query=patient_query,
            success=True
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Healthcare Query Tool API server...")
    print("📋 Make sure you have installed dependencies:")
    print("   pip install -r requirements.txt")
    print("   python -m spacy download en_core_web_md")
    print("")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 