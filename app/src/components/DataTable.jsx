export default function DataTable({ columns, rows, dense = false }) {
  const padding = dense ? "px-3 py-1.5" : "px-4 py-2.5";
  return (
    <div className="overflow-x-auto card">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-slate-700 border-b border-slate-200">
          <tr>
            {columns.map((c) => (
              <th
                key={c.key}
                className={`${padding} text-left font-semibold whitespace-nowrap`}
              >
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={i}
              className="border-b border-slate-100 last:border-0 hover:bg-slate-50/50"
            >
              {columns.map((c) => (
                <td
                  key={c.key}
                  className={`${padding} text-slate-700 whitespace-nowrap`}
                >
                  {c.render ? c.render(row[c.key], row) : row[c.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
