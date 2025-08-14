"""
LLM-backed service for converting natural language queries into FHIR Patient queries.

This replaces the previous spaCy-based NLP pipeline with a single LLM call to
extract structured criteria, which are then converted into a valid FHIR query
using the existing FHIRQueryBuilder.
"""

import os
import json
from typing import Optional, Dict

from fhir_builder import FHIRQueryBuilder

try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except Exception:
    # Library not available until requirements are installed
    _GENAI_AVAILABLE = False


SYSTEM_INSTRUCTIONS = (
    "You are a medical data assistant that extracts criteria from natural-language "
    "questions to build FHIR R4 Patient REST queries against the base URL "
    "http://hapi.fhir.org/baseR4.\n\n"
    "Output ONLY a compact JSON object with this schema and no extra text: \n"
    "{\n"
    "  \"resource\": \"Patient\",\n"
    "  \"conditions\": [{\"text\": string, \"codes\": {\"snomed\": string}}] | null,\n"
    "  \"age_criteria\": {\"operator\": \"gt\"|\"lt\"|\"eq\", \"value\": number} | null,\n"
    "  \"gender\": \"male\"|\"female\"|null,\n"
    "  \"name_criteria\": {\"type\": \"starts_with\"|\"exact\", \"value\": string} | null\n"
    "}\n\n"
    "Only map conditions to SNOMED using this allowed list. If the question mentions a "
    "condition not in this list, return exactly the string UNSUPPORTED_CONDITION (no JSON).\n"
    "Allowed condition → SNOMED mappings: \n"
    "diabetes: 73211009\n"
    "hypertension: 38341003\n"
    "asthma: 195967001\n"
    "copd: 13645005\n"
    "cancer: 363346000\n"
    "covid: 840539006\n"
    "pneumonia: 233604007\n"
    "heart disease: 56265001\n"
    "stroke: 230690007\n"
    "anxiety: 48694002\n"
    "depression: 35489007\n"
    "migraine: 37796009\n"
    "arthritis: 3723001\n"
    "obesity: 414915002\n"
    "allergy: 418917006\n"
    "dementia: 52448006\n\n"
    "Guidelines: \n"
    "- resource must be \"Patient\".\n"
    "- gender only if explicitly mentioned.\n"
    "- age_criteria: convert phrasing like 'over 50'→{operator:'gt',value:50}, 'under 18'→{operator:'lt',value:18}.\n"
    "- name_criteria: support 'name starts with X' or 'named X'.\n"
)


class LLMQueryService:
    def __init__(self):
        self.fhir_builder = FHIRQueryBuilder()
        self.api_key = os.environ.get("GOOGLE_GENAI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.model_name = os.environ.get("GENAI_MODEL", "gemini-1.5-flash")
        self._model = None
        if _GENAI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
            except Exception:
                self._model = None

    def _call_llm(self, natural_language_query: str) -> Optional[str]:
        if not _GENAI_AVAILABLE or not self._model:
            return None
        prompt = (
            SYSTEM_INSTRUCTIONS
            + "\nQuestion: "
            + natural_language_query.strip()
            + "\nRespond with JSON only or UNSUPPORTED_CONDITION."
        )
        try:
            response = self._model.generate_content(prompt)
            text = (response.text or "").strip()
            return text
        except Exception:
            return None

    def _parse_json(self, text: str) -> Optional[Dict]:
        try:
            return json.loads(text)
        except Exception:
            return None

    def process_query(self, natural_language_query: str) -> Dict[str, Optional[str]]:
        """
        Use an LLM to extract structured criteria, then build the FHIR Patient query.
        Returns a dict with key 'fhir_query'. If a condition is unsupported, returns
        {'fhir_query': 'UNSUPPORTED_CONDITION'}.
        """
        llm_text = self._call_llm(natural_language_query)

        # If LLM unavailable or failed, gracefully return unsupported to avoid bad queries
        if not llm_text:
            return {"fhir_query": "UNSUPPORTED_CONDITION"}

        if llm_text.strip().upper() == "UNSUPPORTED_CONDITION":
            return {"fhir_query": "UNSUPPORTED_CONDITION"}

        parsed_criteria = self._parse_json(llm_text)
        if not parsed_criteria or parsed_criteria.get("resource") != "Patient":
            return {"fhir_query": "UNSUPPORTED_CONDITION"}

        patient_query = self.fhir_builder.build_patient_query(parsed_criteria)
        return {"fhir_query": patient_query}


# Global instance for the service, matching the previous import contract
llm_service = LLMQueryService()