from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os
from fastapi.responses import JSONResponse

# Add the nlp-service directory to the path to import the new modular service
sys.path.append(os.path.join(os.path.dirname(__file__), 'nlp-service'))

try:
    from nlp_service import nlp_service
    from fhir_client import execute_fhir_query
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure the nlp-service directory and modules are in the correct location")
    raise

app = FastAPI(title="Healthcare Query Tool API", version="1.0.0")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://healthcare-query-tool.vercel.app"],  # Frontend URL
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

@app.post("/api/query")
async def process_query_endpoint(request: QueryRequest):
    """
    API endpoint to process a natural language query, fetch FHIR data, and return it.
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")
            
        # Step 1: Generate the FHIR query string from the NLP service
        query_result = nlp_service.process_query(request.query)
        fhir_query = query_result.get("fhir_query")

        if not fhir_query:
            raise HTTPException(status_code=500, detail="Failed to generate FHIR query.")

        # Handle unsupported conditions: return the query status and an empty data list
        if fhir_query == "UNSUPPORTED_CONDITION":
            return {"success": True, "fhir_query": "Query not generated for unsupported condition.", "data": "UNSUPPORTED_CONDITION"}

        # Step 2: Execute the query to get the processed patient data
        patient_data = execute_fhir_query(fhir_query)

        return {"success": True, "fhir_query": fhir_query, "data": patient_data}

    except Exception as e:
        print(f"Error processing query: {e}")
        # Return a more generic error to the user
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "An internal error occurred while processing the query."}
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