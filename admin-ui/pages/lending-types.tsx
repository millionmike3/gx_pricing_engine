import LendingTypeTable from "../components/pricing-controls/LendingTypeTable";

const lendingTypes = [
  { type: "Conventional", description: "Standard conforming and agency mortgage loans" },
  { type: "FHA", description: "Government-insured mortgage loans" },
  { type: "VA", description: "Veteran and eligible service-member mortgage loans" },
  { type: "Non-QM", description: "Non-qualified mortgage products; product pricing adjustment configured in the engine" },
  { type: "Hard Money", description: "Short-term, asset-based real estate financing; pricing configuration pending" },
];

export default function LendingTypes() {
  return <LendingTypeTable types={lendingTypes} />;
}
