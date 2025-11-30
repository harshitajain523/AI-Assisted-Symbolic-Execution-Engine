import json
import os
import time
from typing import Any, Dict

import requests

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"
API_KEY_ENV_VAR = "GEMINI_API_KEY"

def generate_repair_candidate(original_code: str, bug_details: dict) -> str:
    """
    Calls the Gemini API to generate a code repair candidate based on bug context.
    Ref: SRS FR9 (AI Repair)
    """
    
    # Extract necessary context for the prompt
    bug_type = bug_details.get("severity", "Bug")
    error_message = bug_details.get("message", "A memory safety error was detected.")
    line_number = bug_details.get("line", "Unknown line")
    
    # 1. System Instruction: Define the LLM's persona and rules
    system_prompt = (
        "You are an expert C code security and debugging assistant. "
        "Your task is to analyze a C code snippet and a KLEE symbolic execution error report. "
        "You must provide a single, concise block of corrected code that fixes the vulnerability. "
        "Do NOT include any surrounding text, explanations, or Markdown fences outside of the code block. "
        "The output must be ONLY the corrected C code."
    )
    
    # 2. User Query: Give the specific task and all relevant data
    user_query = (
        f"The following C code was analyzed by the KLEE symbolic execution engine:\n\n"
        f"--- CODE ---\n{original_code}\n\n"
        f"--- ERROR REPORT ---\n"
        f"KLEE detected a {bug_type} issue on or around line {line_number}. The specific error was: {error_message}\n\n"
        f"Please provide ONLY the corrected and fixed version of the ENTIRE C function. "
        f"Do not modify parts of the code that are unrelated to the bug."
    )
    
    payload: Dict[str, Any] = {
        "contents": [{"parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }

    # Implement basic exponential backoff for API calls
    max_retries = 3
    for attempt in range(max_retries):
        try:
            api_key = os.getenv(API_KEY_ENV_VAR)
            if not api_key:
                return (
                    "Repair failed: GEMINI_API_KEY environment variable is missing. "
                    "Set the key before invoking the repair endpoint."
                )

            response = requests.post(
                f"{API_URL}?key={api_key}", 
                headers={'Content-Type': 'application/json'}, 
                data=json.dumps(payload)
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the raw text response
            generated_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
            
            # Extract the content from the markdown block
            if '```' in generated_text:
                start = generated_text.find('```') + 3
                # Skip the language identifier (like 'c\n')
                start = generated_text.find('\n', start) + 1 if generated_text[start:].startswith(('c', 'cpp')) else start
                
                end = generated_text.rfind('```')
                if end > start:
                    return generated_text[start:end].strip()
            
            return generated_text # Fallback: return raw text if no markdown block found

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429 and attempt < max_retries - 1:
                # Handle Rate Limiting with exponential backoff
                wait_time = 2 ** attempt
                print(f"Rate limit hit. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return f"API Error: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    return "Repair failed after maximum retries."