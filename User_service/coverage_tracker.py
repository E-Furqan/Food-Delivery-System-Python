from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import os
import coverage
import inspect

class CoverageTracker:
    def __init__(self):
        """Initialize the CoverageTracker with a storage file and load existing raw call data."""
        self.storage_file = "coverage_data.json"
        self.coverage_data: Dict[str, List[dict]] = self._load_data()
        self.current_caller: Optional[str] = None

    def _load_data(self) -> Dict[str, List[dict]]:
        """Load raw coverage call data from the storage file, ensuring the correct format."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    # Check for raw data format (direct endpoint: calls mapping)
                    if isinstance(data, dict) and all(isinstance(calls, list) for calls in data.values()):
                        return data
                    # If structured format, extract raw data from coverage_report
                    elif "coverage_report" in data:
                        return {
                            endpoint: calls
                            for endpoint, calls in data["coverage_report"].items()
                        }
                    else:
                        print(f"Invalid format in {self.storage_file}, returning empty data")
                        return {}
            except json.JSONDecodeError:
                print(f"Error decoding {self.storage_file}, returning empty data")
                return {}
        return {}

    def _save_data(self):
        """Save raw coverage call data to the storage file, maintaining compatibility."""
        # Save raw data directly
        with open(self.storage_file, 'w') as f:
            json.dump(self.coverage_data, f, indent=4)

    def _get_function_body_lines(self, func_obj) -> List[int]:
        """Extract executable line numbers from a function's source code."""
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
            print(f"Function {func_obj.__name__} body lines: {body_lines}")
            return body_lines
        except (TypeError, OSError) as e:
            print(f"Error getting body lines for {func_obj.__name__}: {e}")
            return []

    def track_function(self, endpoint: str, function_name: str, func_obj, caller: Optional[str] = None, cov=None):
        """Track and store raw coverage data for a function execution."""
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
        print(f"Tracked raw: {endpoint} - {function_name}, Lines: {len(body_lines)}, Executed: {len(executed_lines)}")
        self._save_data()

    def get_hourly_report(self) -> Dict:
        """Generate a structured report of coverage data for the last hour, focusing on URL-based endpoints."""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        report = {}
        function_data = {}

        # Build function data with caller relationships from raw data
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
                        "callers": set(),
                        "calls": []
                    }
                function_data[func_name]["calls"].append(call)
                if caller:
                    function_data[func_name]["callers"].add(caller)

        # Generate structured report only for URL-based endpoints
        for endpoint, calls in self.coverage_data.items():
            if not endpoint.startswith("internal:/"):
                print(f"Skipping endpoint: {endpoint} (not a URL-based endpoint)")
                continue

            recent_calls = [c for c in calls if datetime.fromisoformat(c["timestamp"]) >= one_hour_ago]
            if not recent_calls:
                print(f"No recent calls for {endpoint}")
                continue

            call_entries = []
            top_level_calls = [c for c in recent_calls if c["caller"] is None]
            for top_call in top_level_calls:
                func_name = top_call["function"]
                func_info = function_data[func_name]
                nested_calls = [
                    c for c in recent_calls
                    if c["caller"] == func_name and
                       datetime.fromisoformat(c["timestamp"]) <= datetime.fromisoformat(
                        top_call["timestamp"]) + timedelta(seconds=1)
                ]
                nested_funcs = {}
                if nested_calls:
                    closest_nested = max(nested_calls, key=lambda x: datetime.fromisoformat(x["timestamp"]))
                    nested_func_name = closest_nested["function"]
                    nested_info = function_data[nested_func_name]
                    nested_funcs[nested_func_name] = {
                        "function_total_lines": closest_nested["total_lines"],
                        "function_executed_lines": closest_nested["executed_lines"],
                        "coverage_percentage": round(
                            (closest_nested["executed_lines"] / closest_nested["total_lines"]) * 100, 2
                        ) if closest_nested["total_lines"] > 0 else 0,
                        "source_file": closest_nested["source_file"],
                        "functions": self._build_nested_functions(nested_func_name, function_data)
                    }

                # Use specific call data for aggregation
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
        """Calculate aggregate total and executed lines from a functions dictionary."""
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

    def _aggregate_metrics(self, func_name: str, function_data: Dict, visited: set = None) -> tuple[int, int]:
        """Calculate aggregate total and executed lines for a function and its nested calls (unused, but kept for reference)."""
        if visited is None:
            visited = set()
        if func_name in visited:
            return 0, 0
        visited.add(func_name)

        total_lines = function_data[func_name]["total_lines"]
        executed_lines = function_data[func_name]["executed_lines"]

        for called_func, info in function_data.items():
            if func_name in info["callers"]:
                nested_total, nested_executed = self._aggregate_metrics(called_func, function_data, visited)
                total_lines += nested_total
                executed_lines += nested_executed

        visited.remove(func_name)
        return total_lines, executed_lines

    def _build_nested_functions(self, func_name: str, function_data: Dict, visited: set = None) -> Dict:
        """Construct a nested structure of functions called by the given function."""
        if visited is None:
            visited = set()
        if func_name in visited:
            return {}
        visited.add(func_name)

        nested = {}
        for called_func, info in function_data.items():
            if func_name in info["callers"]:
                nested[called_func] = {
                    "function_total_lines": info["total_lines"],
                    "function_executed_lines": info["executed_lines"],
                    "coverage_percentage": round((info["executed_lines"] / info["total_lines"]) * 100, 2)
                    if info["total_lines"] > 0 else 0,
                    "source_file": info["source_file"],
                    "functions": self._build_nested_functions(called_func, function_data, visited)
                }
        visited.remove(func_name)
        return nested

    def set_current_caller(self, caller: str):
        """Set the current caller context for tracking nested calls."""
        self.current_caller = caller

    def get_current_caller(self) -> Optional[str]:
        """Get the current caller context."""
        return self.current_caller

    def clear_current_caller(self):
        """Clear the current caller context."""
        self.current_caller = None

    def cleanup_old_data(self):
        """Remove coverage data older than one hour and save the updated raw data."""
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