import { useState } from "react";
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
  const Page = PAGES[active] ?? Overview;

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar active={active} onChange={setActive} />
      <main className="flex-1 min-w-0 px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <Page />
        </div>
      </main>
    </div>
  );
}
