import { AnalysisResponse, FinalReportResponse, RepairResponse } from "../types";

interface ResultsPanelProps {
  analysis?: AnalysisResponse;
  repair?: RepairResponse | null;
  report?: FinalReportResponse | null;
  htmlReportPath?: string | null;
}

export function ResultsPanel({ analysis, repair, report, htmlReportPath }: ResultsPanelProps) {
  return (
    <div className="results-grid">
      <div className="card">
        <h3>Analysis Summary</h3>
        {analysis ? (
          <>
            <p>
              Program: <strong>{analysis.result.program_name}</strong>
            </p>
            <p>
              Coverage: <strong>{analysis.result.coverage_percentage}%</strong>
            </p>
            <p>
              Bugs Detected: <strong>{analysis.result.bugs.length}</strong>
            </p>
            <details>
              <summary>View Paths</summary>
              <ul>
                {analysis.result.paths.map((path) => (
                  <li key={path.path_id}>
                    Path {path.path_id}: {path.summary}
                  </li>
                ))}
              </ul>
            </details>
            <details>
              <summary>Bug Details</summary>
              <ul>
                {analysis.result.bugs.map((bug, index) => (
                  <li key={`${bug.type}-${index}`}>
                    [{bug.severity}] {bug.message} (line {bug.line ?? "?"})
                  </li>
                ))}
              </ul>
            </details>
          </>
        ) : (
          <p>Run an analysis to view details.</p>
        )}
      </div>

      <div className="card">
        <h3>AI Repair</h3>
        {repair ? (
          <>
            <p>Status: {repair.validation_status ?? repair.status}</p>
            {repair.llm_model && <p>Model: {repair.llm_model}</p>}
            {repair.message && <p>Message: {repair.message}</p>}
            {repair.details && (
              <details>
                <summary>Details</summary>
                <pre>{repair.details}</pre>
              </details>
            )}
            {repair.suggested_code && (
              <details>
                <summary>Suggested Code</summary>
                <pre>{repair.suggested_code}</pre>
              </details>
            )}
            {Array.isArray(repair.validation_report) && repair.validation_report.length > 0 && (
              <details>
                <summary>Validation Bugs</summary>
                <ul>
                  {repair.validation_report.map((bug, index) => (
                    <li key={`${bug.type}-${index}`}>
                      {bug.type} (line {bug.line ?? "?"})
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </>
        ) : (
          <p>Generate a repair after analysis.</p>
        )}
      </div>

      <div className="card">
        <h3>Final Report</h3>
        {report ? (
          <>
            <p>Program: {report.program_details.name}</p>
            <p>Initial bugs: {report.initial_analysis_summary.bugs_found}</p>
            <p>AI Repair Status: {report.ai_repair_summary?.status ?? "Not Run"}</p>
            {htmlReportPath && (
              <p>
                HTML Report: <code>{htmlReportPath}</code>
              </p>
            )}
          </>
        ) : (
          <p>Generate the final report to summarize analysis + repair.</p>
        )}
      </div>
    </div>
  );
}

