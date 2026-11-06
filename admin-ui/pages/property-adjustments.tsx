import PropertyAdjustmentsTable from "../components/pricing-controls/PropertyAdjustmentsTable";

const mockAdjustments = [
  { property_type: "Single Family", adjustment_bps: 0 },
  { property_type: "Condo", adjustment_bps: 25 },
  { property_type: "Multi‑Family", adjustment_bps: 40 },
];

export default function PropertyAdjustments() {
  return <PropertyAdjustmentsTable adjustments={mockAdjustments} />;
}
