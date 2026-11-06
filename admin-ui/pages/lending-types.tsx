import LendingTypeTable from "../components/pricing-controls/LendingTypeTable";

const mockTypes = [
  { type: "Conventional", description: "Standard agency loan" },
  { type: "FHA", description: "Government insured loan" },
  { type: "VA", description: "Veteran loan program" },
];

export default function LendingTypes() {
  return <LendingTypeTable types={mockTypes} />;
}
