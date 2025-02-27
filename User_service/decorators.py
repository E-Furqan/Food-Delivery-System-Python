from functools import wraps
from datetime import datetime, timedelta
import inspect
import os
from fastapi import Request
from coverage_tracker import tracker
import coverage

def track_coverage(func):
    sig = inspect.signature(func)
    def _get_end_point_caller(*args, **kwargs):
        request = next((arg for arg in args if isinstance(arg, Request)), None)
        if request is None:
            for param_name, param in sig.parameters.items():
                if param.annotation == Request and param_name in kwargs:
                    request = kwargs[param_name]
                    break
        endpoint = f"{request.url.path}" if request else None
        caller = tracker.get_current_caller()
        if endpoint is None and caller:
            # Check raw data format in coverage_data
            for ep in tracker.coverage_data.keys():
                if ep.startswith("internal:/") and any(
                        call.get("function") == caller for call in tracker.coverage_data[ep]
                ):
                    endpoint = ep.replace("internal:", "")
                    break
            if not endpoint:
                endpoint = func.__name__
        elif endpoint is None:
            endpoint = func.__name__
        print(f"Tracking function: {func.__name__}, Endpoint: {endpoint}, Caller: {caller}")  # Debug
        return endpoint, caller

    # Synchronous wrapper
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        endpoint, caller = _get_end_point_caller(*args, **kwargs)
        try:
            module_file_path = inspect.getfile(func)
        except TypeError:
            print(f"Could not get file for {func.__name__}")
            return func(*args, **kwargs)

        site_packages_path = os.path.realpath(__file__).split('site-packages')[0]
        is_user_defined = not any(
            module_file_path.startswith(path_prefix)
            for path_prefix in ['/usr/lib', '/lib', site_packages_path]
        )

        if is_user_defined:
            cov = coverage.Coverage(
                source=["/home/emumba/Emumba/Python/Food Delivery System/User_service"],
                omit=["*/site-packages/*", "*/tests/*"]
            )
            cov.start()

            previous_caller = tracker.get_current_caller()
            tracker.set_current_caller(func.__name__)
            try:
                result = func(*args, **kwargs)
                cov.stop()
                cov.save()
                cov_data = cov.get_data()
                file_name = os.path.abspath(inspect.getfile(func))
                all_lines = cov_data.lines(file_name) or set()
                print(f"All executed lines for {file_name}: {all_lines}")
                body_lines = tracker._get_function_body_lines(func)
                print(f"Function {func.__name__} body lines: {body_lines}")
                executed_lines = {line for line in all_lines if line in body_lines}

                tracker.coverage_data.setdefault(f"internal:{endpoint}", []).append({
                    "function": func.__name__,
                    "timestamp": datetime.now().isoformat(),
                    "total_lines": len(body_lines),
                    "executed_lines": len(executed_lines),
                    "source_file": file_name,
                    "caller": caller
                })
                print(f"Tracked: {endpoint} - {func.__name__}, Lines: {len(body_lines)}, Executed: {len(executed_lines)}")
                tracker._save_data()
                return result
            except Exception as e:
                cov.stop()
                cov.save()
                cov_data = cov.get_data()
                file_name = os.path.abspath(inspect.getfile(func))
                all_lines = cov_data.lines(file_name) or set()
                print(f"All executed lines for {file_name}: {all_lines}")
                body_lines = tracker._get_function_body_lines(func)
                print(f"Function {func.__name__} body lines: {body_lines}")
                executed_lines = {line for line in all_lines if line in body_lines}

                tracker.coverage_data.setdefault(f"internal:{endpoint}", []).append({
                    "function": func.__name__,
                    "timestamp": datetime.now().isoformat(),
                    "total_lines": len(body_lines),
                    "executed_lines": len(executed_lines),
                    "source_file": file_name,
                    "caller": caller
                })
                print(f"Tracked: {endpoint} - {func.__name__}, Lines: {len(body_lines)}, Executed: {len(executed_lines)}")
                tracker._save_data()
                raise
            finally:
                tracker.set_current_caller(previous_caller)
        else:
            return func(*args, **kwargs)

    # Asynchronous wrapper
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        endpoint, caller = _get_end_point_caller(*args, **kwargs)

        try:
            module_file_path = inspect.getfile(func)
        except TypeError:
            print(f"Could not get file for {func.__name__}")
            return await func(*args, **kwargs)

        site_packages_path = os.path.realpath(__file__).split('site-packages')[0]
        is_user_defined = not any(
            module_file_path.startswith(path_prefix)
            for path_prefix in ['/usr/lib', '/lib', site_packages_path]
        )

        if is_user_defined:
            cov = coverage.Coverage(
                source=["/home/emumba/Emumba/Python/Food Delivery System/User_service"],
                omit=["*/site-packages/*", "*/tests/*"]
            )
            cov.start()

            previous_caller = tracker.get_current_caller()
            tracker.set_current_caller(func.__name__)
            try:
                result = await func(*args, **kwargs)
                cov.stop()
                cov.save()
                cov_data = cov.get_data()
                file_name = os.path.abspath(inspect.getfile(func))
                all_lines = cov_data.lines(file_name) or set()
                print(f"All executed lines for {file_name}: {all_lines}")
                body_lines = tracker._get_function_body_lines(func)
                print(f"Function {func.__name__} body lines: {body_lines}")
                executed_lines = {line for line in all_lines if line in body_lines}

                tracker.coverage_data.setdefault(f"internal:{endpoint}", []).append({
                    "function": func.__name__,
                    "timestamp": datetime.now().isoformat(),
                    "total_lines": len(body_lines),
                    "executed_lines": len(executed_lines),
                    "source_file": file_name,
                    "caller": caller
                })
                print(f"Tracked: {endpoint} - {func.__name__}, Lines: {len(body_lines)}, Executed: {len(executed_lines)}")
                tracker._save_data()
                return result
            except Exception as e:
                cov.stop()
                cov.save()
                cov_data = cov.get_data()
                file_name = os.path.abspath(inspect.getfile(func))
                all_lines = cov_data.lines(file_name) or set()
                print(f"All executed lines for {file_name}: {all_lines}")
                body_lines = tracker._get_function_body_lines(func)
                print(f"Function {func.__name__} body lines: {body_lines}")
                executed_lines = {line for line in all_lines if line in body_lines}

                tracker.coverage_data.setdefault(f"internal:{endpoint}", []).append({
                    "function": func.__name__,
                    "timestamp": datetime.now().isoformat(),
                    "total_lines": len(body_lines),
                    "executed_lines": len(executed_lines),
                    "source_file": file_name,
                    "caller": caller
                })
                print(f"Tracked: {endpoint} - {func.__name__}, Lines: {len(body_lines)}, Executed: {len(executed_lines)}")
                tracker._save_data()
                raise
            finally:
                tracker.set_current_caller(previous_caller)
        else:
            return await func(*args, **kwargs)

    if inspect.iscoroutinefunction(func):
        async_wrapper.__signature__ = sig
        return async_wrapper
    else:
        sync_wrapper.__signature__ = sig
        return sync_wrapper