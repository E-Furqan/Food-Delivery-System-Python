from functools import wraps
import inspect
import os
import asyncio
from fastapi import Request
from coverage_tracker import tracker


def track_coverage(func):
    # Get the original function's signature
    sig = inspect.signature(func)

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Extract endpoint from the Request object if present
        request = next((arg for arg in args if isinstance(arg, Request)), None)
        endpoint = request.url.path if request else f"internal:{func.__name__}"

        try:
            module_file_path = inspect.getfile(func)
        except TypeError:
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

        site_packages_path = os.path.realpath(__file__).split('site-packages')[0]
        is_user_defined = not any(
            module_file_path.startswith(path_prefix)
            for path_prefix in ['/usr/lib', '/lib', site_packages_path]
        )

        if is_user_defined:
            caller = tracker.get_current_caller()
            tracker.set_current_caller(func.__name__)
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            tracker.track_function(endpoint, func.__name__, func, caller)
            tracker.clear_current_caller()
        else:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        # Extract endpoint from the Request object if present
        request = next((arg for arg in args if isinstance(arg, Request)), None)
        endpoint = request.url.path if request else f"internal:{func.__name__}"

        try:
            module_file_path = inspect.getfile(func)
        except TypeError:
            return func(*args, **kwargs)

        site_packages_path = os.path.realpath(__file__).split('site-packages')[0]
        is_user_defined = not any(
            module_file_path.startswith(path_prefix)
            for path_prefix in ['/usr/lib', '/lib', site_packages_path]
        )

        if is_user_defined:
            caller = tracker.get_current_caller()
            tracker.set_current_caller(func.__name__)
            result = func(*args, **kwargs)
            tracker.track_function(endpoint, func.__name__, func, caller)
            tracker.clear_current_caller()
        else:
            result = func(*args, **kwargs)

        return result

    # Bind the signature to the wrapper to preserve parameter names for FastAPI
    async_wrapper.__signature__ = sig
    sync_wrapper.__signature__ = sig

    # Return the appropriate wrapper based on whether the function is async
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper