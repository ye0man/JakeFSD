import { useState } from "react";
import { invoke } from "@tauri-apps/api/core";

interface Stage {
  id: string;
  type: string;
  connector: string;
}

interface PreviewPaneProps {
  pipeline: { name: string; stages: Stage[] } | null;
  manifestPath: string;
}

export default function PreviewPane({ pipeline, manifestPath }: PreviewPaneProps) {
  const [selectedStage, setSelectedStage] = useState<string>("");
  const [data, setData] = useState<Record<string, unknown>[] | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  if (!pipeline || pipeline.stages.length === 0) {
    return <div className="empty-state">Generate a pipeline first to preview stages.</div>;
  }

  async function loadPreview() {
    if (!selectedStage) return;
    setLoading(true);
    setError("");
    setData(null);
    try {
      const result = await invoke<string>("preview_stage", {
        manifestPath,
        stageId: selectedStage,
      });
      setData(JSON.parse(result) as Record<string, unknown>[]);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="preview-pane">
      <div className="preview-toolbar">
        <label htmlFor="stage-select">Stage:</label>
        <select
          id="stage-select"
          value={selectedStage}
          onChange={(e) => setSelectedStage(e.target.value)}
        >
          <option value="">Select a stage</option>
          {pipeline.stages.map((stage) => (
            <option key={stage.id} value={stage.id}>
              {stage.id} ({stage.connector})
            </option>
          ))}
        </select>
        <button onClick={loadPreview} disabled={!selectedStage || loading}>
          {loading ? "Loading..." : "Preview"}
        </button>
      </div>

      {error && <div className="preview-error">{error}</div>}

      {data && data.length > 0 && (
        <div className="preview-table-wrapper">
          <table className="preview-table">
            <thead>
              <tr>
                {Object.keys(data[0]).map((col) => (
                  <th key={col}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => (
                <tr key={idx}>
                  {Object.values(row).map((value, vidx) => (
                    <td key={vidx}>{String(value)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data && data.length === 0 && <div className="empty-state">No rows returned.</div>}
    </div>
  );
}
