from functools import wraps
import inspect
import os
from fastapi import Request
from coverage_tracker import tracker

def track_coverage(func):
    sig = inspect.signature(func)

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        request = next((arg for arg in args if isinstance(arg, Request)), None)
        if request is None:
            for param_name, param in sig.parameters.items():
                if param.annotation == Request and param_name in kwargs:
                    request = kwargs[param_name]
                    break
        # Use the Request URL if available, otherwise inherit from caller or use function name
        endpoint = f"{request.url.path}" if request else None
        caller = tracker.get_current_caller()
        if endpoint is None and caller:
            # Inherit the caller's URL-based endpoint if available
            for ep in tracker.coverage_data.keys():
                if ep.startswith("internal:/") and any(
                    call["function"] == caller for call in tracker.coverage_data[ep]
                ):
                    endpoint = ep.replace("internal:", "")
                    break
            if not endpoint:
                endpoint = func.__name__
        elif endpoint is None:
            endpoint = func.__name__
        print(f"Tracking function: {func.__name__}, Endpoint: {endpoint}, Caller: {caller}")  # Debug

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
            # Preserve the caller context across the call stack
            previous_caller = tracker.get_current_caller()
            tracker.set_current_caller(func.__name__)
            try:
                result = func(*args, **kwargs)
                print(f"Calling track_function for {func.__name__} with endpoint: internal:{endpoint}")  # Debug
                tracker.track_function(f"internal:{endpoint}", func.__name__, func, caller)
                return result
            except Exception as e:
                print(f"Exception in {func.__name__}: {e}")  # Debug
                tracker.track_function(f"internal:{endpoint}", func.__name__, func, caller)
                raise
            finally:
                tracker.set_current_caller(previous_caller)  # Restore previous caller instead of clearing
        else:
            return func(*args, **kwargs)

    sync_wrapper.__signature__ = sig
    return sync_wrapper