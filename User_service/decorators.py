from functools import wraps
from fastapi import Request
from coverage_tracker import tracker
import inspect
import os

def track_coverage(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get request object if present
        request = next((arg for arg in args if isinstance(arg, Request)), None)
        endpoint = request.url.path if request else f"internal:{func.__qualname__}"

        try:
            module_file_path = inspect.getfile(func)
        except TypeError:
            return await func(*args, **kwargs)

        # Check if function is user-defined
        site_packages_path = os.path.realpath(__file__).split('site-packages')[0]
        is_user_defined = not any(
            module_file_path.startswith(path_prefix)
            for path_prefix in ['/usr/lib', '/lib', site_packages_path]
        )

        if is_user_defined:
            tracker.track_function(endpoint, func.__name__, func)

        result = await func(*args, **kwargs)
        return result
    return wrapper