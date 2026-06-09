import { useEffect, useState } from "react";
import { loadCSV } from "./csv";
import { SEGMENT_BY_ID } from "../data/segments";

/**
 * Loads cluster_summary.csv and joins it with the static segment metadata
 * (name + color) so charts can use the right label and palette.
 *
 * Returns an array of rows shaped like:
 *   { cluster, segment, color, age, total_spend, ... }
 */
export function useClusterSummary() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCSV("/data/cluster_summary.csv")
      .then((data) => {
        const enriched = data.map((row) => {
          const segMeta = SEGMENT_BY_ID[row.cluster] ?? {};
          return {
            ...row,
            segment: segMeta.name ?? `Cluster ${row.cluster}`,
            short: segMeta.short ?? `C${row.cluster}`,
            color: segMeta.color ?? "#94a3b8",
          };
        });
        setRows(enriched);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return { rows, loading };
}
