// Processed patient data for display in the table and charts
export interface PatientDisplayData {
  id: string;
  name: string;
  gender: string;
  age: string;
  state: string;
  country: string;
  isAlive: string;
}

// Props for PatientTable component
export interface PatientTableProps {
  fhirQuery: string;
}

// Props for PatientCharts component
export interface PatientChartsProps {
  patients: PatientDisplayData[];
}

// API response type for the backend query
export interface FHIRQueryResponse {
  condition_query?: string;
  patient_query: string;
  success: boolean;
  error?: string;
} 