import { useState } from "react";
import Input from "../UI/Input";
import Button from "../UI/Button";

interface MarginProfile {
  name: string;
  margin_bps: number;
}

export default function MarginProfileEditor({
  profiles,
}: {
  profiles: MarginProfile[];
}) {
  const [localProfiles, setLocalProfiles] = useState(profiles);

  const updateProfile = (index: number, value: number) => {
    const updated = [...localProfiles];
    updated[index].margin_bps = value;
    setLocalProfiles(updated);
  };

  return (
    <div>
      {localProfiles.map((p, i) => (
        <Input
          key={i}
          label={p.name}
          value={p.margin_bps}
          onChange={(v) => updateProfile(i, Number(v))}
        />
      ))}

      <Button onClick={() => console.log(localProfiles)}>Save</Button>
    </div>
  );
}
