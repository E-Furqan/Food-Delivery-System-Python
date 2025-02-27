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
        # No global self.cov anymore

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
                if not in_body and stripped and not stripped.startswith('@'):
                    in_body = True
                if in_body and stripped and not stripped.startswith('#') and not stripped.startswith('"""'):
                    body_lines.append(start_line + i)
            print(f"Function {func_obj.__name__} body lines: {body_lines}")
            return body_lines
        except (TypeError, OSError) as e:
            print(f"Error getting body lines for {func_obj.__name__}: {e}")
            return []

    def track_function(self, endpoint: str, function_name: str, func_obj, caller: Optional[str] = None, cov=None):
        current_time = datetime.now().isoformat()
        if endpoint not in self.coverage_data:
            self.coverage_data[endpoint] = []

        if cov is None:
            raise ValueError("Coverage object must be provided to track_function")

        # Stop coverage and get data for this specific call
        cov.stop()
        cov.save()
        cov_data = cov.get_data()
        file_name = os.path.abspath(inspect.getfile(func_obj))
        executed_lines = cov_data.lines(file_name) or set()
        all_lines = cov_data.lines(file_name) or set()
        print(f"All executed lines for {file_name}: {all_lines}")
        print(f"Executed lines for {file_name}: {executed_lines}")  # Debug

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
        print(f"Tracked: {endpoint} - {function_name}, Lines: {len(body_lines)}, Executed: {len(func_executed_lines)}")  # Debug
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
                        "callers": set(),
                        "calls": []  # Store all calls for this function
                    }
                function_data[func_name]["calls"].append(call)
                if caller:
                    function_data[func_name]["callers"].add(caller)

        # Generate report only for URL-based endpoints
        for endpoint, calls in self.coverage_data.items():
            if not endpoint.startswith("internal:/"):
                print(f"Skipping endpoint: {endpoint} (not a URL-based endpoint)")  # Debug
                continue

            recent_calls = [c for c in calls if datetime.fromisoformat(c["timestamp"]) >= one_hour_ago]
            if not recent_calls:
                print(f"No recent calls for {endpoint}")  # Debug
                continue

            call_entries = []
            # Process top-level calls (createUserEndpoint)
            top_level_calls = [c for c in recent_calls if c["caller"] is None]
            for top_call in top_level_calls:
                func_name = top_call["function"]
                func_info = function_data[func_name]
                # Find the closest nested call (createUser) by timestamp
                nested_calls = [
                    c for c in recent_calls
                    if c["caller"] == func_name and
                       datetime.fromisoformat(c["timestamp"]) <= datetime.fromisoformat(
                        top_call["timestamp"]) + timedelta(seconds=1)
                ]
                nested_funcs = {}
                if nested_calls:
                    # Take the most recent nested call within 1 second
                    closest_nested = max(nested_calls, key=lambda x: datetime.fromisoformat(x["timestamp"]))
                    nested_func_name = closest_nested["function"]
                    nested_info = function_data[nested_func_name]
                    nested_funcs[nested_func_name] = {
                        "total_lines": closest_nested["total_lines"],
                        "executed_lines": closest_nested["executed_lines"],
                        "coverage_percentage": round(
                            (closest_nested["executed_lines"] / closest_nested["total_lines"]) * 100, 2
                        ) if closest_nested["total_lines"] > 0 else 0,
                        "source_file": closest_nested["source_file"],
                        "functions": self._build_nested_functions(nested_func_name, function_data)
                    }

                agg_total, agg_executed = self._aggregate_metrics(func_name, function_data)
                call_entry = {
                    "timestamp": top_call["timestamp"],
                    "total_lines": agg_total,
                    "executed_lines": agg_executed,
                    "coverage_percentage": round((agg_executed / agg_total) * 100, 2) if agg_total > 0 else 0,
                    "functions": {
                        func_name: {
                            "total_lines": top_call["total_lines"],
                            "executed_lines": top_call["executed_lines"],
                            "coverage_percentage": round(
                                (top_call["executed_lines"] / top_call["total_lines"]) * 100, 2
                            ) if top_call["total_lines"] > 0 else 0,
                            "source_file": top_call["source_file"],
                            "functions": nested_funcs
                        }
                    }
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
    def _aggregate_metrics(self, func_name: str, function_data: Dict, visited: set = None) -> tuple[int, int]:
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
        if visited is None:
            visited = set()
        if func_name in visited:
            return {}
        visited.add(func_name)

        nested = {}
        for called_func, info in function_data.items():
            if func_name in info["callers"]:
                nested[called_func] = {
                    "total_lines": info["total_lines"],
                    "executed_lines": info["executed_lines"],
                    "coverage_percentage": round((info["executed_lines"] / info["total_lines"]) * 100, 2)
                    if info["total_lines"] > 0 else 0,
                    "source_file": info["source_file"],
                    "functions": self._build_nested_functions(called_func, function_data, visited)
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
            endpoint: [
                call for call in calls
                if datetime.fromisoformat(call["timestamp"]) >= one_hour_ago
            ]
            for endpoint, calls in self.coverage_data.items()
        }
        self.coverage_data = {k: v for k, v in self.coverage_data.items() if v}
        self._save_data()

tracker = CoverageTracker()