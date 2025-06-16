# Healthcare Query Tool

A natural language processing tool that converts user queries into FHIR API requests for healthcare data retrieval.

## Features

- **Natural Language Processing**: Convert plain English queries into structured FHIR API requests
- **Medical Condition Recognition**: Supports diabetes, hypertension, asthma, COPD, cancer, COVID-19, pneumonia, heart disease, and stroke
- **Advanced Filtering**: Age-based filtering, gender-based filtering, and name-based searching
- **Modern UI**: Clean, responsive web interface built with Next.js
- **Real-time Processing**: Instant query conversion with loading indicators
- **Modular Architecture**: Clean separation of concerns with dedicated modules for entity extraction, query parsing, and FHIR building

## Architecture

```
Frontend (Next.js) → Backend API (FastAPI) → Modular NLP Service → FHIR Query Output
                                          ├── Medical Entity Extractor
                                          ├── Query Parser
                                          └── FHIR Query Builder
```

## Setup Instructions

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download SpaCy language model:**
   ```bash
   python -m spacy download en_core_web_md
   ```

5. **Start the FastAPI server:**
   ```bash
   cd app
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The web application will be available at `http://localhost:3000`

## Example Queries

The system can process natural language queries like:

- "List all female patients with diabetes over 50 years of age"
- "Show me patients with hypertension and are male and below 18 years of age"
- "List all people with asthma that are male"
- "Show all people with diabetes whose name starts with Sid"
- "Find patients that are male with hypertension"

### Expected Output Format

**Input Query:** `"List all female patients with diabetes over 50 years of age"`

**Generated FHIR Query:** `GET [base]/Patient?_has:Condition:subject:code=E11&birthdate=lt2024-01-01&gender=female`

## API Endpoints

### POST `/nlp`
Convert natural language query to FHIR query.

**Request Body:**
```json
{
  "query": "list all female patients with diabetes over 50 years of age"
}
```

**Response:**
```json
{
  "fhir_query": "GET [base]/Patient?_has:Condition:subject:code=E11&birthdate=lt2024-01-01&gender=female",
  "success": true
}
```

## Medical Condition Codes

The system recognizes these medical conditions with their corresponding ICD-10 codes:

| Condition | ICD-10 Code | SNOMED CT |
|-----------|-------------|-----------|
| Diabetes | E11 | 73211009 |
| Hypertension | I10 | 38341003 |
| Asthma | J45 | 195967001 |
| COPD | J44 | 13645005 |
| Cancer | C80 | 363346000 |
| COVID-19 | U07.1 | 840539006 |
| Pneumonia | J18 | 233604007 |
| Heart Disease | I51 | 56265001 |
| Stroke | I64 | 230690007 |

## Development

### Project Structure

```
healthcare-query-tool/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application (directly runnable)
│   │   └── nlp-service/
│   │       ├── medical_entities.py   # Medical condition mappings & entity extraction
│   │       ├── query_parser.py       # Natural language query parsing
│   │       ├── fhir_builder.py       # FHIR query construction
│   │       └── nlp_service.py        # Main orchestrator service
│   ├── requirements.txt               # Python dependencies
│   └── test_api.py                   # API testing script
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # Main page component
│   │   │   └── api/
│   │   │       └── query/
│   │   │           └── route.ts      # API route handler
│   │   └── components/
│   │       └── SearchBox.tsx         # Search input component
│   └── package.json
└── README.md
```

### Modular Architecture

The NLP service is now split into focused modules:

1. **`medical_entities.py`**: Handles medical condition mappings and SpaCy entity recognition setup
2. **`query_parser.py`**: Parses natural language queries and extracts criteria (conditions, age, gender, names)
3. **`fhir_builder.py`**: Constructs FHIR queries from parsed criteria
4. **`nlp_service.py`**: Main orchestrator that coordinates all modules and returns the final FHIR query string

### Adding New Medical Conditions

1. Update `condition_codes` dictionary in `backend/app/nlp-service/medical_entities.py`
2. The entity patterns are automatically generated from the condition codes
3. Restart the backend server

### Testing

Run the test script to verify everything is working:

```bash
cd backend
python test_api.py
```

### Troubleshooting

**Backend Issues:**
- Ensure SpaCy model is downloaded: `python -m spacy download en_core_web_md`
- Check if port 8000 is available
- Verify all dependencies are installed
- Run `python main.py` from the `backend/app/` directory

**Frontend Issues:**
- Ensure backend is running on port 8000
- Check browser console for errors
- Try clearing browser cache

**CORS Issues:**
- The backend is configured to allow requests from `localhost:3000`
- If using different ports, update the CORS configuration in `backend/app/main.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly using `python test_api.py`
5. Submit a pull request

## License

This project is for educational and research purposes. 