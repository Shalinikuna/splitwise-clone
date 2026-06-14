import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/layout/Navbar";
import { importService } from "../services/importService";

const SEVERITY_COLORS = {
  error:   "bg-red-50 border-red-200 text-red-700",
  warning: "bg-yellow-50 border-yellow-200 text-yellow-700",
  info:    "bg-blue-50 border-blue-200 text-blue-600",
};

const SEVERITY_BADGE = {
  error:   "bg-red-100 text-red-700",
  warning: "bg-yellow-100 text-yellow-700",
  info:    "bg-blue-100 text-blue-600",
};

function AnomalyRow({ a }) {
  return (
    <div className={`border rounded-lg px-4 py-2 text-sm ${SEVERITY_COLORS[a.severity] || SEVERITY_COLORS.info}`}>
      <div className="flex items-center gap-2 flex-wrap">
        <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${SEVERITY_BADGE[a.severity]}`}>
          {a.severity.toUpperCase()}
        </span>
        <span className="font-mono text-xs opacity-70">Row {a.row}</span>
        <span className="font-semibold text-xs">[{a.code}]</span>
      </div>
      <p className="mt-1">{a.message}</p>
    </div>
  );
}

function SummaryCard({ label, value, color }) {
  return (
    <div className="card text-center py-4">
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-400 mt-1 uppercase tracking-wide">{label}</p>
    </div>
  );
}

export default function ImportPage() {
  const navigate = useNavigate();
  const fileRef = useRef();
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState("anomalies");

  const handleFile = (f) => {
    if (!f) return;
    if (!f.name.endsWith(".csv")) { setError("Only CSV files accepted."); return; }
    setFile(f);
    setError("");
    setResult(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const res = await importService.uploadCsv(file);
      setResult(res.data);
      setActiveTab("anomalies");
    } catch (e) {
      setError(e.response?.data?.detail || "Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = () => {
    if (!result) return;
    const lines = [
      "# Import Report",
      `# File: ${file?.name}`,
      `# Generated: ${new Date().toISOString()}`,
      "",
      "## SUMMARY",
      `Total Rows: ${result.summary.total_rows}`,
      `Imported:   ${result.summary.imported}`,
      `Skipped:    ${result.summary.skipped}`,
      `Settlements:${result.summary.settlements}`,
      `Anomalies:  ${result.summary.anomaly_count}`,
      "",
      "## ANOMALY BREAKDOWN",
      ...Object.entries(result.summary.anomaly_breakdown || {}).map(
        ([code, count]) => `  ${code}: ${count}`
      ),
      "",
      "## ANOMALIES",
      ...result.anomalies.map(
        (a) => `[${a.severity.toUpperCase()}] Row ${a.row} [${a.code}] ${a.message}`
      ),
      "",
      "## SKIPPED ROWS",
      ...result.skipped.map(
        (s) => `Row ${s.row}: ${s.reason} — "${s.raw?.description || ""}"`
      ),
      "",
      "## IMPORTED EXPENSES",
      "row,date,description,paid_by,amount_inr,split_type,has_anomaly",
      ...result.imported.map(
        (e) =>
          `${e.row},${e.date},"${e.description}",${e.paid_by},${e.amount_inr},${e.split_type},${e.has_anomaly}`
      ),
      "",
      "## SETTLEMENTS",
      "row,date,description,paid_by,paid_to,amount_inr",
      ...result.settlements.map(
        (s) =>
          `${s.row},${s.date},"${s.description}",${s.paid_by},${s.paid_to || ""},${s.amount_inr}`
      ),
    ];
    const blob = new Blob([lines.join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "import_report.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">CSV Import</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Upload your Expenses_Export.csv — anomalies are detected and reported automatically.
            </p>
          </div>
          <button onClick={() => navigate("/")} className="btn-secondary text-sm">
            ← Dashboard
          </button>
        </div>

        {/* Upload zone */}
        {!result && (
          <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-colors ${
              dragging ? "border-brand-500 bg-brand-50" : "border-gray-300 bg-white hover:border-brand-400"
            }`}
          >
            <input
              ref={fileRef}
              type="file"
              accept=".csv"
              className="hidden"
              onChange={(e) => handleFile(e.target.files[0])}
            />
            <div className="text-4xl mb-3">📂</div>
            {file ? (
              <div>
                <p className="font-semibold text-gray-800">{file.name}</p>
                <p className="text-sm text-gray-400 mt-1">{(file.size / 1024).toFixed(1)} KB · Click to change</p>
              </div>
            ) : (
              <div>
                <p className="font-semibold text-gray-700">Drop your CSV here or click to browse</p>
                <p className="text-sm text-gray-400 mt-1">Only .csv files · Expenses_Export.csv</p>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
            {error}
          </div>
        )}

        {file && !result && (
          <button
            onClick={handleUpload}
            disabled={loading}
            className="btn-primary w-full py-3 text-base"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Running anomaly detection...
              </span>
            ) : (
              "🔍 Analyse & Import CSV"
            )}
          </button>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-5">
            {/* Summary cards */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <SummaryCard label="Total Rows"  value={result.summary.total_rows}    color="text-gray-800" />
              <SummaryCard label="Imported"    value={result.summary.imported}       color="text-green-600" />
              <SummaryCard label="Settlements" value={result.summary.settlements}    color="text-blue-600" />
              <SummaryCard label="Skipped"     value={result.summary.skipped}        color="text-red-500" />
              <SummaryCard label="Anomalies"   value={result.summary.anomaly_count}  color="text-yellow-600" />
            </div>

            {/* Anomaly breakdown badges */}
            {result.summary.anomaly_breakdown && (
              <div className="card">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-3">Anomaly Types Detected</p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(result.summary.anomaly_breakdown).map(([code, count]) => (
                    <span key={code} className="bg-yellow-100 text-yellow-800 text-xs font-medium px-2.5 py-1 rounded-full">
                      {code} × {count}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Tabs */}
            <div className="flex gap-1 border-b border-gray-200">
              {[
                { key: "anomalies",   label: `Anomalies (${result.anomalies.length})` },
                { key: "imported",    label: `Imported (${result.imported.length})` },
                { key: "settlements", label: `Settlements (${result.settlements.length})` },
                { key: "skipped",     label: `Skipped (${result.skipped.length})` },
              ].map((t) => (
                <button
                  key={t.key}
                  onClick={() => setActiveTab(t.key)}
                  className={`px-4 py-2 text-sm font-medium transition-colors whitespace-nowrap ${
                    activeTab === t.key
                      ? "border-b-2 border-brand-600 text-brand-600"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Anomalies tab */}
            {activeTab === "anomalies" && (
              <div className="space-y-2">
                {result.anomalies.length === 0 ? (
                  <p className="text-center text-gray-400 py-8">No anomalies detected 🎉</p>
                ) : (
                  result.anomalies.map((a, i) => <AnomalyRow key={i} a={a} />)
                )}
              </div>
            )}

            {/* Imported tab */}
            {activeTab === "imported" && (
              <div className="overflow-x-auto rounded-xl border border-gray-200">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      {["Row", "Date", "Description", "Paid By", "Amount (₹)", "Split", "⚠"].map((h) => (
                        <th key={h} className="px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {result.imported.map((e) => (
                      <tr key={e.row} className={e.has_anomaly ? "bg-yellow-50" : "bg-white"}>
                        <td className="px-3 py-2 font-mono text-xs text-gray-400">{e.row}</td>
                        <td className="px-3 py-2 text-xs">{e.date}</td>
                        <td className="px-3 py-2 max-w-[180px] truncate" title={e.description}>{e.description}</td>
                        <td className="px-3 py-2">{e.paid_by}</td>
                        <td className="px-3 py-2 font-semibold text-gray-800">₹{Number(e.amount_inr).toFixed(2)}</td>
                        <td className="px-3 py-2">
                          <span className="bg-gray-100 text-gray-600 text-xs px-1.5 py-0.5 rounded">{e.split_type}</span>
                        </td>
                        <td className="px-3 py-2">
                          {e.has_anomaly && <span title="Has anomaly">⚠️</span>}
                          {e.is_refund && <span title="Refund" className="ml-1">🔄</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Settlements tab */}
            {activeTab === "settlements" && (
              <div className="space-y-2">
                {result.settlements.length === 0 ? (
                  <p className="text-center text-gray-400 py-8">No settlements detected.</p>
                ) : (
                  result.settlements.map((s) => (
                    <div key={s.row} className="card flex items-center justify-between gap-3">
                      <div>
                        <p className="font-semibold text-sm text-gray-800">{s.description}</p>
                        <p className="text-xs text-gray-400 mt-0.5">
                          Row {s.row} · {s.date} · {s.paid_by} → {s.paid_to || "?"}
                        </p>
                        {s.notes && <p className="text-xs text-gray-400 italic mt-0.5">"{s.notes}"</p>}
                      </div>
                      <span className="font-bold text-blue-600 whitespace-nowrap">
                        ₹{Number(s.amount_inr).toFixed(2)}
                      </span>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Skipped tab */}
            {activeTab === "skipped" && (
              <div className="space-y-2">
                {result.skipped.length === 0 ? (
                  <p className="text-center text-gray-400 py-8">No rows were skipped.</p>
                ) : (
                  result.skipped.map((s) => (
                    <div key={s.row} className="border border-red-200 bg-red-50 rounded-lg px-4 py-2">
                      <p className="text-sm font-semibold text-red-700">
                        Row {s.row} — {s.raw?.description || "(no description)"}
                      </p>
                      <p className="text-xs text-red-600 mt-0.5">Reason: {s.reason}</p>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Action buttons */}
            <div className="flex gap-3">
              <button onClick={handleDownloadReport} className="btn-primary flex-1">
                ⬇ Download Import Report
              </button>
              <button
                onClick={() => { setResult(null); setFile(null); }}
                className="btn-secondary flex-1"
              >
                Import Another File
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
