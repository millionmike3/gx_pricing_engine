export function calcDTI(monthlyDebt: number, monthlyIncome: number): number {
  if (!monthlyIncome) return 0;
  return monthlyDebt / monthlyIncome;
}

export function calcLTV(loanAmount: number, propertyValue: number): number {
  if (!propertyValue) return 0;
  return loanAmount / propertyValue;
}

export function calcAPR(rate: number, termMonths: number, loanAmount: number): number {
  // Simple placeholder APR model
  const fees = loanAmount * 0.01;
  const annualRate = rate / 100;
  return (annualRate + fees / loanAmount) * 100;
}

export function calcMI(ltv: number): number {
  if (ltv < 0.8) return 0;
  if (ltv < 0.9) return 0.5;
  return 0.8;
}
