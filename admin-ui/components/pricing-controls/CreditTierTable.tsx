import Table from "../UI/Table";

interface CreditTier {
  tier: string;
  minScore: number;
  maxScore: number;
}

export default function CreditTierTable({ tiers }: { tiers: CreditTier[] }) {
  const columns = ["tier", "minScore", "maxScore"];

  return <Table columns={columns} data={tiers} />;
}
