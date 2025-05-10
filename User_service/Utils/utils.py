from Schemas import schemas
from collections import defaultdict
from typing import Dict, Set, Tuple

def create_token_payload_obj(id : int, role_type : str):
    payload=schemas.auth_payload(id=id,role=role_type)
    return  payload


def create_order_payload_obj(order_details:schemas.order_details,restaurant_id:int):
    payload = schemas.order_payload(id=restaurant_id,
                                    order_id=order_details.order_id,order_status=order_details.order_status)

    return payload


coverage_data: Dict[str, Dict[str, Dict[str, Tuple[Set[int], float]]]] = defaultdict(lambda: defaultdict(dict))
function_lines_cache: Dict[str, Dict[str, Set[int]]] = {}

CLEANUP_INTERVAL = 600
TIME_WINDOW = 3600

source_dirs = [
    "Client",
    "DatabaseConfig",
    "EnviornmentVariable",
    "Hashing",
    "MiddleWare",
    "Model",
    "Repository",
    "Routes",
    "Schemas",
    "Utils",
    "main.py"
]

