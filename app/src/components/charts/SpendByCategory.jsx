import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { useClusterSummary } from "../../utils/useClusterSummary";

const SPEND_COLS = [
  { key: "lifetime_spend_groceries", label: "Groceries" },
  { key: "lifetime_spend_electronics", label: "Electronics" },
  { key: "lifetime_spend_meat", label: "Meat" },
  { key: "lifetime_spend_fish", label: "Fish" },
  { key: "lifetime_spend_videogames", label: "Video Games" },
  { key: "lifetime_spend_petfood", label: "Pet Food" },
  { key: "lifetime_spend_alcohol_drinks", label: "Alcohol" },
];

export default function SpendByCategory() {
  const { rows, loading } = useClusterSummary();
  if (loading) return <ChartSkeleton />;

  // Transform: rows = categories, each segment is a series
  const data = SPEND_COLS.map((c) => {
    const point = { category: c.label };
    rows.forEach((r) => {
      point[r.short] = Math.round(r[c.key]);
    });
    return point;
  });

  return (
    <div style={{ width: "100%", height: 380 }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 30 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis
            dataKey="category"
            stroke="#64748b"
            fontSize={11}
            angle={-20}
            textAnchor="end"
            height={50}
          />
          <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `€${(v / 1000).toFixed(0)}k`} />
          <Tooltip
            contentStyle={{ borderRadius: 8, fontSize: 12 }}
            formatter={(v) => `€${v.toLocaleString()}`}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {rows.map((r) => (
            <Bar key={r.short} dataKey={r.short} fill={r.color} radius={[4, 4, 0, 0]} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function ChartSkeleton() {
  return (
    <div className="h-64 flex items-center justify-center text-sm text-slate-400">
      Loading data…
    </div>
  );
}
