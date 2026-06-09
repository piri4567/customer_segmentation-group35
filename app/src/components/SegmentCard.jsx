export default function SegmentCard({ segment, onClick, active }) {
  return (
    <button
      onClick={onClick}
      className={[
        "card text-left p-5 w-full transition-all",
        "hover:shadow-md hover:-translate-y-0.5",
        active ? "ring-2 ring-offset-2" : "",
      ].join(" ")}
      style={active ? { ringColor: segment.color } : undefined}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: segment.color }}
            />
            <div className="text-xs uppercase tracking-wider text-slate-500 font-semibold">
              {segment.short}
            </div>
          </div>
          <div className="mt-1 font-bold text-slate-900 text-lg leading-snug">
            {segment.name}
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-500">share</div>
          <div className="font-bold text-slate-900">{segment.pct}%</div>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <div className="text-xs text-slate-500">Customers</div>
          <div className="font-semibold text-slate-900 mt-0.5">
            {segment.customers.toLocaleString()}
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-500">Avg spend</div>
          <div className="font-semibold text-slate-900 mt-0.5">
            €{segment.avgSpend.toLocaleString()}
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-500">Avg children</div>
          <div className="font-semibold text-slate-900 mt-0.5">
            {segment.avgChildren}
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-500">Tenure</div>
          <div className="font-semibold text-slate-900 mt-0.5">
            {segment.avgTenure}y
          </div>
        </div>
      </div>
    </button>
  );
}
