from __future__ import annotations

import os
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.ai.repair_module import generate_repair_candidate
from src.executor.coverage_analyzer import CoverageAnalyzer
from src.executor.klee_runner import (
    WORKSPACE_DIR,
    compile_to_bitcode,
    extract_paths,
    run_klee,
)
from src.executor.ktest_parser import parse_ktest
from src.reporting.html_generator import HTMLReportGenerator, save_html_report


app = FastAPI(title="AI-Assisted Symbolic Execution Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def classify_bug(bug_type: str) -> str:
    """Maps KLEE error types to severity levels (Critical, High, Medium, Low). (FR8)"""
    bug_type = bug_type.lower()
    
    if any(keyword in bug_type for keyword in ['overflow', 'ptr.err', 'ptr', 'null', 'memory', 'free', 'use-after']):
        return "Critical"
    elif any(keyword in bug_type for keyword in ['divide by zero', 'div.err', 'division', 'assert.err', 'assertion']):
        return "High"
    elif any(keyword in bug_type for keyword in ['abort', 'warning', 'overflow', 'underflow']):
        return "Medium"
    else:
        return "Low"


def find_bug_path(bug: dict, paths: list) -> int:
    """Map bug to the path that triggered it."""
    import re
    bug_file = bug.get("err_file", "") 
    
    match = re.search(r'test(\d+)', str(bug_file))
    if match:
        test_num = int(match.group(1))
        # Find corresponding path (assuming path_id starts at 1)
        for path in paths:
            if path["path_id"] == test_num:
                return path["path_id"]
    
    return 1  # Default to first path if not found


# --- Pydantic Models ---
class CodeInput(BaseModel):
    filename: str
    code: str

class AnalysisRequest(BaseModel):
    bc_path: str

# Model for Repair Request 
class RepairRequest(BaseModel):
    original_code: str
    bug_details: dict
    original_filename: str

# NEW: Model for Final Report Consolidation (FR11 & FR12)
class FinalReportRequest(BaseModel):
    initial_analysis: dict
    repair_results: dict | None = None
    original_code: str

class HtmlReportRequest(BaseModel):
    analysis_result: dict
    repair_result: dict | None = None
    output_filename: str = "report.html"


# --- API Endpoints ---
@app.get("/")
def root():
    return {"status": "Active", "version": "1.0"}


@app.post("/compile")
def compile_code(data: CodeInput):
    """Compiles C code to LLVM Bitcode (FR2)."""
    try:
        bc_path = compile_to_bitcode(data.filename, data.code)
        rel_path = os.path.relpath(bc_path, WORKSPACE_DIR)
        return {"status": "success", "bc_path": rel_path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze")
def analyze_program(data: AnalysisRequest):
    """
    Runs KLEE and returns standardized analysis results (FR4, FR6, FR8).
    NOTE: This is the old /analyze that you may have replaced with /full-analysis. 
    Keeping both for full compatibility.
    """
    full_bc_path = os.path.join(WORKSPACE_DIR, data.bc_path)
    
    if not os.path.exists(full_bc_path):
        raise HTTPException(status_code=404, detail="Bitcode not found")
    
    try:
        start_time = time.time()
        
        out_dir, tests, bugs, logs = run_klee(full_bc_path)
        
        # NOTE: extract_paths is assumed to be defined elsewhere
        paths = extract_paths(out_dir) 
        
        classified_bugs = []
        for bug in bugs:
            bug_type = bug.get("type", "Unknown")
            bug["severity"] = classify_bug(bug_type)
            bug["path_id"] = find_bug_path(bug, paths) if paths else 1
            classified_bugs.append(bug)
        
        # NOTE: CoverageAnalyzer is assumed to be defined elsewhere
        source_file = full_bc_path.replace('.bc', '.c')
        coverage_analyzer = CoverageAnalyzer()
        coverage_data = coverage_analyzer.calculate_coverage(out_dir, source_file)
        
        for path in paths:
            path["line_coverage"] = coverage_data.get("lines_covered", [])
        
        execution_time = time.time() - start_time
        
        program_name = Path(data.bc_path).stem + '.c'
        
        result = {
            "program_name": program_name,
            "total_paths": len(paths),
            "explored_paths": len(paths),
            "execution_time": round(execution_time, 2),
            "coverage_percentage": coverage_data.get("coverage_percentage", 0.0),
            "paths": paths,
            "bugs": classified_bugs,
            "metadata": {
                "klee_output_dir": out_dir,
                "total_lines": coverage_data.get("total_lines", 0),
                "lines_covered": coverage_data.get("lines_covered", []),
                "raw_tests": tests,
                "logs": logs
            }
        }
        
        return {
            "status": "completed",
            "result": result
        }
        
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")


@app.post("/full-analysis")
def full_analysis(data: CodeInput):
    """
    Combined endpoint: Compile + Analyze in one call.
    Refs: SRS FR1-FR8 (Complete pipeline)
    """
    try:
        bc_path = compile_to_bitcode(data.filename, data.code)
        
        rel_path = os.path.relpath(bc_path, WORKSPACE_DIR)
        analysis_req = AnalysisRequest(bc_path=rel_path)
        
        result = analyze_program(analysis_req)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/repair")
def repair_code(data: RepairRequest):
    """
    1. Generates a code repair candidate using the LLM (FR9).
    2. Compiles and Re-runs KLEE on the candidate code (FR10: Repair Validation).
    """
    
    # --- Part 1: Generate AI Code (FR9) ---
    try:
        candidate_code = generate_repair_candidate(
            data.original_code,
            data.bug_details
        )
        if candidate_code.startswith("API Error") or candidate_code.startswith("Repair failed"):
             return {
                "status": "ai_failed",
                "message": "AI generation failed. Check API key or rate limits.",
                "details": candidate_code
             }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI communication error: {str(e)}")

    # --- Part 2: Validation (FR10) ---
    validation_status = "Validation Failed"
    validation_bugs = []
    
    try:
        # Give the file a temporary name for compilation
        temp_filename = data.original_filename.replace(".c", f"_repaired_{uuid.uuid4().hex[:4]}.c")
        
        # Compile the AI's suggested code
        repaired_bc_path = compile_to_bitcode(temp_filename, candidate_code)
        
        # Re-run KLEE on the repaired code (only need the bugs list for validation)
        _, _, validation_bugs, _ = run_klee(repaired_bc_path)
        
        if not validation_bugs:
            validation_status = "Validation Success"
        else:
            # Check if the original bug still exists
            original_bug_type = data.bug_details.get("type", "Unknown")
            
            # Count how many validation bugs match the original bug type
            original_bug_still_exists = any(original_bug_type in bug.get("type", "") for bug in validation_bugs)
            
            if original_bug_still_exists:
                 validation_status = "Validation Failed (Original Bug Still Exists)"
            else:
                 # If the original bug is fixed, but new ones exist
                 validation_status = "Validation Failed (New Regression Introduced)"


    except Exception as e:
        validation_status = f"Validation Failed (Compilation/Runtime Error: {str(e)})"


    return {
        "status": "repair_validated",
        "suggested_code": candidate_code,
        "validation_status": validation_status,
        "validation_report": validation_bugs,
        "llm_model": "Gemini 2.5 Flash"
    }

# NEW: Endpoint for generating the Final Consolidated Report (FR11 & FR12)
@app.post("/report")
def generate_final_report(data: FinalReportRequest):
    """
    Consolidates data from the initial analysis and the repair validation 
    into a single structure suitable for final reporting and visualization.
    """
    report = {
        "program_details": {
            "name": data.initial_analysis.get("result", {}).get("program_name", "N/A"),
            "original_code": data.original_code,
            "total_lines": data.initial_analysis.get("result", {}).get("metadata", {}).get("total_lines", 0)
        },
        
        "initial_analysis_summary": {
            "status": "Completed",
            "bugs_found": len(data.initial_analysis.get("result", {}).get("bugs", [])),
            "max_severity": max([b.get("severity", "Low") for b in data.initial_analysis.get("result", {}).get("bugs", [])], default="None"),
            "coverage_percentage": data.initial_analysis.get("result", {}).get("coverage_percentage", 0.0),
            "execution_time_s": data.initial_analysis.get("result", {}).get("execution_time", 0.0)
        },
        
        "detailed_results": {
            "bugs": data.initial_analysis.get("result", {}).get("bugs", []),
            "paths": data.initial_analysis.get("result", {}).get("paths", []),
            "lines_covered": data.initial_analysis.get("result", {}).get("metadata", {}).get("lines_covered", [])
        },
        
        "ai_repair_summary": {
            "status": data.repair_results.get("validation_status", "N/A"),
            "suggested_code": data.repair_results.get("suggested_code", "N/A"),
            "validation_report": data.repair_results.get("validation_report", []),
            "llm_model": data.repair_results.get("llm_model", "N/A")
        } if data.repair_results else None
    }
    
    # FR13 (Export): Return the JSON for immediate use or conversion to PDF/HTML
    return report


@app.get("/results/{file_path:path}")
def get_test_result(file_path: str):
    """Retrieves the concrete symbolic input for a test file (FR7)."""
    safe_path = os.path.normpath(file_path)
    if ".." in safe_path:
        raise HTTPException(status_code=403, detail="Access denied")
    
    full_path = os.path.join(WORKSPACE_DIR, safe_path)
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"File not found: {safe_path}")
    
    try:
        return parse_ktest(full_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "workspace": str(WORKSPACE_DIR),
        "workspace_exists": os.path.exists(WORKSPACE_DIR)
    }


@app.post("/generate-report")
async def generate_html_report(payload: HtmlReportRequest):
    """
    Generate HTML report from analysis/repair results.
    SRS FR11, FR13
    """
    try:
        generator = HTMLReportGenerator()
        html_content = generator.generate_report(
            payload.analysis_result,
            payload.repair_result,
        )

        reports_dir = os.path.join(WORKSPACE_DIR, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        output_path = os.path.join(reports_dir, payload.output_filename)
        save_html_report(html_content, output_path)

        return {
            "status": "success",
            "report_path": output_path,
            "html_content": html_content,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))