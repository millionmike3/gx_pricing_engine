export type EligibilityInput = {
  age: number;
  residencyStatus: "citizen" | "permanent_resident" | "non_resident";
  employmentMonths: number;
  creditScore: number;
};

export type EligibilityResult = {
  eligible: boolean;
  reasons: string[];
};
