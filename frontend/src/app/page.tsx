"use client";

import { useState, useCallback } from "react";
import SearchBox from "../components/SearchBox";
import QuerySuggestions from "../components/QuerySuggestions";
import HistoryPanel, { HistoryItem } from "../components/HistoryPanel";

export default function Home() {
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const suggestions = [
    "Show me all diabetic patients over 50",
    "Hypertension trends",
    "Medication adherence rates by age group",
    "Risk factors analysis",
  ];

  const handleSearch = useCallback(async (query: string) => {
    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) throw new Error("Failed to query service");

      const data = await res.json();
      const resultText: string = data.result ?? data.message ?? "No result";

      const newItem: HistoryItem = {
        query,
        result: resultText,
        timestamp: new Date().toLocaleString(),
      };

      setHistory((prev) => [newItem, ...prev]);
    } catch (err) {
      console.error(err);
      const newItem: HistoryItem = {
        query,
        result: "Error contacting service",
        timestamp: new Date().toLocaleString(),
      };
      setHistory((prev) => [newItem, ...prev]);
    }
  }, []);

  return (
    <div className="flex flex-1">
      {/* Left history panel */}
      <HistoryPanel items={history} />

      {/* Main content */}
      <main className="flex flex-col flex-1 items-center justify-start py-12 gap-6 px-4 sm:px-8">
        <SearchBox onSearch={handleSearch} />
        <QuerySuggestions suggestions={suggestions} onSelect={handleSearch} />
      </main>
    </div>
  );
}
