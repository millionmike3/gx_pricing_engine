import MacroWeightsEditor from "../components/pricing-controls/MacroWeightsEditor";

const mockWeights = [
  { factor: "Inflation", weight: 0.35 },
  { factor: "GDP Growth", weight: 0.25 },
  { factor: "Unemployment", weight: 0.40 },
];

export default function MacroWeights() {
  return <MacroWeightsEditor weights={mockWeights} />;
}
