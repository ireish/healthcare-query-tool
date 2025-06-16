"use client";

import { useState, useCallback } from "react";
import SearchBox from "../components/SearchBox";
import QuerySuggestions from "../components/QuerySuggestions";
import HistoryPanel, { HistoryItem } from "../components/HistoryPanel";

// Type for FHIR query response
interface FHIRQueryResponse {
  fhir_query: string;
  success: boolean;
  error?: string;
}

export default function Home() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [currentQuery, setCurrentQuery] = useState<string>("");
  const [currentResult, setCurrentResult] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const suggestions = [
    "Show me all diabetic patients over 50",
    "List all female patients with hypertension",
    "Find male patients with asthma under 18",
    "Show people with diabetes whose name starts with John",
  ];

  const handleSearch = useCallback(async (query: string) => {
    setIsLoading(true);
    setCurrentQuery(query);
    setCurrentResult("");

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
      
      let resultText: string;
      if (data.success && data.fhir_query) {
        resultText = data.fhir_query;
      } else {
        resultText = data.error || "Failed to generate FHIR query";
      }

      setCurrentResult(resultText);

      // Add to history
      const newItem: HistoryItem = {
        query,
        result: resultText,
        timestamp: new Date().toLocaleString(),
      };

      setHistory((prev) => [newItem, ...prev]);
    } catch (err) {
      console.error("Search error:", err);
      const errorMessage = "Error: Unable to process query. Please check if the backend service is running.";
      setCurrentResult(errorMessage);
      
      const newItem: HistoryItem = {
        query,
        result: errorMessage,
        timestamp: new Date().toLocaleString(),
      };
      setHistory((prev) => [newItem, ...prev]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return (
    <div className="flex flex-1">
      {/* Left history panel */}
      <HistoryPanel items={history} />

      {/* Main content */}
      <main className="flex flex-col flex-1 items-center justify-start py-12 gap-6 px-4 sm:px-8">
        <SearchBox onSearch={handleSearch} />
        
        {/* Current Query Display */}
        {currentQuery && (
          <div className="w-full max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                Your Query:
              </h3>
              <p className="text-gray-700 mb-4 p-3 bg-gray-50 rounded border-l-4 border-blue-500">
                "{currentQuery}"
              </p>
              
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                Generated FHIR Query:
              </h3>
              
              {isLoading ? (
                <div className="flex items-center justify-center p-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-3 text-gray-600">Processing query...</span>
                </div>
              ) : currentResult ? (
                <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                  <pre className="whitespace-pre-wrap break-words">
                    {currentResult}
                  </pre>
                </div>
              ) : null}
            </div>
          </div>
        )}
        
        <QuerySuggestions suggestions={suggestions} onSelect={handleSearch} />
      </main>
    </div>
  );
}
