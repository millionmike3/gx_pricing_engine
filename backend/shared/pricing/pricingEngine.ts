import { PricingInput, PricingResult } from "./pricingTypes";
import { buildScenario } from "./pricingModels";

export function runPricingEngine(input: PricingInput): PricingResult {
  const scenarios = [
    buildScenario("Base", input),
    buildScenario("Buydown", { ...input, loanAmount: input.loanAmount * 0.99 }),
    buildScenario("High LTV", { ...input, ltv: Math.min(1.0, input.ltv + 0.05) }),
  ];

  return { scenarios };
}
