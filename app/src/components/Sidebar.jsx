import { SEGMENTS } from "../data/segments";

const NAV_ITEMS = [
  { id: "overview", label: "Overview", icon: "▦" },
  { id: "segments", label: "Segments", icon: "◇" },
  { id: "methodology", label: "Methodology", icon: "◐" },
  { id: "visuals", label: "Visualisations", icon: "▤" },
  { id: "campaigns", label: "Campaigns", icon: "✦" },
];

export default function Sidebar({ active, onChange }) {
  return (
    <aside className="w-64 shrink-0 bg-navy text-white flex flex-col h-screen sticky top-0">
      {/* Header */}
      <div className="px-6 py-6 border-b border-white/10">
        <div className="text-xs uppercase tracking-widest text-slate-400 font-semibold">
          NOVA IMS · ML II
        </div>
        <div className="mt-1 text-lg font-bold leading-tight">
          Customer<br />Segmentation
        </div>
        <div className="mt-3 text-xs text-slate-400">Group 35 · 2026</div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const isActive = active === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onChange(item.id)}
              className={[
                "w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-3",
                isActive
                  ? "bg-white/10 text-white"
                  : "text-slate-300 hover:bg-white/5 hover:text-white",
              ].join(" ")}
            >
              <span className="text-base opacity-70">{item.icon}</span>
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Segment legend */}
      <div className="px-4 py-4 border-t border-white/10 text-xs">
        <div className="text-slate-400 uppercase tracking-wider mb-2 font-semibold">
          Segments
        </div>
        <ul className="space-y-1.5">
          {SEGMENTS.map((s) => (
            <li key={s.id} className="flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 rounded-full shrink-0"
                style={{ backgroundColor: s.color }}
              />
              <span className="text-slate-300 truncate">{s.short}</span>
              <span className="ml-auto text-slate-500 font-mono">
                {s.pct}%
              </span>
            </li>
          ))}
        </ul>
      </div>

      <div className="px-6 py-3 border-t border-white/10 text-[10px] text-slate-500">
        K-Means · 33 038 customers
      </div>
    </aside>
  );
}
