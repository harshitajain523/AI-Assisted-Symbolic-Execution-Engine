from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class _BugSummary:
    severity: str
    message: str
    line: int | None


class HTMLReportGenerator:
    """
    Simple HTML report builder used by the /generate-report endpoint.
    The goal is to keep the formatting logic self-contained so the API
    handler only orchestrates data movement.
    """

    def generate_report(
        self,
        analysis_result: Dict[str, Any],
        repair_result: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Render a minimal, dependency-free HTML document."""
        normalized_analysis = analysis_result or {}

        # Accept both the raw result payload and the nested structure returned by /full-analysis
        report_body = normalized_analysis.get("result", normalized_analysis)
        program_name = report_body.get("program_name", "N/A")
        coverage = report_body.get("coverage_percentage", 0)
        execution_time = report_body.get("execution_time", 0)
        total_paths = len(report_body.get("paths", []))

        bugs = [
            _BugSummary(
                severity=bug.get("severity", "Unknown"),
                message=bug.get("message", bug.get("type", "Unknown issue")),
                line=bug.get("line"),
            )
            for bug in report_body.get("bugs", [])
        ]

        repair_status = (
            repair_result.get("validation_status", "N/A")
            if repair_result
            else "Not Run"
        )
        suggested_code = (
            repair_result.get("suggested_code", "")
            if repair_result
            else ""
        )

        bug_rows = "".join(
            f"<tr><td>{idx + 1}</td><td>{bug.severity}</td>"
            f"<td>{bug.message}</td><td>{bug.line or 'N/A'}</td></tr>"
            for idx, bug in enumerate(bugs)
        ) or "<tr><td colspan='4'>No bugs reported</td></tr>"

        coverage_rows = "".join(
            f"<li>Path {path.get('path_id', idx + 1)} — "
            f"{'Buggy' if path.get('is_buggy') else 'Clean'}</li>"
            for idx, path in enumerate(report_body.get("paths", []))
        ) or "<li>No execution paths recorded</li>"

        suggested_code_block = (
            f"<pre><code>{self._escape_html(suggested_code)}</code></pre>"
            if suggested_code
            else "<p>No repair suggestion recorded.</p>"
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>KLEE Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 2rem; color: #222; }}
        h1 {{ color: #005f73; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
        th {{ background-color: #f0f4f8; }}
        .section {{ margin-bottom: 2rem; }}
        pre {{ background-color: #f7f7f7; padding: 1rem; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>AI-Assisted Symbolic Execution Report</h1>
    <section class="section">
        <h2>Program Overview</h2>
        <p><strong>Name:</strong> {self._escape_html(program_name)}</p>
        <p><strong>Total Paths:</strong> {total_paths}</p>
        <p><strong>Coverage:</strong> {coverage}%</p>
        <p><strong>Execution Time:</strong> {execution_time}s</p>
    </section>

    <section class="section">
        <h2>Detected Bugs</h2>
        <table>
            <thead>
                <tr><th>#</th><th>Severity</th><th>Message</th><th>Line</th></tr>
            </thead>
            <tbody>
                {bug_rows}
            </tbody>
        </table>
    </section>

    <section class="section">
        <h2>Execution Paths</h2>
        <ul>
            {coverage_rows}
        </ul>
    </section>

    <section class="section">
        <h2>AI Repair</h2>
        <p><strong>Status:</strong> {self._escape_html(repair_status)}</p>
        {suggested_code_block}
    </section>
</body>
</html>
"""

    def _escape_html(self, value: str) -> str:
        replacements = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
        }
        escaped = value or ""
        for key, replacement in replacements.items():
            escaped = escaped.replace(key, replacement)
        return escaped


def save_html_report(html_content: str, output_path: str | Path) -> Path:
    """Persist the generated HTML to disk."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_content, encoding="utf-8")
    return path

