import MarginProfileEditor from "../components/pricing-controls/MarginProfileEditor";

const mockProfiles = [
  { name: "Prime", margin_bps: 75 },
  { name: "Non‑QM", margin_bps: 150 },
  { name: "Jumbo", margin_bps: 90 },
];

export default function MarginProfiles() {
  return <MarginProfileEditor profiles={mockProfiles} />;
}
