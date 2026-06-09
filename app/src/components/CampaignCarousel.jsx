import { useEffect, useState, useRef } from "react";

/**
 * Hero carousel for one segment's campaigns.
 * The image is the creative — no text overlay. Controls float on top.
 * Auto-plays every 7s, pauses on hover.
 */
export default function CampaignCarousel({ segment }) {
  const [idx, setIdx] = useState(0);
  const [paused, setPaused] = useState(false);
  const total = segment.campaigns.length;
  const timerRef = useRef(null);

  // Reset to first campaign whenever segment changes
  useEffect(() => {
    setIdx(0);
  }, [segment.id]);

  // Auto-play
  useEffect(() => {
    if (paused) return;
    timerRef.current = setTimeout(() => {
      setIdx((i) => (i + 1) % total);
    }, 7000);
    return () => clearTimeout(timerRef.current);
  }, [idx, paused, total]);

  const go = (newIdx) => setIdx((newIdx + total) % total);
  const current = segment.campaigns[idx];

  return (
    <div
      className="relative rounded-2xl overflow-hidden shadow-xl bg-slate-900"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      {/* Image — fills the container at 3:1 aspect ratio */}
      <div className="relative w-full" style={{ aspectRatio: "3 / 1" }}>
        <img
          key={current.image /* re-trigger transition on change */}
          src={current.image}
          alt={current.title}
          className="absolute inset-0 w-full h-full object-cover animate-fade"
          loading="lazy"
        />
      </div>

      {/* Floating controls (bottom-left dots, bottom-right arrows) */}
      <div className="absolute inset-x-0 bottom-0 p-4 md:p-5 flex items-center justify-between pointer-events-none">
        {/* Dots */}
        <div className="flex gap-2 pointer-events-auto bg-black/30 backdrop-blur-sm rounded-full px-3 py-1.5">
          {segment.campaigns.map((_, i) => (
            <button
              key={i}
              onClick={() => go(i)}
              aria-label={`Go to campaign ${i + 1}`}
              className={[
                "h-2 rounded-full transition-all",
                i === idx ? "w-8 bg-white" : "w-2 bg-white/50 hover:bg-white/80",
              ].join(" ")}
            />
          ))}
        </div>

        {/* Arrows + counter */}
        <div className="flex items-center gap-3 pointer-events-auto">
          <span className="text-xs font-mono text-white/85 bg-black/30 backdrop-blur-sm rounded-full px-3 py-1.5">
            {String(idx + 1).padStart(2, "0")} /{" "}
            {String(total).padStart(2, "0")}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => go(idx - 1)}
              aria-label="Previous campaign"
              className="w-9 h-9 rounded-full bg-black/40 hover:bg-black/60 backdrop-blur-sm border border-white/20 text-white flex items-center justify-center transition-colors text-lg"
            >
              ‹
            </button>
            <button
              onClick={() => go(idx + 1)}
              aria-label="Next campaign"
              className="w-9 h-9 rounded-full bg-black/40 hover:bg-black/60 backdrop-blur-sm border border-white/20 text-white flex items-center justify-center transition-colors text-lg"
            >
              ›
            </button>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fade { from { opacity: 0; } to { opacity: 1; } }
        .animate-fade { animation: fade 0.5s ease-out; }
      `}</style>
    </div>
  );
}
