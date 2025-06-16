"""
FHIR query construction from parsed criteria
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, List

class FHIRQueryBuilder:
    def __init__(self):
        self.base_url = "[base]"
    
    def build_query(self, parsed_criteria: Dict) -> str:
        """Build FHIR query from parsed criteria"""
        resource = parsed_criteria.get("resource", "Patient")
        query_params = []
        
        if resource == "Patient":
            query_params = self._build_patient_query(parsed_criteria)
        elif resource == "Condition":
            query_params = self._build_condition_query(parsed_criteria)
        
        # Construct final URL
        if query_params:
            return f"GET {self.base_url}/{resource}?{'&'.join(query_params)}"
        else:
            return f"GET {self.base_url}/{resource}"
    
    def _build_patient_query(self, criteria: Dict) -> List[str]:
        """Build query parameters for Patient resource"""
        query_params = []
        
        # Handle conditions using _has parameter
        conditions = criteria.get("conditions", [])
        for condition in conditions:
            code = condition["codes"]["icd10"]
            query_params.append(f"_has:Condition:subject:code={code}")
        
        # Handle age criteria
        age_criteria = criteria.get("age_criteria")
        if age_criteria:
            birthdate_param = self._calculate_birthdate_from_age(
                age_criteria["value"],
                age_criteria["operator"]
            )
            if "&birthdate=" in birthdate_param:
                # Multiple parameters for exact age - split properly
                parts = birthdate_param.split("&")
                for part in parts:
                    if part.startswith("birthdate="):
                        query_params.append(part)
                    else:
                        query_params.append(f"birthdate={part}")
            else:
                # Single parameter for over/under age
                query_params.append(f"birthdate={birthdate_param}")
        
        # Handle gender
        gender = criteria.get("gender")
        if gender:
            query_params.append(f"gender={gender}")
        
        # Handle name criteria
        name_criteria = criteria.get("name_criteria")
        if name_criteria:
            if name_criteria["type"] == "starts_with":
                query_params.append(f"name:starts-with={name_criteria['value']}")
            elif name_criteria["type"] == "exact":
                query_params.append(f"name={name_criteria['value']}")
        
        return query_params
    
    def _build_condition_query(self, criteria: Dict) -> List[str]:
        """Build query parameters for Condition resource"""
        query_params = []
        
        # Direct condition queries
        conditions = criteria.get("conditions", [])
        for condition in conditions:
            code = condition["codes"]["icd10"]
            query_params.append(f"code={code}")
        
        # If age criteria specified for conditions, need to join with patient
        age_criteria = criteria.get("age_criteria")
        if age_criteria:
            birthdate_param = self._calculate_birthdate_from_age(
                age_criteria["value"],
                age_criteria["operator"]
            )
            query_params.append(f"subject.birthdate={birthdate_param}")
        
        # Handle gender for conditions
        gender = criteria.get("gender")
        if gender:
            query_params.append(f"subject.gender={gender}")
        
        return query_params
    
    def _calculate_birthdate_from_age(self, age: int, operator: str) -> str:
        """Calculate birthdate parameter based on age criteria"""
        today = datetime.now()
        
        if operator == "gt":  # over X years (person is older than X)
            # Born before this date (more than X years ago)
            target_date = today - relativedelta(years=age + 1)
            return f"lt{target_date.strftime('%Y-%m-%d')}"
        elif operator == "lt":  # under X years (person is younger than X)
            # Born after this date (less than X years ago)
            target_date = today - relativedelta(years=age)
            return f"gt{target_date.strftime('%Y-%m-%d')}"
        elif operator == "eq":  # exactly X years
            # Born between these dates
            start_date = today - relativedelta(years=age+1)
            end_date = today - relativedelta(years=age)
            return f"gt{start_date.strftime('%Y-%m-%d')}&birthdate=lt{end_date.strftime('%Y-%m-%d')}"
        
        return "" 