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

// API response from the backend, now including the query string
export interface APIResponse {
  fhir_query: string;
  data: PatientDisplayData[] | "UNSUPPORTED_CONDITION";
  success: boolean;
  error?: string;
} 