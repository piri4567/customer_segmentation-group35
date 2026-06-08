import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";
import { useClusterSummary } from "../../utils/useClusterSummary";

export default function PromoSensitivity() {
  const { rows, loading } = useClusterSummary();
  if (loading) {
    return (
      <div className="h-64 flex items-center justify-center text-sm text-slate-400">
        Loading data…
      </div>
    );
  }

  const data = rows
    .map((r) => ({
      name: r.short,
      promo: +(r.percentage_of_products_bought_promotion * 100).toFixed(1),
      color: r.color,
    }))
    .sort((a, b) => b.promo - a.promo);

  return (
    <div style={{ width: "100%", height: 280 }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
          <YAxis
            stroke="#64748b"
            fontSize={11}
            tickFormatter={(v) => `${v}%`}
          />
          <Tooltip
            contentStyle={{ borderRadius: 8, fontSize: 12 }}
            formatter={(v) => `${v}%`}
          />
          <Bar dataKey="promo" radius={[6, 6, 0, 0]}>
            {data.map((d, i) => (
              <Cell key={i} fill={d.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
