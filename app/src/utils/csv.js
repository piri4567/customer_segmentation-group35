import Papa from "papaparse";

/**
 * Load a CSV from the /public folder and return parsed rows.
 * Numeric strings are auto-converted; whitespace is trimmed.
 */
export async function loadCSV(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to fetch ${path}: ${res.status}`);
  const text = await res.text();
  return new Promise((resolve, reject) => {
    Papa.parse(text, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      transformHeader: (h) => h.trim(),
      complete: (results) => resolve(results.data),
      error: (err) => reject(err),
    });
  });
}
