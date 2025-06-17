import { FHIRPatient, FHIRHumanName, FHIRAddress } from "@/types/fhir";
import { PatientDisplayData } from "@/types";

// Helper function to extract the URL from FHIR query
export const extractQueryUrl = (fhirQuery: string): string | null => {
  const match = fhirQuery.match(/GET\s+(.+)$/);
  return match ? match[1] : null;
};

// Helper function to calculate age from birth date
export const calculateAge = (birthDate: string): number => {
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
export const extractPatientName = (names?: FHIRHumanName[]): string => {
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
export const extractState = (addresses?: FHIRAddress[]): string => {
  if (!addresses || addresses.length === 0) return "-";
  const homeAddress = addresses.find(addr => addr.use === "home") || addresses[0];
  return homeAddress.state || "-";
};

// Helper function to extract address country
export const extractCountry = (addresses?: FHIRAddress[]): string => {
  if (!addresses || addresses.length === 0) return "-";
  const homeAddress = addresses.find(addr => addr.use === "home") || addresses[0];
  return homeAddress.country || "-";
};

// Helper function to determine if patient is alive
export const isPatientAlive = (patient: FHIRPatient): string => {
  if (patient.deceasedBoolean === true || patient.deceasedDateTime) return "No";
  if (patient.deceasedBoolean === false) return "Yes";
  return "-"; // Unknown/not specified
};

// Process FHIR patients into display format
export const processPatients = (fhirPatients: FHIRPatient[]): PatientDisplayData[] => {
  return fhirPatients.map(patient => {
    let ageDisplay = "-";
    if (patient.birthDate) {
      const calculatedAge = calculateAge(patient.birthDate);
      // Only show realistic ages (1-100), otherwise show "-"
      if (calculatedAge > 0 && calculatedAge <= 100) {
        ageDisplay = calculatedAge.toString();
      }
    }
    
    return {
      id: patient.id || "-",
      name: extractPatientName(patient.name),
      gender: patient.gender ? patient.gender.charAt(0).toUpperCase() + patient.gender.slice(1) : "-",
      age: ageDisplay,
      state: extractState(patient.address),
      country: extractCountry(patient.address),
      isAlive: isPatientAlive(patient)
    };
  });
}; 