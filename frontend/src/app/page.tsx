"use client";

import { useState, useCallback, useEffect } from "react";
import SearchBox from "../components/SearchBox";
import QuerySuggestions from "../components/QuerySuggestions";
import PatientTable from "../components/PatientTable";
import { FHIRQueryResponse } from "@/types";

// A larger pool of potential query suggestions based on the backend entities.
const allSuggestions = [
  "Show me all diabetic patients over 50",
  "List all female patients with hypertension",
  "Find male patients with asthma under 18",
  "Show people with anxiety whose name starts with 'A'",
  "How many patients have been diagnosed with cancer?",
  "List patients with obesity over 30",
  "Show me patients with dementia located in the US",
  "Find patients with a history of stroke",
  "List all patients with a recorded allergy",
  "How many patients are suffering from depression?",
  "Show me arthritic patients over the age of 65",
  "Find patients diagnosed with COPD",
  "List all patients with a history of migraines",
  "Show me patients who have had pneumonia",
  "Find patients with any kind of heart disease",
];

// Function to get N random items from an array
const getRandomSuggestions = (count: number): string[] => {
  const shuffled = [...allSuggestions].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
};

export default function Home() {
  const [currentQuery, setCurrentQuery] = useState<string>("");
  const [fhirQueryCondition, setFhirQueryCondition] = useState<string | null>(null);
  const [fhirQueryPatient, setFhirQueryPatient] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);

  // On component mount, select 4 random suggestions to display.
  useEffect(() => {
    setSuggestions(getRandomSuggestions(4));
  }, []);

  const handleSearch = useCallback(async (query: string) => {
    setIsLoading(true);
    setCurrentQuery(query);
    setFhirQueryCondition(null);
    setFhirQueryPatient("");
    setError(null);

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data: FHIRQueryResponse = await res.json();
      
      if (data.success) {
        setFhirQueryCondition(data.condition_query || null);
        setFhirQueryPatient(data.patient_query);
      } else {
        setError(data.error || "Failed to generate FHIR query");
      }

    } catch (err) {
      console.error("Search error:", err);
      const errorMessage = "Error: Unable to process query. Please check if the backend service is running.";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="flex flex-1">
      {/* Main content */}
      <main className="flex flex-col flex-1 items-center justify-start py-12 gap-6 px-4 sm:px-8">
        <SearchBox onSearch={handleSearch} />
        <QuerySuggestions suggestions={suggestions} onSelect={handleSearch} />
        
        {/* Current Query Display */}
        {currentQuery && (
          <div className="w-full max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                Your Query:
              </h3>
              <p className="text-gray-700 mb-4 p-3 bg-gray-50 rounded border-l-4 border-blue-500">
                &quot;{currentQuery}&quot;
              </p>
              
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                Generated FHIR APIs:
              </h3>
              
              {isLoading ? (
                <div className="flex items-center justify-center p-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-3 text-gray-600">Processing query...</span>
                </div>
              ) : error ? (
                <div className="bg-red-100 text-red-700 p-4 rounded-lg font-mono text-sm">
                  {error}
                </div>
              ) : (
                <div className="space-y-4">
                  {fhirQueryPatient && (
                    <div>
                      <label className="text-sm font-medium text-gray-600">1. Condition Resource API</label>
                      <div className="bg-gray-900 p-3 mt-1 rounded-lg font-mono text-sm overflow-x-auto">
                        <pre className={`whitespace-pre-wrap break-words ${fhirQueryCondition ? 'text-green-400' : 'text-gray-400'}`}>
                          {fhirQueryCondition || "No Disease/Condition identified"}
                        </pre>
                      </div>
                    </div>
                  )}
                  {fhirQueryPatient && (
                    <div>
                      <label className="text-sm font-medium text-gray-600">{fhirQueryCondition ? "2. Patient Resource API" : "Patient Resource API"}</label>
                      <div className="bg-gray-900 text-green-400 p-3 mt-1 rounded-lg font-mono text-sm max-h-24 overflow-y-auto">
                        <pre className="whitespace-pre-wrap break-words">
                          {fhirQueryPatient}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Patient Data Table - Shows below the FHIR query */}
        {fhirQueryPatient && !isLoading && !error && (
          <PatientTable fhirQuery={fhirQueryPatient} />
        )}
        
      </main>
    </div>
  );
}
