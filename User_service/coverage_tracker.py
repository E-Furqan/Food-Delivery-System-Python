from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import os
import inspect

class CoverageTracker:
    def __init__(self):
        self.storage_file = "coverage_data.json"
        self.coverage_data: Dict[str, List[dict]] = self._load_data()
        self.current_caller: Optional[str] = None  # Track the current calling function

    def _load_data(self) -> Dict[str, List[dict]]:
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_data(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.coverage_data, f)

    def _get_function_info(self, func_obj) -> dict:
        try:
            source_lines, _ = inspect.getsourcelines(func_obj)
            executable_lines = [
                line.strip() for line in source_lines
                if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""')
            ]
            return {
                "total_lines": len(executable_lines),
                "source_file": inspect.getfile(func_obj)
            }
        except (TypeError, OSError):
            return {
                "total_lines": 0,
                "source_file": "unknown"
            }

    def set_current_caller(self, caller: str):
        self.current_caller = caller

    def get_current_caller(self) -> Optional[str]:
        return self.current_caller

    def clear_current_caller(self):
        self.current_caller = None

    def track_function(self, endpoint: str, function_name: str, func_obj, caller: Optional[str] = None):
        current_time = datetime.now().isoformat()

        if endpoint not in self.coverage_data:
            self.coverage_data[endpoint] = []

        func_info = self._get_function_info(func_obj)
        self.coverage_data[endpoint].append({
            "function": function_name,
            "timestamp": current_time,
            "total_lines": func_info["total_lines"],
            "source_file": func_info["source_file"],
            "caller": caller  # Record who called this function
        })
        self._save_data()

    def get_hourly_report(self) -> Dict:
        one_hour_ago = datetime.now() - timedelta(hours=1)
        report = {}

        # Build a mapping of functions to their callers and data
        function_data = {}
        for endpoint, calls in self.coverage_data.items():
            recent_calls = [
                call for call in calls
                if datetime.fromisoformat(call["timestamp"]) >= one_hour_ago
            ]
            for call in recent_calls:
                func_name = call["function"]
                caller = call.get("caller")
                if func_name not in function_data:
                    function_data[func_name] = {
                        "total_lines": call.get("total_lines", 0),
                        "executed_lines": call.get("total_lines", 0),
                        "source_file": call.get("source_file", "unknown"),
                        "endpoint": endpoint,
                        "callers": set()
                    }
                if caller:
                    function_data[func_name]["callers"].add(caller)

        # Construct the nested report
        for endpoint, calls in self.coverage_data.items():
            recent_calls = [
                call for call in calls
                if datetime.fromisoformat(call["timestamp"]) >= one_hour_ago
            ]
            if not recent_calls:
                continue

            # Only process top-level endpoints (those with no callers)
            top_level_funcs = {
                call["function"] for call in recent_calls
                if not function_data[call["function"]]["callers"]
            }
            if not top_level_funcs:
                continue

            functions = {}
            total_lines = 0
            executed_lines = 0

            for func in top_level_funcs:
                func_info = function_data[func]
                total_lines += func_info["total_lines"]
                executed_lines += func_info["executed_lines"]

                # Build nested functions
                nested_funcs = self._build_nested_functions(func, function_data)
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

tracker = CoverageTracker()