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

    def _load_data(self) -> Dict[str, List[dict]]:
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and all(isinstance(calls, list) for calls in data.values()):
                        return data
                    elif "coverage_report" in data:
                        return {endpoint: calls for endpoint, calls in data["coverage_report"].items()}
                    else:
                        print(f"Invalid format in {self.storage_file}, returning empty data")
                        return {}
            except json.JSONDecodeError:
                print(f"Error decoding {self.storage_file}, returning empty data")
                return {}
        return {}

    def _save_data(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.coverage_data, f, indent=4)

    def _get_function_body_lines(self, func_obj) -> List[int]:
        try:
            source_lines, start_line = inspect.getsourcelines(func_obj)
            body_lines = []
            in_body = False
            for i, line in enumerate(source_lines):
                stripped = line.strip()
                if not in_body and stripped and not stripped.startswith('@'):
                    in_body = True
                if in_body and stripped and not (stripped.startswith('#') or stripped.startswith('"""')):
                    body_lines.append(start_line + i)
            return body_lines
        except (TypeError, OSError) as e:
            print(f"Error getting body lines for {func_obj.__name__}: {e}")
            return []

    def track_function(self, endpoint: str, function_name: str, func_obj, caller: Optional[str] = None, cov=None):
        if cov is None:
            raise ValueError("Coverage object must be provided to track_function")
        cov.stop()
        cov.save()
        cov_data = cov.get_data()
        file_name = os.path.abspath(inspect.getfile(func_obj))
        all_lines = cov_data.lines(file_name) or set()
        body_lines = self._get_function_body_lines(func_obj)
        executed_lines = {line for line in all_lines if line in body_lines}
        raw_data = {
            "function": function_name,
            "timestamp": datetime.now().isoformat(),
            "total_lines": len(body_lines),
            "executed_lines": len(executed_lines),
            "source_file": file_name,
            "caller": caller
        }
        self.coverage_data.setdefault(endpoint, []).append(raw_data)
        self._save_data()

    def get_hourly_report(self) -> Dict:
        one_hour_ago = datetime.now() - timedelta(hours=1)
        report = {}

        # Process each endpoint
        for endpoint, calls in self.coverage_data.items():
            if not endpoint.startswith("internal:/"):
                continue  # Skip non-URL endpoints
            recent_calls = [c for c in calls if datetime.fromisoformat(c["timestamp"]) >= one_hour_ago]
            if not recent_calls:
                continue

            call_entries = []
            top_level_calls = [c for c in recent_calls if c["caller"] is None]
            for top_call in top_level_calls:
                func_name = top_call["function"]
                # Build nested functions specific to this call's timestamp
                nested_funcs = self._build_nested_functions(func_name, top_call["timestamp"])
                functions_dict = {
                    func_name: {
                        "function_total_lines": top_call["total_lines"],
                        "function_executed_lines": top_call["executed_lines"],
                        "coverage_percentage": round(
                            (top_call["executed_lines"] / top_call["total_lines"]) * 100, 2
                        ) if top_call["total_lines"] > 0 else 0,
                        "source_file": top_call["source_file"],
                        "functions": nested_funcs
                    }
                }
                agg_total, agg_executed = self._calculate_aggregate_metrics(functions_dict)
                call_entry = {
                    "timestamp": top_call["timestamp"],
                    "total_lines": agg_total,
                    "executed_lines": agg_executed,
                    "coverage_percentage": round((agg_executed / agg_total) * 100, 2) if agg_total > 0 else 0,
                    "functions": functions_dict
                }
                call_entries.append(call_entry)
            if call_entries:
                report[endpoint] = call_entries

        final_report = {
            "coverage_report": report,
            "period": "last_hour",
            "timestamp": datetime.now().isoformat()
        }
        return final_report

    def _calculate_aggregate_metrics(self, functions_dict: Dict) -> tuple[int, int]:
        total_lines = 0
        executed_lines = 0
        for func_info in functions_dict.values():
            total_lines += func_info["function_total_lines"]
            executed_lines += func_info["function_executed_lines"]
            if "functions" in func_info:
                nested_total, nested_executed = self._calculate_aggregate_metrics(func_info["functions"])
                total_lines += nested_total
                executed_lines += nested_executed
        return total_lines, executed_lines

    def _build_nested_functions(self, func_name: str, top_call_timestamp: str, visited: set = None) -> Dict:
        if visited is None:
            visited = set()
        if func_name in visited:
            return {}  # Avoid infinite recursion
        visited.add(func_name)
        nested = {}

        # Find calls where this function is the caller, closest to the top-level timestamp
        for endpoint, calls in self.coverage_data.items():
            for call in calls:
                if call.get("caller") == func_name:
                    call_time = datetime.fromisoformat(call["timestamp"])
                    top_time = datetime.fromisoformat(top_call_timestamp)
                    # Use calls within a small time window of the top-level call
                    if abs((call_time - top_time).total_seconds()) < 1:  # 1-second tolerance
                        nested_func_name = call["function"]
                        nested[nested_func_name] = {
                            "function_total_lines": call["total_lines"],
                            "function_executed_lines": call["executed_lines"],
                            "coverage_percentage": round(
                                (call["executed_lines"] / call["total_lines"]) * 100, 2
                            ) if call["total_lines"] > 0 else 0,
                            "source_file": call["source_file"],
                            "functions": self._build_nested_functions(nested_func_name, top_call_timestamp, visited)
                        }
        visited.remove(func_name)
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
            endpoint: [call for call in calls if datetime.fromisoformat(call["timestamp"]) >= one_hour_ago]
            for endpoint, calls in self.coverage_data.items()
        }
        self.coverage_data = {k: v for k, v in self.coverage_data.items() if v}
        self._save_data()

tracker = CoverageTracker()