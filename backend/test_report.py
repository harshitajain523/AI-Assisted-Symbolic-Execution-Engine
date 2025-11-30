import requests
import json
import time

# --- CONFIGURATION ---
API_BASE_URL = "http://localhost:8000"
# NOTE: Using raw string prefix (r"...") to handle the backslashes in the code payload safely in Python
BUGGY_CODE = r'#include <klee/klee.h>\nint main() { int x; klee_make_symbolic(&x, sizeof(x), "x"); return 100/(x-10); }'
BUGGY_FILENAME = "buggy_div.c"

# We pre-define BUG_DETAILS because it contains the result of the analysis (severity, line number)
# We assume the analysis will find the High severity divide-by-zero bug on line 2.
BUG_DETAILS = {
    "type": "divide by zero",
    "line": 2,
    "message": "Error: divide by zero",
    "severity": "High",
    "path_id": 1
}

def make_post_request(endpoint, data):
    """Helper function to send JSON POST requests."""
    url = f"{API_BASE_URL}/{endpoint}"
    print(f"\n[INFO] Calling {url}...")
    
    # Simple retry mechanism for stability
    for attempt in range(3):
        try:
            response = requests.post(
                url, 
                headers={"Content-Type": "application/json"}, 
                data=json.dumps(data)
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Attempt {attempt+1} failed: {e}. Retrying in 2s...")
            time.sleep(2)
    raise ConnectionError(f"Failed to connect to {url} after 3 attempts.")

def run_full_test():
    # 1. INITIAL ANALYSIS (FR1-FR8) - Gets the initial bug report
    print("--- STEP 1: INITIAL ANALYSIS (FR1-FR8) ---")
    analysis_payload = {"filename": BUGGY_FILENAME, "code": BUGGY_CODE}
    initial_analysis_result = make_post_request("full-analysis", analysis_payload)
    print(f"[SUCCESS] Analysis completed. Output dir: {initial_analysis_result['result']['metadata']['klee_output_dir']}")
    
    # ⚠️ Use the Bug Details from the LIVE Analysis Result
    # This ensures we use the exact bug report returned by the server (e.g., path_id, err_file)
    if initial_analysis_result['result']['bugs']:
        live_bug_details = initial_analysis_result['result']['bugs'][0]
    else:
        print("[FAILURE] Analysis found no bugs. Cannot proceed with repair test.")
        return 

    # 2. AI REPAIR & VALIDATION (FR9 & FR10) - Uses the live bug report
    print("\n--- STEP 2: AI REPAIR AND VALIDATION (FR9 & FR10) ---")
    repair_payload = {
        "original_code": BUGGY_CODE,
        "bug_details": live_bug_details, # Using the exact bug details from Step 1
        "original_filename": BUGGY_FILENAME
    }
    repair_results = make_post_request("repair", repair_payload)
    
    print(f"[SUCCESS] Repair completed. Validation status: {repair_results['validation_status']}")

    # 3. GENERATE FINAL REPORT (FR11 & FR12) - Consolidates both results
    print("\n--- STEP 3: GENERATE FINAL REPORT (FR11 & FR12) ---")
    report_payload = {
        "initial_analysis": initial_analysis_result,
        "repair_results": repair_results,
        "original_code": BUGGY_CODE
    }
    final_report = make_post_request("report", report_payload)
    
    print("\n=============================================")
    print("    FINAL CONSOLIDATED REPORT (FR11/FR12)    ")
    print("=============================================")
    print(json.dumps(final_report, indent=4))
    print("=============================================")
    
    # Verification check
    if final_report['ai_repair_summary']['status'] == "Validation Success":
        print("\n[VERIFIED] Full end-to-end flow is confirmed working.")
    else:
        print("\n[FAILURE] Validation did not pass. Check API key or KLEE environment.")


if __name__ == "__main__":
    try:
        run_full_test()
    except Exception as e:
        print(f"\n[FATAL ERROR] The process stopped: {e}")
        print("Ensure Uvicorn is running and 'requests' library is installed.")
