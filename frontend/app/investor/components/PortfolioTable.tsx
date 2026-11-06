export default function PortfolioTable() {
  return (
    <table className="w-full border mt-4">
      <thead>
        <tr className="bg-gray-100">
          <th className="p-2 border">Asset</th>
          <th className="p-2 border">Yield</th>
          <th className="p-2 border">Risk</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td className="p-2 border">Mortgage Pool A</td>
          <td className="p-2 border">5.2%</td>
          <td className="p-2 border">Low</td>
        </tr>
      </tbody>
    </table>
  );
}
