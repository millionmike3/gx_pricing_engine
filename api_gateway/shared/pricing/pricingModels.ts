import { PricingInput } from "./pricingTypes";
import { calcAPR, calcLLPA } from "../mortgage/math";

export function baseRateModel(input: PricingInput): number {
  let rate = 6.0;

  if (input.creditScore > 740) rate -= 0.25;
  if (input.creditScore < 660) rate += 0.5;

  if (input.ltv > 0.8) rate += 0.25;
  if (input.dti > 0.45) rate += 0.25;

  return rate;
}

export function buildScenario(label: string, input: PricingInput): any {
  const baseRate = baseRateModel(input);
  const llpaAdj = calcLLPA(input.creditScore, input.ltv);
  const finalRate = baseRate + llpaAdj;
  const apr = calcAPR(finalRate, input.termMonths, input.loanAmount);

  return {
    label,
    baseRate,
    llpaAdj,
    finalRate,
    apr,
  };
}
