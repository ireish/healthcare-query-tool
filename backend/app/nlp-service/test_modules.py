#!/usr/bin/env python3
"""
Test script for the modular NLP components
"""

from nlp_service import nlp_service

def test_modular_components():
    """Test the modular NLP service with sample queries"""
    test_queries = [
        "List all female patients with diabetes over 50 years of age",
        "Show me patients with hypertension and are male and below 18 years of age", 
        "List all people with asthma that are male",
        "Show all people with diabetes whose name starts with Sid"
    ]
    
    print("🧪 Testing Modular NLP Components")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Input Query: {query}")
        try:
            fhir_query = nlp_service.process_query(query)
            print(f"   FHIR Query: {fhir_query}")
            print("   ✅ Success")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 Modular component testing completed!")

if __name__ == "__main__":
    test_modular_components() 