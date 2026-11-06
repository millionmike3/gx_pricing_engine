import { UnderwritingInput } from "./types";

export const UnderwritingRules = [
  {
    id: "MIN_CREDIT_SCORE",
    description: "Credit score must be at least 620",
    check: (data: UnderwritingInput) => data.creditScore >= 620,
    failReason: "Credit score below 620",
  },
  {
    id: "MAX_DTI",
    description: "DTI must be <= 50%",
    check: (data: UnderwritingInput) => data.dti <= 0.5,
    failReason: "Debt-to-income ratio above 50%",
  },
  {
    id: "MAX_LTV",
    description: "LTV must be <= 97%",
    check: (data: UnderwritingInput) => data.ltv <= 0.97,
    failReason: "Loan-to-value above 97%",
  },
];
