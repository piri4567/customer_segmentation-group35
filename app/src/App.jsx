import { useEffect, useRef, useState } from "react";
import Sidebar from "./components/Sidebar";
import Overview from "./pages/Overview";
import Segments from "./pages/Segments";
import Methodology from "./pages/Methodology";
import Visualisations from "./pages/Visualisations";
import Campaigns from "./pages/Campaigns";

const PAGES = {
  overview: Overview,
  segments: Segments,
  methodology: Methodology,
  visuals: Visualisations,
  campaigns: Campaigns,
};

export default function App() {
  const [active, setActive] = useState("overview");
  const mainRef = useRef(null);
  const Page = PAGES[active] ?? Overview;

  // Reset scroll position to the top whenever the active page changes.
  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
    if (mainRef.current) mainRef.current.scrollTop = 0;
  }, [active]);

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar active={active} onChange={setActive} />
      <main ref={mainRef} className="flex-1 min-w-0 px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <Page />
        </div>
      </main>
    </div>
  );
}
