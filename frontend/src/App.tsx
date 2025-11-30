import { useState } from "react";
import {
  AnalysisResponse,
  FinalReportResponse,
  RepairResponse,
  CodeInput,
  AnalysisBug
} from "./types";
import { CodeInputForm } from "./components/CodeInputForm";
import { Section } from "./components/Section";
import { ResultsPanel } from "./components/ResultsPanel";
import { LoadingIndicator } from "./components/LoadingIndicator";
import { runFullAnalysis, repairProgram, buildFinalReport, generateHtmlReport } from "./api";

const DEFAULT_CODE: CodeInput = {
  filename: "buggy_div.c",
  code: `#include <klee/klee.h>

int main() {
    int x;
    klee_make_symbolic(&x, sizeof(x), "x");
    if (x > 100) {
        return x;
    }
    return 100 / (x - 10);
}`
};

type LoadingState = "idle" | "analysis" | "repair" | "report" | "html";

export default function App() {
  const [analysis, setAnalysis] = useState<AnalysisResponse>();
  const [repair, setRepair] = useState<RepairResponse | null>(null);
  const [finalReport, setFinalReport] = useState<FinalReportResponse | null>(null);
  const [htmlReportPath, setHtmlReportPath] = useState<string | null>(null);
  const [loading, setLoading] = useState<LoadingState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [currentInput, setCurrentInput] = useState<CodeInput>(DEFAULT_CODE);

  const firstBug = analysis?.result.bugs?.[0];

  const resetDownstreamState = () => {
    setRepair(null);
    setFinalReport(null);
    setHtmlReportPath(null);
  };

  const handleRunAnalysis = async (input: CodeInput) => {
    setLoading("analysis");
    setError(null);
    setStatusMessage("Running KLEE full analysis...");
    try {
      setCurrentInput(input);
      const result = await runFullAnalysis(input);
      setAnalysis(result);
      resetDownstreamState();
      setStatusMessage("Analysis completed successfully.");
    } catch (analysisError) {
      setError(analysisError instanceof Error ? analysisError.message : String(analysisError));
    } finally {
      setLoading("idle");
    }
  };

  const ensureBugDetails = (): AnalysisBug => {
    if (!firstBug) {
      throw new Error("Cannot repair because no bugs were reported in the latest analysis.");
    }
    return firstBug;
  };

  const handleRunRepair = async () => {
    if (!analysis) {
      setError("Run an analysis before requesting a repair.");
      return;
    }

    setLoading("repair");
    setError(null);
    setStatusMessage("Requesting AI repair suggestion...");
    try {
      const bugDetails = ensureBugDetails();
      const repairResult = await repairProgram({
        original_code: currentInput.code,
        original_filename: currentInput.filename,
        bug_details: bugDetails
      });

      setRepair(repairResult);
      setStatusMessage("Repair attempt completed.");
    } catch (repairError) {
      setError(repairError instanceof Error ? repairError.message : String(repairError));
    } finally {
      setLoading("idle");
    }
  };

  const handleBuildReport = async () => {
    if (!analysis) {
      setError("Run an analysis before creating the final report.");
      return;
    }

    setLoading("report");
    setError(null);
    setStatusMessage("Generating final consolidated report...");
    try {
      const reportResponse = await buildFinalReport({
        initial_analysis: analysis,
        repair_results: repair ?? undefined,
        original_code: currentInput.code
      });
      setFinalReport(reportResponse);
      setStatusMessage("Report generated. You can now export HTML.");
    } catch (reportError) {
      setError(reportError instanceof Error ? reportError.message : String(reportError));
    } finally {
      setLoading("idle");
    }
  };

  const handleExportHtml = async () => {
    if (!analysis) {
      setError("Run an analysis before exporting an HTML report.");
      return;
    }

    setLoading("html");
    setError(null);
    setStatusMessage("Rendering HTML report...");
    try {
      const response = await generateHtmlReport({
        analysis_result: analysis,
        repair_result: repair ?? undefined,
        output_filename: "latest-report.html"
      });
      setHtmlReportPath(response.report_path);
      setStatusMessage("HTML report saved to workspace.");
    } catch (htmlError) {
      setError(htmlError instanceof Error ? htmlError.message : String(htmlError));
    } finally {
      setLoading("idle");
    }
  };

  return (
    <>
      <header>
        <h1>AI-Assisted Symbolic Execution Dashboard</h1>
        <p>Upload C code, run KLEE analysis, request AI repairs, and export comprehensive reports.</p>
      </header>

      {statusMessage && (
        <div className="status-banner" role="status">
          {loading !== "idle" ? <LoadingIndicator text={statusMessage} /> : <span>{statusMessage}</span>}
        </div>
      )}
      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}

      <Section title="1. Upload & Analyze" subtitle="Runs compilation + KLEE analysis per FR1–FR8.">
        <CodeInputForm initialCode={DEFAULT_CODE} busy={loading === "analysis"} onRunAnalysis={handleRunAnalysis} />
      </Section>

      <Section
        title="2. Post-Analysis Actions"
        subtitle="Request AI repair, consolidate reports, and export HTML (FR9–FR13)."
        actions={
          <div className="actions-row">
            <button onClick={handleRunRepair} disabled={!analysis || loading === "repair"}>
              {loading === "repair" ? "Repairing..." : "Run AI Repair"}
            </button>
            <button onClick={handleBuildReport} disabled={!analysis || loading === "report"}>
              {loading === "report" ? "Building..." : "Build Final Report"}
            </button>
            <button onClick={handleExportHtml} disabled={!analysis || loading === "html"}>
              {loading === "html" ? "Exporting..." : "Export HTML"}
            </button>
          </div>
        }
      >
        <ResultsPanel
          analysis={analysis}
          repair={repair}
          report={finalReport}
          htmlReportPath={htmlReportPath}
        />
      </Section>
    </>
  );
}

