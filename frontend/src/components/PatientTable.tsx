"use client";

import React, { useState, useEffect, useMemo } from "react";
import dynamic from "next/dynamic";
import { PatientDisplayData } from "@/types";

// Dynamically import charts to avoid SSR issues
const PatientCharts = dynamic(() => import("./PatientCharts"), { ssr: false });

interface PatientTableProps {
  patientData: PatientDisplayData[];
}

export default function PatientTable({ patientData }: PatientTableProps) {
  // The 'patients' state is initialized from props and used for local filtering
  const [patients, setPatients] = useState<PatientDisplayData[]>(patientData);
  // The record count is based on the initial unfiltered data from props
  const [recordCount, setRecordCount] = useState<number>(patientData.length);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const patientsPerPage = 10;

  // Filter states
  const [ageRange, setAgeRange] = useState({ min: "", max: "" });
  const [genderFilter, setGenderFilter] = useState("All");
  const [countryFilter, setCountryFilter] = useState("All");
  const [aliveFilter, setAliveFilter] = useState("All");

  // When the initial patientData prop changes, reset the component's state
  useEffect(() => {
    setPatients(patientData);
    setRecordCount(patientData.length);
    setCurrentPage(1); // Reset to first page
  }, [patientData]);

  // Memoized lists for filter dropdowns
  const availableCountries = useMemo(() => {
    const countries = new Set(patients.map(p => p.country).filter(c => c && c !== "-"));
    return ["All", ...Array.from(countries).sort()];
  }, [patients]);

  // Memoized filtered patients (for client-side filtering)
  const filteredPatients = useMemo(() => {
    let result = patients;

    // Apply age range filter
    if (ageRange.min) {
        result = result.filter(p => p.age !== '-' && parseInt(p.age, 10) >= parseInt(ageRange.min, 10));
    }
    if (ageRange.max) {
        result = result.filter(p => p.age !== '-' && parseInt(p.age, 10) <= parseInt(ageRange.max, 10));
    }
    // Apply gender filter
    if (genderFilter !== "All") {
      if (genderFilter === "Other") {
        result = result.filter(p => p.gender !== 'Male' && p.gender !== 'Female');
      } else {
        result = result.filter(p => p.gender === genderFilter);
      }
    }
    // Apply country filter
    if (countryFilter !== "All") {
        result = result.filter(p => p.country === countryFilter);
    }
    // Apply alive status filter
    if (aliveFilter !== "All") {
        result = result.filter(p => p.isAlive === aliveFilter);
    }
    return result;
  }, [patients, ageRange, genderFilter, countryFilter, aliveFilter]);

  // Effect to reset page to 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [ageRange, genderFilter, countryFilter, aliveFilter]);
  
  const totalPages = Math.ceil(filteredPatients.length / patientsPerPage);
  const paginatedPatients = filteredPatients.slice((currentPage - 1) * patientsPerPage, currentPage * patientsPerPage);

  return (
    <div className="w-full max-w-7xl mx-auto mt-6">
      <div className="bg-white rounded-lg shadow-md border border-gray-200">
        {/* Header and Filters */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-800">
              Patient Data Results
            </h3>
            <p className="text-sm text-gray-600">
              {`Displaying ${filteredPatients.length} of ${recordCount} Records`}
            </p>
          </div>
        </div>

        {/* Filter UI */}
        <div className="p-4 bg-gray-50 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
              <label className="text-sm font-medium text-gray-700">Age Range</label>
              <div className="flex items-center space-x-2 mt-1">
                  <input type="number" placeholder="Min" value={ageRange.min} onChange={e => setAgeRange({...ageRange, min: e.target.value})} className="p-2 border rounded-md w-full text-sm text-gray-900 placeholder-gray-500"/>
                  <input type="number" placeholder="Max" value={ageRange.max} onChange={e => setAgeRange({...ageRange, max: e.target.value})} className="p-2 border rounded-md w-full text-sm text-gray-900 placeholder-gray-500"/>
              </div>
          </div>
          <div>
              <label className="text-sm font-medium text-gray-700">Gender</label>
              <select value={genderFilter} onChange={e => setGenderFilter(e.target.value)} className="p-2 border rounded-md w-full mt-1 text-sm text-gray-900">
                  <option>All</option>
                  <option>Male</option>
                  <option>Female</option>
                  <option>Other</option>
              </select>
          </div>
          <div>
              <label className="text-sm font-medium text-gray-700">Country</label>
              <select value={countryFilter} onChange={e => setCountryFilter(e.target.value)} className="p-2 border rounded-md w-full mt-1 text-sm text-gray-900">
                  {availableCountries.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
          </div>
          <div>
              <label className="text-sm font-medium text-gray-700">Status</label>
              <select value={aliveFilter} onChange={e => setAliveFilter(e.target.value)} className="p-2 border rounded-md w-full mt-1 text-sm text-gray-900">
                  <option>All</option>
                  <option>Yes</option>
                  <option>No</option>
              </select>
          </div>
        </div>

        {/* Table */}
        {paginatedPatients.length > 0 && (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Gender
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Age
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    State
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Country
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Is Alive?
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {paginatedPatients.map((patient, index) => (
                  <tr key={patient.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {patient.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {patient.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {patient.gender}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {patient.age}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {patient.state}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {patient.country}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        patient.isAlive === "Yes" 
                          ? "bg-green-100 text-green-800" 
                          : patient.isAlive === "No" 
                            ? "bg-red-100 text-red-800" 
                            : "bg-gray-100 text-gray-800"
                      }`}>
                        {patient.isAlive}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* No Data State */}
        {filteredPatients.length === 0 && (
          <div className="p-12 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No patient data found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {patients.length > 0 ? "No patients match the current filter criteria." : "Your query returned no matching patients."}
            </p>
          </div>
        )}
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between my-4 px-6">
            <span className="text-sm text-gray-600">
              Page {currentPage} of {totalPages}
            </span>
            <div className="flex items-center space-x-2">
              <button
                className={`px-3 py-1 rounded-md border border-black text-black text-sm ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100'}`}
                onClick={() => currentPage > 1 && setCurrentPage(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Prev
              </button>
             
              <button
                className={`px-3 py-1 rounded-md border border-black text-black text-sm ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100'}`}
                onClick={() => currentPage < totalPages && setCurrentPage(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Charts */}
        {filteredPatients.length > 0 && (
          <PatientCharts patients={filteredPatients} />
        )}
      </div>
    </div>
  );
} 