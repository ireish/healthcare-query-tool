"use client";

import React from "react";

interface QuerySuggestionsProps {
  suggestions: string[];
  onSelect: (query: string) => void;
}

export default function QuerySuggestions({
  suggestions,
  onSelect,
}: QuerySuggestionsProps) {
  return (
    <div className="flex flex-wrap gap-2 justify-center sm:justify-start">
      {suggestions.map((text) => (
        <button
          key={text}
          onClick={() => onSelect(text)}
          className="bg-gray-100 hover:bg-gray-200 text-gray-900 text-sm px-3 py-1 rounded-full transition whitespace-nowrap"
        >
          {text}
        </button>
      ))}
    </div>
  );
} 