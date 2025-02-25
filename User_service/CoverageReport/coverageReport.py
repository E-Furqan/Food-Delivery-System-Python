# import coverage
# import sys
# import inspect
# import time
# import threading
# import os
#
#
# from Utils.utils import function_lines_cache,CLEANUP_INTERVAL,coverage_data,TIME_WINDOW,source_dirs
#
# coverage_lock = threading.Lock()
#
#
#
#
# # def cache_function_lines():
# #     PROJECT_DIR = os.getcwd()
# #     for module_name, module in sys.modules.items():
# #         if hasattr(module, "__file__") and module.__file__:
# #             # Check if the module is inside the project directory (not a system or third-party module)
# #             if module.__file__.startswith(PROJECT_DIR):
# #                 print(module_name, module.__file__)
#
#
# def cache_function_lines():
#     """Precompute function line numbers for user-written modules."""
#     project_root = os.getcwd()  # Adjust if necessary
#
#     for module_name, module in sys.modules.items():
#         if not module_name or not hasattr(module, "__file__"):
#             continue  # Skip built-in and dynamically loaded modules
#
#         module_path = module.__file__
#
#         if not module_path or not module_path.endswith(".py") or not module_path.startswith(project_root):
#             continue  # Ensure it's a user module in the project directory
#
#         function_lines_cache[module_name] = {}
#
#         for name, obj in inspect.getmembers(module, inspect.isfunction):
#             if inspect.getmodule(obj) == module:
#                 source_lines, start_line = inspect.getsourcelines(obj)
#                 function_lines_cache[module_name][name] = set(range(start_line, start_line + len(source_lines)))
#
#     print( function_lines_cache)
#
#
#
#
# def cleanup_old_data():
#     """ Periodically removes data older than 1 hour. """
#     while True:
#         time.sleep(CLEANUP_INTERVAL)
#         cutoff_time = time.time() - TIME_WINDOW
#
#         for endpoint in list(coverage_data.keys()):
#             for file in list(coverage_data[endpoint].keys()):
#                 _, timestamp = coverage_data[endpoint][file]
#                 if timestamp < cutoff_time:
#                     del coverage_data[endpoint][file]
#
#             if not coverage_data[endpoint]:
#                 del coverage_data[endpoint]
#
