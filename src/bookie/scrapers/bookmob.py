import requests
import typing
from lxml import html

URL = 'https://www.bookmob.ca/actions/ajax/getSellPricing.php'


def get_resale_price(isbn: str) -> typing.Optional[str]:
    res = requests.post(URL, data={'ISBN': isbn})
    tree = html.fromstring(res.content)
    we_pay = tree.xpath('//dl[@class="we_pay"]')

    if we_pay:
        options = we_pay[0].getchildren()
        option_names = options[0::2]
        option_prices = options[1::2]

        for name, price in zip(option_names, option_prices):
            if 'Check/PayPal' in name.text_content():
                return price.text_content()[1:]
