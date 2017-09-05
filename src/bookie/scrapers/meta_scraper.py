import typing
from bookie.scrapers import bookmob
from bookie.scrapers import bookscouter
from bookie.scrapers import queens


def get_resale_prices(isbn: str) -> typing.Dict[str, typing.Optional[str]]:
    return {
        'BookMob': bookmob.get_resale_price(isbn),
        "Queen's": queens.get_resale_price(isbn),
        'BookScouter': bookscouter.get_resale_price(isbn),
    }
