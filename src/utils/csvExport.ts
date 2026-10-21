/**
 * csvExport.ts
 * Robust RFC-4180 compliant CSV export utility for analysis dashboards.
 */

export function exportToCsv(
  filename: string,
  data: Record<string, any>[],
  customColumns?: { key: string; label: string }[]
): boolean {
  if (!data || data.length === 0) {
    console.warn("exportToCsv: No data to export");
    return false;
  }

  // Determine headers
  const columns = customColumns
    ? customColumns
    : Object.keys(data[0]).map((k) => ({ key: k, label: k }));

  const formatValue = (val: any): string => {
    if (val === null || val === undefined) return "";
    let str = typeof val === "object" ? JSON.stringify(val) : String(val);

    // Escape quotes and wrap if commas/quotes/newlines exist
    if (str.includes('"') || str.includes(",") || str.includes("\n") || str.includes("\r")) {
      str = `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  };

  const headerLine = columns.map((c) => formatValue(c.label)).join(",");
  const rowLines = data.map((row) =>
    columns.map((c) => formatValue(row[c.key])).join(",")
  );

  const csvContent = "\uFEFF" + [headerLine, ...rowLines].join("\r\n"); // UTF-8 BOM for Excel compatibility

  try {
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    const cleanFilename = filename.endsWith(".csv") ? filename : `${filename}.csv`;
    link.setAttribute("href", url);
    link.setAttribute("download", cleanFilename);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    return true;
  } catch (error) {
    console.error("CSV Export failed:", error);
    return false;
  }
}
