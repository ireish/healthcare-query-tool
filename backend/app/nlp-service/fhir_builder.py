"""
FHIR query construction from parsed criteria
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional

class FHIRQueryBuilder:
    def __init__(self):
        self.base_url = "http://hapi.fhir.org/baseR4"
    
    def build_condition_lookup_query(self, parsed_criteria: Dict) -> Optional[str]:
        """Builds a FHIR query to look up conditions and fetch patient IDs."""
        conditions = parsed_criteria.get("conditions")
        if not conditions:
            return None

        # Using SNOMED code for conditions as it's more specific.
        # We'll take the first condition found for simplicity.
        snomed_code = conditions[0]["codes"]["snomed"]
        
        # Limit to 1000 records as requested
        query_params = f"code=http://snomed.info/sct|{snomed_code}&_count=1000"
        
        return f"GET {self.base_url}/Condition?{query_params}"

    def build_patient_query(self, parsed_criteria: Dict, patient_ids: Optional[List[str]] = None) -> str:
        """Builds a FHIR query for the Patient resource."""
        query_params = []

        # If we have patient IDs from the condition search, use them.
        if patient_ids:
            if not patient_ids: # Handle case where condition search returned no patients
                query_params.append("_id=")
            else:
                query_params.append(f"_id={','.join(patient_ids)}")

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