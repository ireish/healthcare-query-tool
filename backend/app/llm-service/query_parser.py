"""
Natural language query parsing and criteria extraction
"""

import re
from typing import Optional, Dict, List
from medical_entities import MedicalEntityExtractor

class QueryParser:
    def __init__(self, medical_extractor: MedicalEntityExtractor):
        self.medical_extractor = medical_extractor
        self.nlp = medical_extractor.get_nlp_model()
    
    def parse_query(self, query: str) -> Dict:
        """Parse the natural language query and extract relevant information"""
        doc = self.nlp(query.lower())
        
        # Extract primary resource
        resource = self._extract_resource(query.lower())
        
        # Extract conditions
        conditions = self.medical_extractor.extract_conditions(doc)
        
        # Extract age criteria
        age_criteria = self._extract_age_criteria(doc)
        
        # Extract gender
        gender = self._extract_gender(query.lower())
        
        # Extract name criteria
        name_criteria = self._extract_name_criteria(query)
        
        return {
            "resource": resource,
            "conditions": conditions,
            "age_criteria": age_criteria,
            "gender": gender,
            "name_criteria": name_criteria
        }
    
    def _extract_resource(self, query_lower: str) -> str:
        """Determine primary FHIR resource type"""
        if any(term in query_lower for term in ["patient", "patients", "people", "person"]):
            return "Patient"
        elif "condition" in query_lower or "diagnosis" in query_lower:
            return "Condition"
        return "Patient"  # Default to Patient
    
    def _extract_gender(self, query_lower: str) -> Optional[str]:
        """Extract gender with improved word boundary matching"""
        # Use word boundaries to avoid partial matches
        # Order matters - check more specific terms first
        gender_patterns = [
            (r'\bfemale\b', 'female'),
            (r'\bwomen\b', 'female'),
            (r'\bwoman\b', 'female'),
            (r'\bgirl\b', 'female'),
            (r'\bgirls\b', 'female'),
            (r'\bmale\b', 'male'),
            (r'\bmen\b', 'male'),
            (r'\bman\b', 'male'),
            (r'\bboy\b', 'male'),
            (r'\bboys\b', 'male'),
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
        # First try existing entity-based extraction
        age_info = None
        
        for ent in doc.ents:
            if ent.label_ == "AGE":
                text = ent.text.lower()
                number_match = re.search(r'\d+', text)
                if number_match:
                    age = int(number_match.group())
                    if "over" in text or "above" in text:
                        age_info = {"operator": "gt", "value": age}
                    elif "under" in text or "below" in text:
                        age_info = {"operator": "lt", "value": age}
                    else:
                        # Determine operator by searching the full query context
                        full_query = doc.text.lower()
                        if re.search(r'(under|below)\s+%d' % age, full_query):
                            age_info = {"operator": "lt", "value": age}
                        elif re.search(r'(over|above)\s+%d' % age, full_query):
                            age_info = {"operator": "gt", "value": age}
                        else:
                            age_info = {"operator": "eq", "value": age}
        
        # Fallback regex approach if entity extraction failed
        if age_info is None:
            # Look for patterns like "under 18", "over 65" without the word years
            pattern_map = {
                r'under\s+(\d+)': "lt",
                r'below\s+(\d+)': "lt",
                r'over\s+(\d+)': "gt",
                r'above\s+(\d+)': "gt",
            }
            query_text = doc.text.lower()
            for pattern, op in pattern_map.items():
                match = re.search(pattern, query_text)
                if match:
                    age = int(match.group(1))
                    age_info = {"operator": op, "value": age}
                    break
        
        return age_info 