import {
  AnalysisResponse,
  CodeInput,
  FinalReportPayload,
  FinalReportResponse,
  HtmlReportResponse,
  RepairRequestPayload,
  RepairResponse
} from "./types";

const API_BASE_URL = __API_BASE_URL__;

async function postJson<T>(endpoint: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Request failed (${response.status}): ${detail}`);
  }

  return response.json() as Promise<T>;
}

export function runFullAnalysis(input: CodeInput) {
  return postJson<AnalysisResponse>("full-analysis", input);
}

export function repairProgram(payload: RepairRequestPayload) {
  return postJson<RepairResponse>("repair", payload);
}

export function buildFinalReport(payload: FinalReportPayload) {
  return postJson<FinalReportResponse>("report", payload);
}

export function generateHtmlReport(payload: {
  analysis_result: AnalysisResponse;
  repair_result?: RepairResponse | null;
  output_filename?: string;
}) {
  return postJson<HtmlReportResponse>("generate-report", payload);
}

