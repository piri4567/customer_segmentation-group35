export default function KPICard({ label, value, sub, accent }) {
  return (
    <div className="card p-5">
      <div className="stat-label">{label}</div>
      <div className="mt-2 flex items-baseline gap-2">
        <span
          className="stat-num"
          style={accent ? { color: accent } : undefined}
        >
          {value}
        </span>
      </div>
      {sub && <div className="mt-1 text-sm text-slate-500">{sub}</div>}
    </div>
  );
}
