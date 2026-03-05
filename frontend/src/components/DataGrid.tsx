export default function DataGrid({ data }: { data: any[] }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-gray-500">
        <div className="text-center">
          <div className="mb-2 text-6xl opacity-20">📊</div>
          <p>Select a table to view data</p>
        </div>
      </div>
    );
  }

  const columns = Object.keys(data[0]);

  return (
    <div className="h-full w-full overflow-auto bg-[#1e1e1e]">
      <table className="w-full text-left text-sm text-gray-300">
        <thead className="sticky top-0 bg-[#252526] text-xs uppercase font-bold text-gray-400">
          <tr>
            {columns.map(col => (
              <th key={col} className="border-b border-r border-[#333] px-4 py-2 font-mono whitespace-nowrap">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="font-mono text-xs">
          {data.map((row, i) => (
            <tr key={i} className="hover:bg-[#2a2d2e]">
              {columns.map(col => (
                <td key={col} className="border-b border-r border-[#333] px-4 py-1 whitespace-nowrap overflow-hidden text-ellipsis max-w-[200px]">
                  {row[col]?.toString() || <span className="text-gray-600">null</span>}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}