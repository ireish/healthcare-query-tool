"use client";

import React from "react";

export default function Header() {
  return (
    <header className="flex items-center gap-3 py-4 px-6 border-b border-gray-200 bg-white shadow-sm">
      <span className="text-3xl" role="img" aria-label="health-icon">
        🩺
      </span>
      <h1 className="text-2xl font-bold font-[family-name:var(--font-pt-serif)] text-gray-900">
        HEALTH QUERY AI ( FHIR - Complaint )  
      </h1>
    </header>
  );
} 