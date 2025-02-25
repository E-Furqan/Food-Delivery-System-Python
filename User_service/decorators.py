from functools import wraps
from fastapi import Request
from coverage_tracker import tracker
import inspect
import os
from typing import Optional

def track_coverage(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = next((arg for arg in args if isinstance(arg, Request)), None)
        endpoint = request.url.path if request else f"internal:{func.__name__}"

        try:
            module_file_path = inspect.getfile(func)
        except TypeError:
            return await func(*args, **kwargs)

        site_packages_path = os.path.realpath(__file__).split('site-packages')[0]
        is_user_defined = not any(
            module_file_path.startswith(path_prefix)
            for path_prefix in ['/usr/lib', '/lib', site_packages_path]
        )

        if is_user_defined:
            # Pass the current function as the caller to track hierarchy
            caller = tracker.get_current_caller()
            tracker.track_function(endpoint, func.__name__, func, caller)

        # Set this function as the current caller for nested calls
        tracker.set_current_caller(func.__name__)
        result = await func(*args, **kwargs)
        tracker.clear_current_caller()

        return result
    return wrapper