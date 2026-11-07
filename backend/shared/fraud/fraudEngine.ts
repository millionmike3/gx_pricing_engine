import { FraudRules } from "./fraudRules";

export function runFraudCheck(data: any) {
  const triggered = FraudRules.filter(rule => rule.check(data));
  return {
    passed: triggered.length === 0,
    triggered,
  };
}
