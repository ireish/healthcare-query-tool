"""
Medical entity recognition and condition mappings for healthcare queries
"""

import spacy
from typing import Dict, List

class MedicalEntityExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_md")
        
        # A single source of truth for medical codes, using the base condition term as the key.
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
            "anxiety": {"icd10": "F41.9", "snomed": "48694002", "display": "Anxiety disorder"},
            "depression": {"icd10": "F32.9", "snomed": "35489007", "display": "Depressive disorder"},
            "migraine": {"icd10": "G43.9", "snomed": "37796009", "display": "Migraine"},
            "arthritis": {"icd10": "M19.90", "snomed": "3723001", "display": "Arthritis"},
            "obesity": {"icd10": "E66.9", "snomed": "414915002", "display": "Obesity"},
            "allergy": {"icd10": "T78.40", "snomed": "418917006", "display": "Allergy to substance"},
            "dementia": {"icd10": "F03", "snomed": "52448006", "display": "Dementia"},
        }
        
        # Map aliases (adjective forms, etc.) to the base condition term.
        self.condition_aliases = {
            "diabetic": "diabetes",
            "hypertensive": "hypertension",
            "asthmatic": "asthma",
            "cancerous": "cancer",
            "anxious": "anxiety",
            "depressed": "depression",
            "arthritic": "arthritis",
            "obese": "obesity",
            "allergic": "allergy",
            "migraine": "migraines",
        }
        
        self._setup_entity_patterns()
    
    def _setup_entity_patterns(self):
        """Add custom entity patterns for medical terms"""
        # Add patterns for age expressions
        age_patterns = [
            {"label": "AGE", "pattern": [{"LOWER": "over"}, {"LIKE_NUM": True}, {"LOWER": {"IN": ["years", "year"]}}]},
            {"label": "AGE", "pattern": [{"LOWER": "above"}, {"LIKE_NUM": True}, {"LOWER": {"IN": ["years", "year"]}}]},
            {"label": "AGE", "pattern": [{"LOWER": "under"}, {"LIKE_NUM": True}, {"LOWER": {"IN": ["years", "year"]}}]},
            {"label": "AGE", "pattern": [{"LOWER": "below"}, {"LIKE_NUM": True}, {"LOWER": {"IN": ["years", "year"]}}]},
            {"label": "AGE", "pattern": [{"LIKE_NUM": True}, {"LOWER": {"IN": ["years", "year"]}, "OP": "?"}, {"LOWER": "old", "OP": "?"}]},
        ]
        
        # Create patterns for all base conditions and their aliases
        condition_patterns = []
        all_condition_terms = list(self.condition_codes.keys()) + list(self.condition_aliases.keys())
        
        for condition in all_condition_terms:
            condition_patterns.append({"label": "CONDITION", "pattern": [{"LOWER": condition}]})
            # Handle multi-word conditions like "heart disease"
            if " " in condition:
                parts = condition.split()
                pattern = [{"LOWER": part} for part in parts]
                condition_patterns.append({"label": "CONDITION", "pattern": pattern})
        
        # Create ruler and add to pipeline
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns(age_patterns + condition_patterns)
    
    def extract_conditions(self, doc) -> List[Dict]:
        """Extract medical conditions and normalize them using the alias map."""
        conditions = []
        for ent in doc.ents:
            if ent.label_ == "CONDITION":
                condition_text = ent.text.lower()
                
                # Normalize the extracted term using the alias map. If not found, use the term itself.
                normalized_text = self.condition_aliases.get(condition_text, condition_text)
                
                # Look up codes using the normalized base term.
                if normalized_text in self.condition_codes:
                    conditions.append({
                        "text": normalized_text,
                        "codes": self.condition_codes[normalized_text]
                    })
        return conditions
    
    def get_nlp_model(self):
        """Get the spaCy NLP model"""
        return self.nlp 