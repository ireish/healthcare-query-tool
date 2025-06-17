"use client";

import React, { useState, useEffect, useMemo } from "react";
import dynamic from "next/dynamic";
import { FHIRBundle, FHIRHumanName, FHIRAddress, FHIRPatient } from "@/types/fhir";
import { PatientDisplayData, PatientTableProps } from "@/types";
import { extractQueryUrl, processPatients } from "@/lib/fhir-utils";

// Dynamic import to avoid SSR issues with Recharts (which relies on browser APIs)
const PatientCharts = dynamic(() => import("./PatientCharts"), { ssr: false });

export default function PatientTable({ fhirQuery }: PatientTableProps) {
  const [patients, setPatients] = useState<PatientDisplayData[]>([]);
  const [recordCount, setRecordCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const patientsPerPage = 10;

  // Filter states
  const [ageRange, setAgeRange] = useState({ min: "", max: "" });
  const [genderFilter, setGenderFilter] = useState("All");
  const [countryFilter, setCountryFilter] = useState("All");
  const [aliveFilter, setAliveFilter] = useState("All");

  // Memoized lists for filter dropdowns
  const availableCountries = useMemo(() => {
    const countries = new Set(patients.map(p => p.country).filter(c => c && c !== "-"));
    return ["All", ...Array.from(countries).sort()];
  }, [patients]);

  // Helper function to calculate age from birth date
  const calculateAge = (birthDate: string): number => {
    if (!birthDate) return 0;
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    
    return age;
  };

  // Helper function to extract patient name
  const extractPatientName = (names?: FHIRHumanName[]): string => {
    if (!names || names.length === 0) return "-";
    const officialName = names.find(name => name.use === "official") || names[0];
    if (officialName.text) return officialName.text;
    const parts = [
        ...(officialName.prefix || []),
        ...(officialName.given || []),
        officialName.family || '',
    ];
    return parts.join(" ") || "-";
  };

  // Helper function to extract address state
  const extractState = (addresses?: FHIRAddress[]): string => {
    if (!addresses || addresses.length === 0) return "-";
    const homeAddress = addresses.find(addr => addr.use === "home") || addresses[0];
    return homeAddress.state || "-";
  };

  // Helper function to extract address country
  const extractCountry = (addresses?: FHIRAddress[]): string => {
    if (!addresses || addresses.length === 0) return "-";
    const homeAddress = addresses.find(addr => addr.use === "home") || addresses[0];
    return homeAddress.country || "-";
  };

  // Helper function to determine if patient is alive
  const isPatientAlive = (patient: FHIRPatient): string => {
    if (patient.deceasedBoolean === true || patient.deceasedDateTime) return "No";
    if (patient.deceasedBoolean === false) return "Yes";
    return "-"; // Unknown/not specified
  };

  // Memoized filtered patients
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

  // Fetch data from FHIR server
  const fetchPatientData = async (url: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // Append _count=500 to limit fetched records
      // Check if URL already has query parameters
      const separator = url.includes('?') ? '&' : '?';
      const fetchUrl = `${url}${separator}_count=500`;
      console.log("Fetching FHIR data from:", fetchUrl);
      
      const response = await fetch(fetchUrl, {
        headers: {
          'Accept': 'application/fhir+json',
          'Content-Type': 'application/fhir+json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: FHIRBundle = await response.json();
      console.log("FHIR Response:", data);

      if (data.resourceType !== "Bundle") {
        throw new Error(`Expected Bundle, got ${data.resourceType}`);
      }

      const fhirPatients = data.entry?.filter(e => e.resource?.resourceType === 'Patient').map(e => e.resource as FHIRPatient) || [];

      // Process patients (age validation will be handled in processPatients)
      const processed = processPatients(fhirPatients);
      setPatients(processed);
      // Use actual number of processed patients instead of data.total to fix display issue
      setRecordCount(processed.length);
      setCurrentPage(1);

    } catch (err) {
      console.error("Error fetching FHIR data:", err);
      setError(err instanceof Error ? err.message : "An unknown error occurred");
      setPatients([]);
      setRecordCount(0);
    } finally {
      setLoading(false);
    }
  };

  // Effect to fetch data when fhirQuery changes
  useEffect(() => {
    if (!fhirQuery || !fhirQuery.trim()) return;
    const url = extractQueryUrl(fhirQuery);
    if (!url) {
        setError("Invalid FHIR query format");
        return;
    }
    fetchPatientData(url);
  }, [fhirQuery]);

  // Don't render anything if no query
  if (!fhirQuery || !fhirQuery.trim()) {
    return null;
  }
  
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
            {!loading && !error && (
              <p className="text-sm text-gray-600">
                {`Total Records: ${recordCount}`}
              </p>
            )}
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

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center p-12">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Fetching patient data...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="p-6">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">
                    Error fetching patient data
                  </h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>{error}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Table */}
        {!loading && !error && paginatedPatients.length > 0 && (
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
        {!loading && !error && filteredPatients.length === 0 && (
          <div className="p-12 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No patient data found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {patients.length > 0 ? "No patients match the current filter criteria." : "The FHIR query returned no matching patients."}
            </p>
          </div>
        )}
        
        {/* Pagination */}
        {!loading && !error && totalPages > 1 && (
          <div className="flex items-center justify-between my-4 px-6">
            <span className="text-sm text-gray-600">
              Page {currentPage} of {totalPages}
            </span>
            <div className="flex items-center space-x-2">
              <button
                className={`px-3 py-1 rounded-md border text-sm ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100'}`}
                onClick={() => currentPage > 1 && setCurrentPage(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Prev
              </button>
             
              <button
                className={`px-3 py-1 rounded-md border text-sm ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100'}`}
                onClick={() => currentPage < totalPages && setCurrentPage(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Charts */}
        {!loading && !error && filteredPatients.length > 0 && (
          <PatientCharts patients={filteredPatients} />
        )}
      </div>
    </div>
  );
} 