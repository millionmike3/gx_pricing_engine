import Table from "../UI/Table";

interface LendingType {
  type: string;
  description: string;
}

export default function LendingTypeTable({ types }: { types: LendingType[] }) {
  const columns = ["type", "description"];

  return <Table columns={columns} data={types} />;
}
