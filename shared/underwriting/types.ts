export type UnderwritingInput = {
  creditScore: number;
  dti: number;
  ltv: number;
  income: number;
  loanAmount: number;
};

export type UnderwritingDecision = {
  approved: boolean;
  reasons: string[];
};
