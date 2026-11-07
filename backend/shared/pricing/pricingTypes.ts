export type PricingInput = {
  loanAmount: number;
  creditScore: number;
  ltv: number;
  dti: number;
  productType: "fixed" | "arm";
  termMonths: number;
};

export type PricingScenario = {
  label: string;
  baseRate: number;
  llpaAdj: number;
  finalRate: number;
  apr: number;
};

export type PricingResult = {
  scenarios: PricingScenario[];
};
