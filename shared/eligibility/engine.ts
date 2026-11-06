import { EligibilityInput } from "./types";

export const EligibilityRules = [
  {
    id: "MIN_AGE",
    description: "Borrower must be at least 18",
    check: (data: EligibilityInput) => data.age >= 18,
    failReason: "Borrower is under 18",
  },
  {
    id: "EMPLOYMENT_HISTORY",
    description: "At least 12 months of employment",
    check: (data: EligibilityInput) => data.employmentMonths >= 12,
    failReason: "Insufficient employment history",
  },
  {
    id: "MIN_CREDIT_SCORE",
    description: "Credit score must be at least 580",
    check: (data: EligibilityInput) => data.creditScore >= 580,
    failReason: "Credit score below 580",
  },
];
