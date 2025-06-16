"""
Main NLP service orchestrator for healthcare query processing
"""

from medical_entities import MedicalEntityExtractor
from query_parser import QueryParser
from fhir_builder import FHIRQueryBuilder

class HealthcareNLPService:
    def __init__(self):
        """Initialize the NLP service with all components"""
        self.medical_extractor = MedicalEntityExtractor()
        self.query_parser = QueryParser(self.medical_extractor)
        self.fhir_builder = FHIRQueryBuilder()
    
    def process_query(self, natural_language_query: str) -> str:
        """
        Process a natural language query and return FHIR query string
        
        Args:
            natural_language_query: The input query in natural language
            
        Returns:
            str: The generated FHIR query string
        """
        # Parse the query to extract criteria
        parsed_criteria = self.query_parser.parse_query(natural_language_query)
        
        # Build and return FHIR query
        fhir_query = self.fhir_builder.build_query(parsed_criteria)
        
        return fhir_query

# Global instance for the service
nlp_service = HealthcareNLPService() 