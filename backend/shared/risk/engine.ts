import { RiskInput, RiskScoreResult } from "./types";
import { baseRisk, riskBand } from "./factors";

export function runRiskScoring(input: RiskInput): RiskScoreResult {
  const score = baseRisk(input);
  const band = riskBand(score);

  return { score, band };
}
