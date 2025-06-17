"""
Medical entity recognition and condition mappings for healthcare queries
"""

import spacy
from typing import Dict, List

class MedicalEntityExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_md")
        
        # Medical condition mappings (simplified - in production, use comprehensive medical coding libraries)
        self.condition_codes = {
            # Diabetes
            "diabetes": {"icd10": "E11", "snomed": "73211009", "display": "Diabetes mellitus"},
            "diabetic": {"icd10": "E11", "snomed": "73211009", "display": "Diabetes mellitus"},
            # Hypertension
            "hypertension": {"icd10": "I10", "snomed": "38341003", "display": "Hypertension"},
            "hypertensive": {"icd10": "I10", "snomed": "38341003", "display": "Hypertension"},
            # Asthma
            "asthma": {"icd10": "J45", "snomed": "195967001", "display": "Asthma"},
            "asthmatic": {"icd10": "J45", "snomed": "195967001", "display": "Asthma"},
            # COPD
            "copd": {"icd10": "J44", "snomed": "13645005", "display": "COPD"},
            # Cancer
            "cancer": {"icd10": "C80", "snomed": "363346000", "display": "Malignant neoplasm"},
            "cancerous": {"icd10": "C80", "snomed": "363346000", "display": "Malignant neoplasm"},
            # COVID-19
            "covid": {"icd10": "U07.1", "snomed": "840539006", "display": "COVID-19"},
            # Pneumonia
            "pneumonia": {"icd10": "J18", "snomed": "233604007", "display": "Pneumonia"},
            # Heart Disease
            "heart disease": {"icd10": "I51", "snomed": "56265001", "display": "Heart disease"},
            # Stroke
            "stroke": {"icd10": "I64", "snomed": "230690007", "display": "Stroke"},
            # Anxiety
            "anxiety": {"icd10": "F41.9", "snomed": "48694002", "display": "Anxiety disorder"},
            "anxious": {"icd10": "F41.9", "snomed": "48694002", "display": "Anxiety disorder"},
            # Depression
            "depression": {"icd10": "F32.9", "snomed": "35489007", "display": "Depressive disorder"},
            "depressed": {"icd10": "F32.9", "snomed": "35489007", "display": "Depressive disorder"},
            # Migraine
            "migraine": {"icd10": "G43.9", "snomed": "37796009", "display": "Migraine"},
            # Arthritis
            "arthritis": {"icd10": "M19.90", "snomed": "3723001", "display": "Arthritis"},
            "arthritic": {"icd10": "M19.90", "snomed": "3723001", "display": "Arthritis"},
            # Obesity
            "obesity": {"icd10": "E66.9", "snomed": "414915002", "display": "Obesity"},
            "obese": {"icd10": "E66.9", "snomed": "414915002", "display": "Obesity"},
            # Allergy
            "allergy": {"icd10": "T78.40", "snomed": "418917006", "display": "Allergy to substance"},
            "allergic": {"icd10": "T78.40", "snomed": "418917006", "display": "Allergy to substance"},
            # Dementia
            "dementia": {"icd10": "F03", "snomed": "52448006", "display": "Dementia"},
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
    
    def extract_conditions(self, doc) -> List[Dict]:
        """Extract medical conditions from spaCy doc"""
        conditions = []
        # Normalization map for display purposes
        normalization_map = {
            "diabetic": "diabetes",
            "hypertensive": "hypertension",
            "asthmatic": "asthma",
            "cancerous": "cancer",
            "anxious": "anxiety",
            "depressed": "depression",
            "arthritic": "arthritis",
            "obese": "obesity",
            "allergic": "allergy",
        }

        for ent in doc.ents:
            if ent.label_ == "CONDITION":
                condition_text = ent.text.lower()
                if condition_text in self.condition_codes:
                    normalized_text = normalization_map.get(condition_text, condition_text)
                    conditions.append({
                        "text": normalized_text,
                        "codes": self.condition_codes[condition_text]
                    })
        return conditions
    
    def get_nlp_model(self):
        """Get the spaCy NLP model"""
        return self.nlp 