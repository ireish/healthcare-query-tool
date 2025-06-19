#!/usr/bin/env python3
"""
Test script for the Healthcare Query Tool API
"""

import requests
import json
import sys

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running on port 8000?")
        return False

def test_api_endpoint():
    """Test the main API query processing endpoint"""
    test_queries = [
        "List all female patients with diabetes over 50 years of age",
        "Show me patients with hypertension and are male and below 18 years of age",
        "List all people with asthma that are male",
        "Show all people with diabetes whose name starts with Sid"
    ]
    
    for query in test_queries:
        try:
            print(f"\n🔍 Testing query: {query}")
            response = requests.post(
                "http://localhost:8000/api/query",
                headers={"Content-Type": "application/json"},
                json={"query": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Query processed successfully")
                print(f"   FHIR Query: {data.get('fhir_query', 'None')}")
                print(f"   Success: {data.get('success', False)}")
                if data.get('error'):
                    print(f"   Error: {data.get('error')}")
            else:
                print(f"❌ Query failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server")
            return False
    
    return True

def main():
    print("🧪 Testing Healthcare Query Tool API")
    print("=" * 50)
    
    # Test health endpoint
    if not test_health_endpoint():
        print("\n❌ Health check failed. Exiting.")
        sys.exit(1)
    
    # Test main API endpoint
    if not test_api_endpoint():
        print("\n❌ API endpoint tests failed.")
        sys.exit(1)
    
    print("\n🎉 All tests passed!")
    print("\nYou can now:")
    print("1. Visit http://localhost:8000/docs for API documentation")
    print("2. Start the frontend with 'npm run dev' in the frontend directory")
    print("3. Access the web app at http://localhost:3000")

if __name__ == "__main__":
    main() 