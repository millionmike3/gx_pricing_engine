export const SarRules = [
  {
    id: "LARGE_JUMP_IN_INCOME",
    description: "Income increased more than 200% in 30 days",
    check: (data: any) => data.incomeJump > 2.0,
  },
  {
    id: "UNVERIFIED_DOCUMENTS",
    description: "Borrower submitted unverifiable documents",
    check: (data: any) => data.unverifiedDocs === true,
  },
];
