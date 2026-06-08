import { useState } from "react";
import { SEGMENTS } from "../data/segments";
import SegmentCard from "../components/SegmentCard";
import CampaignCard from "../components/CampaignCard";
import SegmentSpendBars from "../components/charts/SegmentSpendBars";

export default function Segments() {
  const [activeId, setActiveId] = useState(SEGMENTS[0].id);
  const active = SEGMENTS.find((s) => s.id === activeId);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Segments</h1>
        <p className="mt-1 text-slate-600">
          Five distinct customer profiles identified through K-Means clustering.
          Click any segment to see its full profile, defining characteristics
          and tailored campaigns.
        </p>
      </header>

      {/* Cards row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {SEGMENTS.map((s) => (
          <SegmentCard
            key={s.id}
            segment={s}
            active={s.id === activeId}
            onClick={() => setActiveId(s.id)}
          />
        ))}
      </div>

      {/* Detail */}
      <div className="card p-6">
        <div className="flex items-center gap-3">
          <span
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: active.color }}
          />
          <h2 className="text-2xl font-bold text-slate-900">{active.name}</h2>
          <span className="ml-auto text-sm font-medium text-slate-500">
            {active.customers.toLocaleString()} customers · {active.pct}% of base
          </span>
        </div>

        <p className="mt-4 text-slate-700 leading-relaxed">
          {active.description}
        </p>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="section-title">Defining characteristics</h3>
            <ul className="space-y-2 text-sm text-slate-700">
              {active.characteristics.map((c, i) => (
                <li key={i} className="flex gap-2">
                  <span
                    className="mt-2 w-1.5 h-1.5 rounded-full shrink-0"
                    style={{ backgroundColor: active.color }}
                  />
                  <span>{c}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="section-title">At a glance</h3>
            <div className="grid grid-cols-2 gap-3">
              <Stat label="Customers" val={active.customers.toLocaleString()} />
              <Stat label="Share" val={`${active.pct}%`} />
              <Stat label="Avg lifetime spend" val={`€${active.avgSpend.toLocaleString()}`} />
              <Stat label="Avg age" val={`${active.avgAge} y`} />
              <Stat label="Avg children" val={active.avgChildren} />
              <Stat label="Avg tenure" val={`${active.avgTenure} y`} />
            </div>
          </div>
        </div>

        {/* Spend profile chart */}
        <div className="mt-8">
          <h3 className="section-title">Where this segment spends</h3>
          <p className="text-xs text-slate-500 mb-3">
            Average lifetime spend per category — sorted, bar opacity reflects
            magnitude relative to this segment's top category.
          </p>
          <SegmentSpendBars segmentId={active.id} />
        </div>
      </div>

      {/* Campaigns */}
      <div>
        <h3 className="section-title">Campaigns for {active.name}</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {active.campaigns.map((c, i) => (
            <CampaignCard
              key={i}
              campaign={c}
              accentColor={active.color}
              index={i}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, val }) {
  return (
    <div className="border border-slate-200 rounded-lg px-3 py-2">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-0.5 font-semibold text-slate-900">{val}</div>
    </div>
  );
}
