export type RiskInput = {
  creditScore: number;
  dti: number;
  ltv: number;
  fraudFlags: number;
  sarFlags: number;
};

export type RiskScoreResult = {
  score: number; // 0–100
  band: "low" | "medium" | "high";
};
