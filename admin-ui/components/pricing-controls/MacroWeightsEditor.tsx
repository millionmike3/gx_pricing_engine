import { useState } from "react";
import Input from "../UI/Input";
import Button from "../UI/Button";

interface MacroWeight {
  factor: string;
  weight: number;
}

export default function MacroWeightsEditor({
  weights,
}: {
  weights: MacroWeight[];
}) {
  const [localWeights, setLocalWeights] = useState(weights);

  const updateWeight = (index: number, value: number) => {
    const updated = [...localWeights];
    updated[index].weight = value;
    setLocalWeights(updated);
  };

  return (
    <div>
      {localWeights.map((w, i) => (
        <Input
          key={i}
          label={w.factor}
          value={w.weight}
          onChange={(v) => updateWeight(i, Number(v))}
        />
      ))}

      <Button onClick={() => console.log(localWeights)}>Save</Button>
    </div>
  );
}
