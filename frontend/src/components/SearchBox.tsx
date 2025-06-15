"use client";

import React, { useState } from "react";

interface SearchBoxProps {
  onSearch: (query: string) => void;
}

export default function SearchBox({ onSearch }: SearchBoxProps) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed) return;
    onSearch(trimmed);
    setValue("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex w-full max-w-2xl mx-auto"
    >
      <input
        type="text"
        placeholder="Ask about patient data, conditions, treatments..."
        className="flex-grow bg-white text-gray-900 rounded-l-md border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-3 rounded-r-md hover:bg-blue-700 text-sm sm:text-base"
      >
        Query
      </button>
    </form>
  );
} 