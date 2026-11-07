export function calcLLPA(creditScore: number, ltv: number): number {
  let adj = 0;

  if (creditScore < 660) adj += 0.5;
  else if (creditScore < 700) adj += 0.25;

  if (ltv > 0.8) adj += 0.25;

  return adj;
}
