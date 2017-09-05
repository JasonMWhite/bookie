import requests
import typing
from lxml import html


BOOKSTORE_URL = 'https://www.campusbookstore.com/textbooks/used-books/sell-used-books/results'
XPATH_LOCATION = '//article[a/@id="606"]//div[@class="bookboxwhite"]/font/strong'


def get_resale_price(isbn: str) -> typing.Optional[str]:
    res = requests.post(BOOKSTORE_URL, data={'isbn': isbn})
    tree: html.HtmlElement = html.fromstring(res.content)
    price_nodes: typing.List[html.Element] = tree.xpath(XPATH_LOCATION)
    if price_nodes:
        return price_nodes[0].text_content().split('$')[1]
