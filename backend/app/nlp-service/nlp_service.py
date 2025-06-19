"""
Main NLP service orchestrator for healthcare query processing
"""
import requests
import re
from typing import List, Optional, Dict

from medical_entities import MedicalEntityExtractor
from query_parser import QueryParser
from fhir_builder import FHIRQueryBuilder

class HealthcareNLPService:
    def __init__(self):
        """Initialize the NLP service with all components"""
        self.medical_extractor = MedicalEntityExtractor()
        self.query_parser = QueryParser(self.medical_extractor)
        self.fhir_builder = FHIRQueryBuilder()
    
    def process_query(self, natural_language_query: str) -> Dict[str, Optional[str]]:
        """
        Process a natural language query to generate a single, direct FHIR Patient query.
        """
        # Step 1: Parse the natural language query to extract criteria
        parsed_criteria = self.query_parser.parse_query(natural_language_query)
        
        # Step 2: Build the final Patient query using all extracted criteria
        patient_query = self.fhir_builder.build_patient_query(parsed_criteria)
        
        return {
            "fhir_query": patient_query
        }

# Global instance for the service
nlp_service = HealthcareNLPService() 