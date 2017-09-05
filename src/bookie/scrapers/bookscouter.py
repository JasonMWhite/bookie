import json
import typing
import requests

URL = 'https://api.bookscouter.com/v3/prices/sell/'


def get_resale_price(isbn: str) -> typing.Optional[str]:
    res = requests.get(URL + isbn)
    data = json.loads(res.content)
    if 'data' in data:
        return str(max([value['Price'] for value in data['data']['Prices']]))
    return None
