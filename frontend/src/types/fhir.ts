// Types for FHIR resources
export interface FHIRIdentifier {
  system?: string;
  value?: string;
}

export interface FHIRHumanName {
  use?: string;
  text?: string;
  family?: string;
  given?: string[];
  prefix?: string[];
}

export interface FHIRAddress {
  use?: string;
  text?: string;
  line?: string[];
  city?: string;
  district?: string;
  state?: string;
  postalCode?: string;
  country?: string;
}

export interface FHIRPatient {
  resourceType: "Patient";
  id: string;
  identifier?: FHIRIdentifier[];
  name?: FHIRHumanName[];
  gender?: "male" | "female" | "other" | "unknown";
  birthDate?: string;
  address?: FHIRAddress[];
  deceasedBoolean?: boolean;
  deceasedDateTime?: string;
}

export interface FHIRBundleEntry {
  fullUrl?: string;
  resource: FHIRPatient;
  search?: {
    mode: string;
  };
}

export interface FHIRBundle {
  resourceType: "Bundle";
  id: string;
  type: "searchset";
  total?: number;
  entry?: FHIRBundleEntry[];
  link?: Array<{
    relation: string;
    url: string;
  }>;
} 