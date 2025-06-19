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
        Process a natural language query through a two-step process:
        1. Query for Conditions to get patient IDs.
        2. Query for Patients using those IDs and other criteria.
        """
        # Step 1: Parse the natural language query
        parsed_criteria = self.query_parser.parse_query(natural_language_query)
        
        condition_query = None
        patient_ids = None

        # Step 2: If a condition is present, build and execute the Condition query
        if parsed_criteria.get("conditions"):
            condition_query = self.fhir_builder.build_condition_lookup_query(parsed_criteria)
            if condition_query:
                patient_ids = self._fetch_patient_ids_from_condition(condition_query)

                # **CRITICAL CHECK**: If conditions were queried but no patients were found, stop here.
                if patient_ids is not None and not patient_ids:
                    return {
                        "condition_query": condition_query,
                        "patient_query": "No patient identified" # Special flag for the frontend
                    }

        # Step 3: Build the final Patient query
        patient_query = self.fhir_builder.build_patient_query(parsed_criteria, patient_ids)
        
        return {
            "condition_query": condition_query,
            "patient_query": patient_query
        }

    def _fetch_patient_ids_from_condition(self, condition_query: str) -> Optional[List[str]]:
        """Executes the Condition query and extracts patient IDs from the response."""
        url_match = re.search(r'GET\s+(.+)', condition_query)
        if not url_match:
            return None
        
        url = url_match.group(1)
        
        try:
            response = requests.get(url, headers={'Accept': 'application/fhir+json'})
            response.raise_for_status()  # Raise an exception for bad status codes
            
            bundle = response.json()
            patient_ids = []
            
            if bundle.get("resourceType") == "Bundle" and bundle.get("entry"):
                for entry in bundle["entry"]:
                    resource = entry.get("resource")
                    if resource and resource.get("resourceType") == "Condition":
                        subject = resource.get("subject")
                        if subject and subject.get("reference"):
                            # Extract ID from "Patient/12345"
                            match = re.search(r'Patient/(\w+)', subject["reference"])
                            if match:
                                patient_ids.append(match.group(1))
            
            # Return unique patient IDs
            return list(set(patient_ids))
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching patient IDs from {url}: {e}")
            return None # Return None on error to build a patient query without IDs

# Global instance for the service
nlp_service = HealthcareNLPService() 