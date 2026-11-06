export default function ComparisonTable({ data }: any) {
  return (
    <table className="w-full border mt-4">
      <thead>
        <tr className="bg-gray-100">
          <th className="p-2 border">Scenario</th>
          <th className="p-2 border">Rate</th>
          <th className="p-2 border">APR</th>
        </tr>
      </thead>
      <tbody>
        {data?.scenarios?.map((s: any, idx: number) => (
          <tr key={idx}>
            <td className="p-2 border">{s.label}</td>
            <td className="p-2 border">{s.rate}</td>
            <td className="p-2 border">{s.apr}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
