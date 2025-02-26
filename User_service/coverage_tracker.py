from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import os
import coverage
import inspect

class CoverageTracker:
    def __init__(self):
        self.storage_file = "coverage_data.json"
        self.coverage_data: Dict[str, List[dict]] = self._load_data()
        self.current_caller: Optional[str] = None
        self.cov = coverage.Coverage(source=["."], omit=["*/site-packages/*", "*/tests/*"])
        self.cov.start()

    def _load_data(self) -> Dict[str, List[dict]]:
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                for endpoint, calls in data.items():
                    data[endpoint] = [
                        call for call in calls
                        if "function" in call and "timestamp" in call and "total_lines" in call
                    ]
                return data
        return {}

    def _save_data(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.coverage_data, f)

    def _get_function_body_lines(self, func_obj) -> List[int]:
        try:
            source_lines, start_line = inspect.getsourcelines(func_obj)
            body_lines = []
            in_body = False
            for i, line in enumerate(source_lines):
                stripped = line.strip()
                if not in_body and line.startswith(" "):
                    in_body = True
                if in_body and stripped and not stripped.startswith('#') and not stripped.startswith('"""'):
                    body_lines.append(start_line + i - 1)
            return body_lines
        except (TypeError, OSError):
            return []

    def track_function(self, endpoint: str, function_name: str, func_obj, caller: Optional[str] = None):
        current_time = datetime.now().isoformat()
        if endpoint not in self.coverage_data:
            self.coverage_data[endpoint] = []

        self.cov.save()
        cov_data = self.cov.get_data()
        file_name = os.path.abspath(inspect.getfile(func_obj))
        executed_lines = cov_data.lines(file_name) or set()

        body_lines = self._get_function_body_lines(func_obj)
        func_executed_lines = {line for line in executed_lines if line in body_lines}

        self.coverage_data[endpoint].append({
            "function": function_name,
            "timestamp": current_time,
            "total_lines": len(body_lines),
            "executed_lines": len(func_executed_lines),
            "source_file": file_name,
            "caller": caller
        })
        self._save_data()

    def get_hourly_report(self) -> Dict:
        one_hour_ago = datetime.now() - timedelta(hours=1)
        report = {}
        function_data = {}

        # Build function data with caller relationships
        for endpoint, calls in self.coverage_data.items():
            recent_calls = [
                call for call in calls
                if datetime.fromisoformat(call["timestamp"]) >= one_hour_ago
            ]
            for call in recent_calls:
                func_name = call["function"]
                caller = call.get("caller")
                executed_lines = call.get("executed_lines", 0)
                if func_name not in function_data:
                    function_data[func_name] = {
                        "total_lines": call["total_lines"],
                        "executed_lines": executed_lines,
                        "source_file": call["source_file"],
                        "endpoint": endpoint,
                        "callers": set()
                    }
                if caller:
                    function_data[func_name]["callers"].add(caller)

        # Generate report with aggregated metrics
        for endpoint, calls in self.coverage_data.items():
            recent_calls = [c for c in calls if datetime.fromisoformat(c["timestamp"]) >= one_hour_ago]
            if not recent_calls:
                continue

            top_level_funcs = {call["function"] for call in recent_calls if not function_data[call["function"]]["callers"]}
            if not top_level_funcs:
                continue

            functions = {}
            total_lines = 0
            executed_lines = 0

            for func in top_level_funcs:
                func_info = function_data[func]
                nested_funcs = self._build_nested_functions(func, function_data)

                # Aggregate totals recursively
                agg_total, agg_executed = self._aggregate_metrics(func, function_data)
                total_lines += agg_total
                executed_lines += agg_executed

                functions[func] = {
                    "total_lines": func_info["total_lines"],
                    "executed_lines": func_info["executed_lines"],
                    "coverage_percentage": round((func_info["executed_lines"] / func_info["total_lines"]) * 100, 2)
                    if func_info["total_lines"] > 0 else 0,
                    "source_file": func_info["source_file"],
                    "functions": nested_funcs
                }

            report[endpoint] = {
                "total_lines": total_lines,
                "executed_lines": executed_lines,
                "coverage_percentage": round((executed_lines / total_lines) * 100, 2) if total_lines > 0 else 0,
                "functions": functions
            }

        return report

    def _aggregate_metrics(self, func_name: str, function_data: Dict) -> tuple[int, int]:
        """Recursively aggregate total_lines and executed_lines for a function and its nested calls."""
        total_lines = function_data[func_name]["total_lines"]
        executed_lines = function_data[func_name]["executed_lines"]

        for called_func, info in function_data.items():
            if func_name in info["callers"]:
                nested_total, nested_executed = self._aggregate_metrics(called_func, function_data)
                total_lines += nested_total
                executed_lines += nested_executed

        return total_lines, executed_lines

    def _build_nested_functions(self, func_name: str, function_data: Dict) -> Dict:
        nested = {}
        for called_func, info in function_data.items():
            if func_name in info["callers"]:
                nested[called_func] = {
                    "total_lines": info["total_lines"],
                    "executed_lines": info["executed_lines"],
                    "coverage_percentage": round((info["executed_lines"] / info["total_lines"]) * 100, 2)
                    if info["total_lines"] > 0 else 0,
                    "source_file": info["source_file"],
                    "functions": self._build_nested_functions(called_func, function_data)
                }
        return nested

    def set_current_caller(self, caller: str):
        self.current_caller = caller

    def get_current_caller(self) -> Optional[str]:
        return self.current_caller

    def clear_current_caller(self):
        self.current_caller = None

    def cleanup_old_data(self):
        one_hour_ago = datetime.now() - timedelta(hours=1)
        self.coverage_data = {
            endpoint: [
                call for call in calls
                if datetime.fromisoformat(call["timestamp"]) >= one_hour_ago
            ]
            for endpoint, calls in self.coverage_data.items()
        }
        self.coverage_data = {k: v for k, v in self.coverage_data.items() if v}
        self._save_data()

    def stop_coverage(self):
        self.cov.stop()
        self.cov.save()

tracker = CoverageTracker()