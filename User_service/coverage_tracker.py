from datetime import datetime, timedelta
import json
from typing import Dict, List
import os
import inspect

class CoverageTracker:
    def __init__(self):
        self.storage_file = "coverage_data.json"
        self.coverage_data: Dict[str, List[dict]] = self._load_data()

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
            # Count only executable lines (exclude empty lines and comments)
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

    def track_function(self, endpoint: str, function_name: str, func_obj):
        current_time = datetime.now().isoformat()

        if endpoint not in self.coverage_data:
            self.coverage_data[endpoint] = []

        func_info = self._get_function_info(func_obj)
        self.coverage_data[endpoint].append({
            "function": function_name,
            "timestamp": current_time,
            "total_lines": func_info["total_lines"],
            "source_file": func_info["source_file"]
        })
        self._save_data()

    def get_hourly_report(self) -> Dict:
        one_hour_ago = datetime.now() - timedelta(hours=1)
        report = {}

        for endpoint, calls in self.coverage_data.items():
            recent_calls = [
                call for call in calls
                if datetime.fromisoformat(call["timestamp"]) >= one_hour_ago
            ]
            if recent_calls:
                functions = {}
                for call in recent_calls:
                    func_name = call["function"]
                    if func_name not in functions:
                        source_file = call.get("source_file", "unknown")
                        total_lines = call.get("total_lines", 0)
                        functions[func_name] = {
                            "total_lines": total_lines,
                            "executed_lines": total_lines,  # Assuming full execution
                            "source_file": source_file
                        }

                total_lines = sum(f["total_lines"] for f in functions.values())
                executed_lines = sum(f["executed_lines"] for f in functions.values())

                report[endpoint] = {
                    "total_lines": total_lines,
                    "executed_lines": executed_lines,
                    "coverage_percentage": round((executed_lines / total_lines) * 100, 2) if total_lines > 0 else 0,
                    "functions": {
                        func_name: {
                            "total_lines": info["total_lines"],
                            "executed_lines": info["executed_lines"],
                            "coverage_percentage": round((info["executed_lines"] / info["total_lines"]) * 100, 2)
                            if info["total_lines"] > 0 else 0,
                            "source_file": info["source_file"]
                        }
                        for func_name, info in functions.items()
                    }
                }

        return report

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