import Table from "../UI/Table";

interface PropertyAdjustment {
  property_type: string;
  adjustment_bps: number;
}

export default function PropertyAdjustmentsTable({
  adjustments,
}: {
  adjustments: PropertyAdjustment[];
}) {
  const columns = ["property_type", "adjustment_bps"];

  return <Table columns={columns} data={adjustments} />;
}
