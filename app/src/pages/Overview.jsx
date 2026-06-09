import { SEGMENTS } from "../data/segments";
import KPICard from "../components/KPICard";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

export default function Overview() {
  const totalCustomers = SEGMENTS.reduce((s, x) => s + x.customers, 0);
  const totalRevenue = SEGMENTS.reduce(
    (s, x) => s + x.customers * x.avgSpend,
    0
  );
  const avgSpend = Math.round(totalRevenue / totalCustomers);

  // High-value families revenue share
  const highValue = SEGMENTS.find((s) => s.name === "High-Value Families");
  const highValueRev = highValue.customers * highValue.avgSpend;
  const highValueRevPct = ((highValueRev / totalRevenue) * 100).toFixed(0);

  const pieData = SEGMENTS.map((s) => ({
    name: s.short,
    value: s.customers,
    color: s.color,
  }));

  const revenueData = SEGMENTS.map((s) => ({
    name: s.short,
    revenue: Math.round((s.customers * s.avgSpend) / 1_000_000),
    color: s.color,
  })).sort((a, b) => b.revenue - a.revenue);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Executive Overview</h1>
        <p className="mt-1 text-slate-600">
          K-Means segmentation of {totalCustomers.toLocaleString()} retail
          customers into 5 actionable groups. Each segment has a distinct
          behavioural profile and a tailored campaign set.
        </p>
      </header>

      {/* KPI row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Customers"
          value={totalCustomers.toLocaleString()}
          sub="From customer_info dataset"
        />
        <KPICard
          label="Total lifetime revenue"
          value={`€${(totalRevenue / 1_000_000).toFixed(0)}M`}
          sub="Sum of avg spend × segment size"
        />
        <KPICard
          label="Avg lifetime spend"
          value={`€${avgSpend.toLocaleString()}`}
          sub="Portfolio mean"
        />
        <KPICard
          label="Segments identified"
          value="5"
          sub="K=5 via elbow + silhouette"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card p-5">
          <h3 className="section-title">Customers per segment</h3>
          <div style={{ width: "100%", height: 280 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={95}
                  label={(entry) =>
                    `${entry.name} ${(
                      (entry.value / totalCustomers) *
                      100
                    ).toFixed(1)}%`
                  }
                  labelLine={false}
                >
                  {pieData.map((d, i) => (
                    <Cell key={i} fill={d.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(v) => v.toLocaleString()}
                  contentStyle={{ borderRadius: 8, fontSize: 12 }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-5">
          <h3 className="section-title">Estimated revenue by segment (€M)</h3>
          <div style={{ width: "100%", height: 280 }}>
            <ResponsiveContainer>
              <BarChart
                data={revenueData}
                layout="vertical"
                margin={{ left: 10, right: 30 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" stroke="#64748b" fontSize={11} />
                <YAxis
                  type="category"
                  dataKey="name"
                  stroke="#64748b"
                  fontSize={12}
                  width={80}
                />
                <Tooltip
                  formatter={(v) => `€${v}M`}
                  contentStyle={{ borderRadius: 8, fontSize: 12 }}
                />
                <Bar dataKey="revenue" radius={[0, 6, 6, 0]}>
                  {revenueData.map((d, i) => (
                    <Cell key={i} fill={d.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Strategic highlights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card p-5">
          <h3 className="section-title">Key findings</h3>
          <ul className="space-y-3 text-sm text-slate-700 leading-relaxed">
            <li className="flex gap-3">
              <span className="text-xl leading-none text-seg-family">●</span>
              <span>
                <strong>High-Value Families</strong> ({highValue.pct}% of
                customers) generate an estimated{" "}
                <strong>{highValueRevPct}% of total lifetime revenue</strong> —
                their average spend is 2.5× the portfolio mean. Highest-priority
                retention target.
              </span>
            </li>
            <li className="flex gap-3">
              <span className="text-xl leading-none text-seg-core">●</span>
              <span>
                <strong>Core Everyday Shoppers</strong> are the largest segment
                at 41% and represent the largest absolute revenue pool. A 10%
                basket-size increase here is the highest-impact lever available.
              </span>
            </li>
            <li className="flex gap-3">
              <span className="text-xl leading-none text-seg-budget">●</span>
              <span>
                <strong>Budget-Conscious Shoppers</strong> visit the most
                distinct stores — active cross-shopping. A structured loyalty
                programme can consolidate spend currently spread across
                competitors.
              </span>
            </li>
            <li className="flex gap-3">
              <span className="text-xl leading-none text-seg-tech">●</span>
              <span>
                <strong>Tech-Savvy Singles</strong> and{" "}
                <strong>Pet and Home Essentials</strong> have clearly defined
                category affinities directly addressable through targeted
                promotions derived from basket association rules.
              </span>
            </li>
          </ul>
        </div>

        <div className="card p-5">
          <h3 className="section-title">Strategic priorities</h3>
          <ol className="space-y-3 text-sm text-slate-700 leading-relaxed list-decimal pl-4 marker:font-bold marker:text-slate-400">
            <li>
              <strong>Protect High-Value Families.</strong> VIP loyalty tier
              with exclusive cashback and family milestone rewards.
            </li>
            <li>
              <strong>Grow the Core Everyday Base.</strong> Cross-category
              promotions anchored in grocery and fresh produce.
            </li>
            <li>
              <strong>Consolidate Budget-Conscious Shoppers.</strong> Mid-week
              double-points days and household bundles.
            </li>
            <li>
              <strong>Convert Pet Segment to Subscriptions.</strong>{" "}
              Predictable, high-frequency purchases are a natural
              subscribe-and-save opportunity.
            </li>
            <li>
              <strong>Anchor Tech-Savvy Singles with tiered loyalty.</strong>{" "}
              Bronze / Silver / Gold tiers tied to tech spend, with early
              access and progressive discounts.
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
}
