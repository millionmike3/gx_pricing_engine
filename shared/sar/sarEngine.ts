import { SarRules } from "./sarRules";

export function runSarCheck(data: any) {
  const triggered = SarRules.filter(rule => rule.check(data));
  return {
    suspicious: triggered.length > 0,
    triggered,
  };
}
