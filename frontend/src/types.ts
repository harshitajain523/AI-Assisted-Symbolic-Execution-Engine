export interface CodeInput {
  filename: string;
  code: string;
}

export interface AnalysisBug {
  type: string;
  severity: string;
  message: string;
  line: number;
  err_file?: string;
  path_id?: number;
}

export interface AnalysisPath {
  path_id: number;
  test_name: string;
  is_buggy: boolean;
  summary: string;
  line_coverage?: number[];
}

export interface AnalysisMetadata {
  klee_output_dir: string;
  total_lines: number;
  lines_covered: number[];
  raw_tests: string[];
  logs: string;
}

export interface AnalysisResultPayload {
  program_name: string;
  total_paths: number;
  explored_paths: number;
  execution_time: number;
  coverage_percentage: number;
  paths: AnalysisPath[];
  bugs: AnalysisBug[];
  metadata: AnalysisMetadata;
}

export interface AnalysisResponse {
  status: string;
  result: AnalysisResultPayload;
}

export interface RepairRequestPayload {
  original_code: string;
  bug_details: AnalysisBug;
  original_filename: string;
}

export interface RepairResponse {
  status: string;
  suggested_code?: string;
  validation_status?: string;
  validation_report?: AnalysisBug[];
  llm_model?: string;
  message?: string;
  details?: string;
}

export interface FinalReportPayload {
  initial_analysis: AnalysisResponse;
  repair_results?: RepairResponse | null;
  original_code: string;
}

export interface FinalReportResponse {
  program_details: {
    name: string;
    original_code: string;
    total_lines: number;
  };
  initial_analysis_summary: {
    status: string;
    bugs_found: number;
    max_severity: string;
    coverage_percentage: number;
    execution_time_s: number;
  };
  detailed_results: {
    bugs: AnalysisBug[];
    paths: AnalysisPath[];
    lines_covered: number[];
  };
  ai_repair_summary: {
    status: string;
    suggested_code: string;
    validation_report: AnalysisBug[];
    llm_model: string;
  } | null;
}

export interface HtmlReportResponse {
  status: string;
  report_path: string;
  html_content: string;
}

