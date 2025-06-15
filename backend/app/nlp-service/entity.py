import spacy
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
from typing import Dict, Optional
import json

class FHIRQueryBuilder:
    def __init__(self):
        # Load SpaCy model
        self.nlp = spacy.load("en_core_web_md")
        
        # Medical condition mappings (simplified - in production, use comprehensive medical coding libraries)
        self.condition_codes = {
            "diabetes": {"icd10": "E11", "snomed": "73211009", "display": "Diabetes mellitus"},
            "hypertension": {"icd10": "I10", "snomed": "38341003", "display": "Hypertension"},
            "asthma": {"icd10": "J45", "snomed": "195967001", "display": "Asthma"},
            "copd": {"icd10": "J44", "snomed": "13645005", "display": "COPD"},
            "cancer": {"icd10": "C80", "snomed": "363346000", "display": "Malignant neoplasm"},
            "covid": {"icd10": "U07.1", "snomed": "840539006", "display": "COVID-19"},
            "pneumonia": {"icd10": "J18", "snomed": "233604007", "display": "Pneumonia"},
            "heart disease": {"icd10": "I51", "snomed": "56265001", "display": "Heart disease"},
            "stroke": {"icd10": "I64", "snomed": "230690007", "display": "Stroke"},
        }
        
        # Add custom pipeline components
        self._add_custom_entities()
    
    def _add_custom_entities(self):
        """Add custom entity patterns for medical terms"""
        # Add patterns for age expressions
        age_patterns = [
            {"label": "AGE", "pattern": [{"LOWER": "over"}, {"LIKE_NUM": True}, {"LOWER": {"IN": ["years", "year"]}}]},
            {"label": "AGE", "pattern": [{"LOWER": "above"}, {"LIKE_NUM": True}, {"LOWER": {"IN": ["years", "year"]}}]},
            {"label": "AGE", "pattern": [{"LOWER": "under"}, {"LIKE_NUM": True}, {"LOWER": {"IN": ["years", "year"]}}]},
            {"label": "AGE", "pattern": [{"LOWER": "below"}, {"LIKE_NUM": True}, {"LOWER": {"IN": ["years", "year"]}}]},
            {"label": "AGE", "pattern": [{"LIKE_NUM": True}, {"LOWER": {"IN": ["years", "year"]}, "OP": "?"}, {"LOWER": "old", "OP": "?"}]},
        ]
        
        # Add medical condition patterns
        condition_patterns = []
        for condition in self.condition_codes.keys():
            condition_patterns.append({"label": "CONDITION", "pattern": [{"LOWER": condition}]})
            if " " in condition:
                parts = condition.split()
                pattern = [{"LOWER": part} for part in parts]
                condition_patterns.append({"label": "CONDITION", "pattern": pattern})
        
        # Create ruler and add to pipeline
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns(age_patterns + condition_patterns)
    
    def parse_query(self, query: str) -> Dict:
        """Parse the natural language query and extract relevant information"""
        doc = self.nlp(query.lower())
        
        parsed_info = {
            "action": None,
            "resource": None,
            "conditions": [],
            "age_criteria": None,
            "gender": None,
            "name_criteria": None,
            "other_criteria": []
        }
        
        # Determine action (list, find, get, search, etc.)
        action_words = ["list", "find", "get", "search", "show", "display"]
        for token in doc:
            if token.text in action_words:
                parsed_info["action"] = token.text
                break
        
        # Determine primary resource - improved to include "people"
        query_lower = query.lower()
        if any(term in query_lower for term in ["patient", "patients", "people", "person"]):
            parsed_info["resource"] = "Patient"
        elif "condition" in query_lower or "diagnosis" in query_lower:
            parsed_info["resource"] = "Condition"
        
        # Extract conditions
        for ent in doc.ents:
            if ent.label_ == "CONDITION":
                condition_text = ent.text.lower()
                if condition_text in self.condition_codes:
                    parsed_info["conditions"].append({
                        "text": condition_text,
                        "codes": self.condition_codes[condition_text]
                    })
        
        # Extract age criteria
        age_criteria = self._extract_age_criteria(doc)
        if age_criteria:
            parsed_info["age_criteria"] = age_criteria
        
        # Extract gender - improved with word boundaries and proper ordering
        gender_info = self._extract_gender(query_lower)
        if gender_info:
            parsed_info["gender"] = gender_info
        
        # Extract name criteria
        name_criteria = self._extract_name_criteria(query)
        if name_criteria:
            parsed_info["name_criteria"] = name_criteria
        
        return parsed_info
    
    def _extract_gender(self, query_lower: str) -> Optional[str]:
        """Extract gender with improved word boundary matching"""
        # Use word boundaries to avoid partial matches
        # Order matters - check more specific terms first
        gender_patterns = [
            (r'\bfemale\b', 'female'),
            (r'\bwomen\b', 'female'),
            (r'\bmale\b', 'male'),
            (r'\bmen\b', 'male'),
        ]
        
        for pattern, gender in gender_patterns:
            if re.search(pattern, query_lower):
                return gender
        
        return None
    
    def _extract_name_criteria(self, query: str) -> Optional[Dict]:
        """Extract name-related search criteria"""
        # Look for name patterns like "name starts with", "name begins with", etc.
        name_patterns = [
            r'name\s+starts?\s+with\s+["`]?([^"`\s]+)["`]?',
            r'name\s+begins?\s+with\s+["`]?([^"`\s]+)["`]?',
            r'named\s+["`]?([^"`\s]+)["`]?',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, query.lower())
            if match:
                name_value = match.group(1)
                if "start" in pattern or "begin" in pattern:
                    return {"type": "starts_with", "value": name_value}
                else:
                    return {"type": "exact", "value": name_value}
        
        return None
    
    def _extract_age_criteria(self, doc) -> Optional[Dict]:
        """Extract age-related criteria from the parsed document"""
        age_info = None
        
        for ent in doc.ents:
            if ent.label_ == "AGE":
                # Extract the number and comparison operator
                text = ent.text.lower()
                number_match = re.search(r'\d+', text)
                
                if number_match:
                    age = int(number_match.group())
                    
                    if "over" in text or "above" in text:
                        age_info = {"operator": "gt", "value": age}
                    elif "under" in text or "below" in text:
                        age_info = {"operator": "lt", "value": age}
                    else:
                        age_info = {"operator": "eq", "value": age}
        
        return age_info
    
    def calculate_birthdate_from_age(self, age: int, operator: str) -> str:
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
    
    def build_fhir_query(self, parsed_info: Dict) -> str:
        """Build FHIR query from parsed information"""
        base_url = "[base]"
        resource = parsed_info["resource"] or "Patient"
        query_params = []
        
        if resource == "Patient":
            # Handle conditions using _has parameter
            for condition in parsed_info["conditions"]:
                # Use ICD-10 code by default, but could be configured
                code = condition["codes"]["icd10"]
                query_params.append(f"_has:Condition:subject:code={code}")
            
            # Handle age criteria
            if parsed_info["age_criteria"]:
                birthdate_param = self.calculate_birthdate_from_age(
                    parsed_info["age_criteria"]["value"],
                    parsed_info["age_criteria"]["operator"]
                )
                if "&" in birthdate_param:
                    # Multiple parameters for exact age
                    for param in birthdate_param.split("&"):
                        if param.startswith("birthdate="):
                            query_params.append(param)
                        else:
                            query_params.append(f"birthdate={param}")
                else:
                    query_params.append(f"birthdate={birthdate_param}")
            
            # Handle gender
            if parsed_info["gender"]:
                query_params.append(f"gender={parsed_info['gender']}")
            
            # Handle name criteria
            if parsed_info["name_criteria"]:
                name_info = parsed_info["name_criteria"]
                if name_info["type"] == "starts_with":
                    query_params.append(f"name:starts-with={name_info['value']}")
                elif name_info["type"] == "exact":
                    query_params.append(f"name={name_info['value']}")
        
        elif resource == "Condition":
            # Direct condition queries
            for condition in parsed_info["conditions"]:
                code = condition["codes"]["icd10"]
                query_params.append(f"code={code}")
            
            # If age criteria specified for conditions, need to join with patient
            if parsed_info["age_criteria"]:
                birthdate_param = self.calculate_birthdate_from_age(
                    parsed_info["age_criteria"]["value"],
                    parsed_info["age_criteria"]["operator"]
                )
                query_params.append(f"subject.birthdate={birthdate_param}")
            
            # Handle gender for conditions
            if parsed_info["gender"]:
                query_params.append(f"subject.gender={parsed_info['gender']}")
        
        # Construct final URL
        if query_params:
            return f"GET {base_url}/{resource}?{'&'.join(query_params)}"
        else:
            return f"GET {base_url}/{resource}"
    
    def process_query(self, natural_language_query: str) -> Dict:
        """Main method to process a natural language query"""
        # Parse the query
        parsed_info = self.parse_query(natural_language_query)
        
        # Build FHIR query
        fhir_query = self.build_fhir_query(parsed_info)
        
        return {
            "input": natural_language_query,
            "parsed": parsed_info,
            "fhir_query": fhir_query
        }


