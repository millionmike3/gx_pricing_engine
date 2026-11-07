import { RiskInput } from "./types";

export function baseRisk(input: RiskInput): number {
  let score = 50;

  if (input.creditScore > 740) score -= 15;
  else if (input.creditScore < 660) score += 15;

  if (input.dti > 0.45) score += 10;
  if (input.ltv > 0.9) score += 10;

  score += input.fraudFlags * 10;
  score += input.sarFlags * 15;

  return Math.max(0, Math.min(100, score));
}

export function riskBand(score: number): "low" | "medium" | "high" {
  if (score < 40) return "low";
  if (score < 70) return "medium";
  return "high";
}
