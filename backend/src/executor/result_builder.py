from typing import List, Dict
import time
from .ktest_parser import parse_ktest, parse_klee_error
from .coverage_analyzer import CoverageAnalyzer
from pathlib import Path

class ResultBuilder:
    """
    Builds the standardized JSON output for Person 2 & 3
    Matches the API contract from work division
    """
    
    def build_analysis_result(
        self,
        source_file: str,
        klee_out_dir: str,
        paths: List[Dict],
        bugs: List[Dict],
        execution_time: float
    ) -> Dict:
        """
        Combines all data into unified format
        Ref: SRS Section 3.2 (Functional Requirements)
        """
        
        # Calculate coverage
        coverage_analyzer = CoverageAnalyzer()
        coverage_data = coverage_analyzer.calculate_coverage(klee_out_dir, source_file)
        
        # Link bugs to paths
        for bug in bugs:
            bug["path_id"] = self._find_bug_path(bug, paths)
        
        # Add coverage info to paths
        for path in paths:
            path["line_coverage"] = coverage_data["lines_covered"]
        
        result = {
            "program_name": Path(source_file).name,
            "total_paths": len(paths),
            "explored_paths": len(paths),
            "execution_time": round(execution_time, 2),
            "coverage_percentage": coverage_data["coverage_percentage"],
            "paths": paths,
            "bugs": bugs,
            "metadata": {
                "klee_output_dir": klee_out_dir,
                "total_lines": coverage_data["total_lines"],
                "lines_covered": coverage_data["lines_covered"]
            }
        }
        
        return result
    
    def _find_bug_path(self, bug: Dict, paths: List[Dict]) -> int:
        """
        Map bug to the path that triggered it
        Bug files are named like: test000003.div.err
        """
        bug_file = bug.get("file", "")
        
        # Extract test number from bug filename
        import re
        match = re.search(r'test(\d+)', bug_file)
        if match:
            test_num = int(match.group(1))
            # Find corresponding path
            for path in paths:
                if f"test{test_num:06d}" in path["test_name"]:
                    return path["path_id"]
        
        return 1  # Default to first path if not found