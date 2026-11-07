import { UnderwritingInput, UnderwritingDecision } from "./types";
import { UnderwritingRules } from "./rules";

export function runUnderwriting(input: UnderwritingInput): UnderwritingDecision {
  const failed = UnderwritingRules.filter(rule => !rule.check(input));

  return {
    approved: failed.length === 0,
    reasons: failed.map(f => f.failReason),
  };
}
