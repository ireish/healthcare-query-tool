import requests
import re
from typing import List, Dict, Optional
from datetime import date
import random

def calculate_age(birth_date_str: Optional[str]) -> int:
    """Calculates age from a date string. Returns -1 for unknown/invalid dates."""
    if not birth_date_str:
        return -1
    try:
        birth_date = date.fromisoformat(birth_date_str)
        today = date.today()
        # Precise age calculation
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except (ValueError, TypeError):
        return -1

def extract_patient_name(names: Optional[List[Dict]]) -> str:
    """Extracts a patient's name from a list of name objects."""
    if not names:
        return "-"
    official_name = next((n for n in names if n.get('use') == 'official'), names[0])
    if official_name.get('text'):
        return official_name.get('text')
    
    parts = [
        *(official_name.get('prefix', [])),
        *(official_name.get('given', [])),
        official_name.get('family', ''),
    ]
    return ' '.join(filter(None, parts)).strip() or "-"

def extract_address_part(addresses: Optional[List[Dict]], part: str) -> str:
    """Extracts a specific part of an address (e.g., state, country)."""
    if not addresses:
        return "-"
    home_address = next((a for a in addresses if a.get('use') == 'home'), addresses[0])
    return home_address.get(part, "-")

def is_patient_alive(patient: Dict) -> str:
    """Determines if a patient is alive based on deceased flags."""
    if patient.get('deceasedBoolean') is True or patient.get('deceasedDateTime'):
        return "No"
    if patient.get('deceasedBoolean') is False:
        return "Yes"
    return "-"

def process_patient_resource(patient: Dict) -> Dict:
    """Processes a single FHIR Patient resource into our simplified display format."""
    age = calculate_age(patient.get("birthDate"))
    return {
        "id": patient.get("id", "-"),
        "name": extract_patient_name(patient.get("name")),
        "gender": patient.get("gender", "-").capitalize(),
        "age": str(age) if age != -1 else "-",
        "state": extract_address_part(patient.get("address"), "state"),
        "country": extract_address_part(patient.get("address"), "country"),
        "isAlive": is_patient_alive(patient),
        "_age_internal": age  # Internal field for filtering, removed before sending to frontend
    }

def execute_fhir_query(fhir_query: str) -> List[Dict]:
    """Executes the FHIR query, and then processes, filters, and samples the data."""
    url_match = re.search(r'GET\s+(.+)', fhir_query)
    if not url_match:
        print(f"Error: Invalid FHIR query format provided: {fhir_query}")
        return []
    
    base_url = url_match.group(1)
    separator = '&' if '?' in base_url else '?'
    fetch_url = f"{base_url}{separator}_count=5000"
    
    # Check if this is an age-based query by looking for birthdate parameter
    is_age_based_query = 'birthdate=' in fhir_query
    
    print(f"Fetching data from FHIR server: {fetch_url}")
    
    try:
        response = requests.get(fetch_url, headers={'Accept': 'application/fhir+json'}, timeout=30)
        response.raise_for_status()
        bundle = response.json()
        
        if bundle.get("resourceType") != "Bundle":
            return []
            
        entries = bundle.get("entry", [])
        if not entries:
            return []

        # Process all patient resources from the bundle
        all_patients = [process_patient_resource(e["resource"]) for e in entries if e.get("resource", {}).get("resourceType") == "Patient"]
        
        # --- Filtering and Sampling Logic ---
        # 1. Filter out patients with age > 110
        filtered_list = [p for p in all_patients if p["_age_internal"] <= 110]
        
        # 2. For age-based queries, ALWAYS filter out unknown ages to ensure data quality
        # For other queries, only filter unknown ages if we have more than 500 records
        if is_age_based_query or len(filtered_list) > 500:
            filtered_list = [p for p in filtered_list if p["_age_internal"] != -1]
        
        # 3. If count is still > 500, randomly sample 500 records
        if len(filtered_list) > 500:
            final_list = random.sample(filtered_list, 500)
        else:
            final_list = filtered_list
            
        # Clean up the internal age field before returning the data
        for p in final_list:
            del p["_age_internal"]
            
        print(f"Returning {len(final_list)} records to the frontend.")
        return final_list

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from FHIR server: {e}")
        return [] 