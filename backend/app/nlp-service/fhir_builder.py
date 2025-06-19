"""
FHIR query construction from parsed criteria
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional

class FHIRQueryBuilder:
    def __init__(self):
        self.base_url = "http://hapi.fhir.org/baseR4"
    
    def build_patient_query(self, parsed_criteria: Dict) -> str:
        """Builds a single, combined FHIR query for the Patient resource using _has for conditions."""
        query_params = []

        # Handle conditions using the _has parameter
        conditions = parsed_criteria.get("conditions")
        if conditions:
            # For simplicity, we'll use the first condition found.
            # Production systems might handle multiple conditions.
            snomed_code = conditions[0]["codes"]["snomed"]
            condition_param = f"_has:Condition:subject:code=http://snomed.info/sct|{snomed_code}"
            query_params.append(condition_param)

        # Handle age criteria
        age_criteria = parsed_criteria.get("age_criteria")
        if age_criteria:
            birthdate_param = self._calculate_birthdate_from_age(
                age_criteria["value"],
                age_criteria["operator"]
            )
            # Add birthdate params only if they are not empty
            if birthdate_param:
                 query_params.append(f"birthdate={birthdate_param}")

        # Handle gender
        gender = parsed_criteria.get("gender")
        if gender:
            query_params.append(f"gender={gender}")
        
        # Handle name criteria
        name_criteria = parsed_criteria.get("name_criteria")
        if name_criteria:
            if name_criteria["type"] == "starts_with":
                query_params.append(f"name:starts-with={name_criteria['value']}")
            elif name_criteria["type"] == "exact":
                query_params.append(f"name={name_criteria['value']}")
        
        # Construct final URL
        if query_params:
            return f"GET {self.base_url}/Patient?{'&'.join(query_params)}"
        else:
            # If no criteria, query for all patients (or handle as an error, depending on requirements)
            return f"GET {self.base_url}/Patient"
    
    def _calculate_birthdate_from_age(self, age: int, operator: str) -> str:
        """Calculate birthdate parameter based on age criteria"""
        today = datetime.now()
        
        if operator == "gt":  # over X years (person is older than X)
            target_date = today - relativedelta(years=age + 1)
            return f"le{target_date.strftime('%Y-%m-%d')}" # le (less than or equal to) is more inclusive for "over"
        elif operator == "lt":  # under X years (person is younger than X)
            target_date = today - relativedelta(years=age)
            return f"gt{target_date.strftime('%Y-%m-%d')}" # gt (greater than)
        elif operator == "eq":  # exactly X years
            start_date = today - relativedelta(years=age + 1)
            end_date = today - relativedelta(years=age)
            return f"ge{start_date.strftime('%Y-%m-%d')}&birthdate=le{end_date.strftime('%Y-%m-%d')}"
        
        return "" 