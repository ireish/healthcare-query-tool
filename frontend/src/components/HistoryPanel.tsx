"use client";

import React from "react";

export interface HistoryItem {
  query: string;
  result: string;
  timestamp: string;
}

interface HistoryPanelProps {
  items: HistoryItem[];
  onSelect?: (item: HistoryItem) => void;
}

export default function HistoryPanel({ items, onSelect }: HistoryPanelProps) {
  return (
    <aside className="w-64 bg-gray-50 text-gray-900 border-r border-gray-200 p-4 h-screen overflow-y-auto">
      <h2 className="font-semibold mb-4">Query History</h2>
      <ul className="space-y-3">
        {items.length === 0 && (
          <li className="text-sm text-gray-500">No queries yet</li>
        )}
        {items.map((item, idx) => (
          <li key={`${item.query}-${idx}`}>
            <button
              className="w-full text-left bg-white border border-gray-200 rounded-md p-2 hover:bg-gray-100"
              onClick={() => onSelect?.(item)}
            >
              <p className="text-sm font-medium truncate">{item.query}</p>
              <p className="text-xs text-gray-500">
                {item.result} • {item.timestamp}
              </p>
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
} 