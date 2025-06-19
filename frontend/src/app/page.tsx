"use client";

import { useState, useCallback, useEffect } from "react";
import SearchBox from "../components/SearchBox";
import QuerySuggestions from "../components/QuerySuggestions";
import PatientTable from "../components/PatientTable";
import { APIResponse, PatientDisplayData } from "@/types";

// A larger pool of potential query suggestions based on the backend entities.
const allSuggestions = [
  "Show me all diabetic patients over 50",
  "List all female patients with hypertension",
  "Find male patients with asthma under 18",
  "Show people with anxiety whose name starts with Jo",
  "Show many patients have been diagnosed with cancer?",
  "List patients with obesity over 30",
  "Show me patients with dementia",
  "Find patients with a history of stroke",
  "List all patients with a recorded allergy",
  "List patients that are suffering from depression?",
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
  const [patientData, setPatientData] = useState<PatientDisplayData[]>([]);
  const [fhirQuery, setFhirQuery] = useState<string>("");
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
    setPatientData([]);
    setFhirQuery("");
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

      const data: APIResponse = await res.json();
      
      if (data.success) {
        setFhirQuery(data.fhir_query);
        if (data.data === "UNSUPPORTED_CONDITION") {
          setError("The condition you mentioned is not currently supported. Please try a different medical term.");
          setPatientData([]);
        } else {
          setPatientData(data.data as PatientDisplayData[]);
        }
      } else {
        setError(data.error || "Failed to fetch data from the backend.");
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
        
        {/* Box to show query, loading, error, or generated API */}
        {currentQuery && (
          <div className="w-full max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Your Query:</h3>
              <p className="text-gray-700 mb-4 p-3 bg-gray-50 rounded border-l-4 border-blue-500">
                &quot;{currentQuery}&quot;
              </p>

              {isLoading ? (
                <div className="flex items-center justify-center p-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-3 text-gray-600">Processing query and fetching data...</span>
                </div>
              ) : error ? (
                <div className="bg-red-100 text-red-700 p-4 rounded-lg text-sm">{error}</div>
              ) : fhirQuery && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Generated FHIR API:</h3>
                  <div className="bg-gray-900 text-green-400 p-3 mt-1 rounded-lg font-mono text-sm max-h-48 overflow-y-auto">
                    <pre className="whitespace-pre-wrap break-words">{fhirQuery}</pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Patient Data Table - Renders only when data is available */}
        {!isLoading && !error && patientData.length > 0 && (
          <PatientTable patientData={patientData} />
        )}
        
      </main>
    </div>
  );
}
