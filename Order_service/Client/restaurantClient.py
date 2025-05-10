import requests
from Schemas import schemas
from EnviornmentVariable import enVVar


def fetch_item_prices(payload:schemas.orderd_items):
    url = enVVar.FETCH_ITEM_URL

    response = requests.post(url, json=payload.dict())


    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)