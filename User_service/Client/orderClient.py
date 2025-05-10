import requests

from Schemas import schemas
from EnviornmentVariable import enVVar

def update_order_status(payload: schemas.order_payload, token: str):
    """Send a request to update order status."""
    url = enVVar.UPDATE_ORDER_STATUS_URL
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.put(url, json=payload.dict(), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        raise Exception(f"HTTP error occurred: {http_err}")
    except Exception as err:
        raise Exception(f"Failed to update order status: {err}")

