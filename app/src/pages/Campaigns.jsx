import { useEffect, useState } from "react";
import { SEGMENTS, SEGMENT_BY_ID } from "../data/segments";
import CampaignCarousel from "../components/CampaignCarousel";
import DataTable from "../components/DataTable";
import { loadCSV } from "../utils/csv";

export default function Campaigns() {
  const [activeId, setActiveId] = useState(SEGMENTS[0].id);
  const [rules, setRules] = useState([]);
  const active = SEGMENT_BY_ID[activeId];

  useEffect(() => {
    loadCSV(`/data/rules_cluster_${activeId}.csv`)
      .then((rows) =>
        setRules(
          rows.slice(0, 8).map((r) => ({
            antecedents: r.antecedents_str,
            consequents: r.consequents_str,
            support: typeof r.support === "number" ? r.support.toFixed(3) : r.support,
            confidence:
              typeof r.confidence === "number" ? r.confidence.toFixed(2) : r.confidence,
            lift: typeof r.lift === "number" ? r.lift.toFixed(2) : r.lift,
          }))
        )
      )
      .catch(() => setRules([]));
  }, [activeId]);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">
          Campaigns &amp; Association Rules
        </h1>
        <p className="mt-1 text-slate-600">
          Each segment has four campaigns grounded in real-world retail
          practice and tied to that cluster's basket association rules (mined
          via Apriori, per-cluster).
        </p>
      </header>

      {/* Segment switcher */}
      <div className="flex flex-wrap gap-2">
        {SEGMENTS.map((s) => {
          const isActive = s.id === activeId;
          return (
            <button
              key={s.id}
              onClick={() => setActiveId(s.id)}
              className={[
                "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                isActive
                  ? "text-white shadow"
                  : "bg-white text-slate-700 border border-slate-200 hover:border-slate-300",
              ].join(" ")}
              style={isActive ? { backgroundColor: s.color } : undefined}
            >
              {s.short}
            </button>
          );
        })}
      </div>

      {/* Hero carousel */}
      <div>
        <h2 className="section-title">Featured creatives</h2>
        <CampaignCarousel segment={active} />
      </div>

      {/* Rules */}
      <div>
        <h2 className="section-title">
          Top association rules for cluster {activeId} ·{" "}
          <span className="font-normal text-slate-500">
            {rules.length} of top-N
          </span>
        </h2>
        {rules.length > 0 ? (
          <DataTable
            dense
            columns={[
              { key: "antecedents", label: "Antecedents (if customer buys…)" },
              { key: "consequents", label: "Consequents (…they also buy)" },
              { key: "support", label: "Support" },
              { key: "confidence", label: "Confidence" },
              { key: "lift", label: "Lift" },
            ]}
            rows={rules}
          />
        ) : (
          <div className="card p-6 text-center text-sm text-slate-500">
            No rules available for this cluster (file may be missing or empty).
          </div>
        )}
      </div>
    </div>
  );
}