# Advanced features for better query building
class AdvancedFHIRQueryBuilder(FHIRQueryBuilder):
    def __init__(self):
        super().__init__()
        
        # Additional mappings for complex queries
        self.status_mappings = {
            "active": "active",
            "resolved": "resolved",
            "inactive": "inactive",
            "remission": "remission"
        }
        
        self.severity_mappings = {
            "severe": "severe",
            "moderate": "moderate", 
            "mild": "mild"
        }
    
    def parse_complex_criteria(self, query: str, parsed_info: Dict) -> Dict:
        """Parse more complex criteria from the query"""
        doc = self.nlp(query.lower())
        
        # Check for temporal expressions
        temporal_patterns = {
            "diagnosed in": "onset-date",
            "diagnosed after": "onset-date=gt",
            "diagnosed before": "onset-date=lt",
            "recorded in": "recorded-date",
            "active": "clinical-status=active",
            "resolved": "clinical-status=resolved"
        }
        
        for pattern, param in temporal_patterns.items():
            if pattern in query.lower():
                # Extract date if present
                date_match = re.search(r'\b(19|20)\d{2}\b', query)
                if date_match:
                    year = date_match.group()
                    if "=" in param:
                        parsed_info["other_criteria"].append(f"{param}{year}-01-01")
                    else:
                        parsed_info["other_criteria"].append(f"{param}={year}")
        
        return parsed_info

# Initialize the query builder
query_builder = AdvancedFHIRQueryBuilder()

# Example queries - updated and expanded
examples = [
    "list all female patients with diabetes over 50 years of age",
    "find patients that are male with hypertension",
    "show patients under 18 with asthma and are female",
    "get all active conditions for patients over 65",
    "list patients diagnosed with covid in 2023",
    "find male patients with heart disease over 40 years old",
    "Show me patients with hypertension and are male and below 18 years of age",
    "List all people with asthma that are male",
    "Show all people with diabetes whose name starts with Sid"
]

if __name__ == "__main__":
    for query in examples:
        result = query_builder.process_query(query)
        print(f"\nInput: {result['input']}")
        print(f"FHIR Query: {result['fhir_query']}")
        print(f"Parsed Info: {json.dumps(result['parsed'], indent=2)}")