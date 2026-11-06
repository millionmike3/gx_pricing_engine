export const FraudRules = [
  {
    id: "LOW_CREDIT_SCORE",
    description: "Credit score below 580",
    check: (data: any) => data.creditScore < 580,
  },
  {
    id: "HIGH_DTI",
    description: "Debt-to-income ratio above 50%",
    check: (data: any) => data.dti > 0.5,
  },
];
