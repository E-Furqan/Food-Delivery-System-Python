# from fastapi import APIRouter
# from Utils.utils import TIME_WINDOW, coverage_data, function_lines_cache
# import time
# import os
#
# router = APIRouter(
#     prefix="/coverage",
#     tags=['Coverage_report']
# )
#
# def normalize_module_path(filepath, base_dir="/home/emumba/Emumba/Python/Food Delivery System/User_service"):
#     relative_path = os.path.relpath(filepath, base_dir)
#     module_path = relative_path.replace(os.sep, ".").rstrip(".py")
#     return module_path
#
#
#
#
# @router.get("/overall_report")
# def overall_coverage_report():
#     cutoff_time = time.time() - TIME_WINDOW
#     overall_report = {
#         "overall_report": {
#             "total_lines": 0,
#             "covered_lines": 0,
#             "missed_lines": 0,
#             "coverage_percentage": 0
#         },
#         "detailed_report": {}
#     }
#
#     for endpoint, files in coverage_data.items():
#         if endpoint not in overall_report["detailed_report"]:
#             overall_report["detailed_report"][endpoint] = {
#                 "total_lines": 0,
#                 "covered_lines": 0,
#                 "missed_lines": 0,
#                 "coverage_percentage": 0,
#                 "functions": {}
#             }
#
#         for file, (executed_lines, timestamp) in files.items():
#             if timestamp < cutoff_time:
#                 continue
#
#             module_name = normalize_module_path(file)
#             if module_name not in function_lines_cache:
#                 continue
#
#             function_details = {}
#             for func_name, func_lines in function_lines_cache[module_name].items():
#                 if func_name not in called_functions.get():
#                     continue  # Skip functions not called during the request
#
#                 hit_lines = func_lines & executed_lines
#                 covered_func_lines = len(hit_lines)
#                 total_func_lines = len(func_lines)
#                 missing_func_lines = total_func_lines - covered_func_lines
#
#                 if covered_func_lines > 0:
#                     function_details[func_name] = {
#                         "total_lines": total_func_lines,
#                         "covered_lines": covered_func_lines,
#                         "missing_lines": missing_func_lines,
#                         "coverage_percentage": round((covered_func_lines / total_func_lines) * 100, 2) if total_func_lines else 0
#                     }
#
#             if function_details:
#                 total_module_lines = sum(len(lines) for lines in function_lines_cache[module_name].values())
#                 covered_module_lines = sum(len(func_lines & executed_lines) for func_lines in function_lines_cache[module_name].values())
#                 missing_module_lines = total_module_lines - covered_module_lines
#
#                 overall_report["detailed_report"][endpoint]["total_lines"] += total_module_lines
#                 overall_report["detailed_report"][endpoint]["covered_lines"] += covered_module_lines
#                 overall_report["detailed_report"][endpoint]["missed_lines"] += missing_module_lines
#                 overall_report["detailed_report"][endpoint]["functions"].update(function_details)
#
#     total_lines = sum(endpoint_data["total_lines"] for endpoint_data in overall_report["detailed_report"].values())
#     covered_lines = sum(endpoint_data["covered_lines"] for endpoint_data in overall_report["detailed_report"].values())
#     missed_lines = total_lines - covered_lines
#     coverage_percentage = round((covered_lines / total_lines) * 100, 2) if total_lines else 0
#
#     overall_report["overall_report"]["total_lines"] = total_lines
#     overall_report["overall_report"]["covered_lines"] = covered_lines
#     overall_report["overall_report"]["missed_lines"] = missed_lines
#     overall_report["overall_report"]["coverage_percentage"] = coverage_percentage
#
#     return overall_report
