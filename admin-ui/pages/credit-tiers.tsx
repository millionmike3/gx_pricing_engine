import CreditTierTable from "../components/pricing-controls/CreditTierTable";

const mockTiers = [
  { tier: "A", minScore: 760, maxScore: 850 },
  { tier: "B", minScore: 700, maxScore: 759 },
  { tier: "C", minScore: 640, maxScore: 699 },
];

export default function CreditTiers() {
  return <CreditTierTable tiers={mockTiers} />;
}
