export default function CampaignCard({ campaign, accentColor, index }) {
  return (
    <div className="card p-4 flex gap-4">
      <div
        className="w-1 self-stretch rounded-full shrink-0"
        style={{ backgroundColor: accentColor }}
      />
      <div className="flex-1 min-w-0">
        <div className="flex items-start gap-3">
          <span
            className="text-xs font-mono text-slate-400 mt-0.5 shrink-0"
            style={{ minWidth: "1.5rem" }}
          >
            {String(index + 1).padStart(2, "0")}
          </span>
          <div className="flex-1">
            <h4 className="font-semibold text-slate-900 leading-snug">
              {campaign.title}
            </h4>
            <p className="mt-2 text-sm text-slate-600 leading-relaxed">
              {campaign.rationale}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
