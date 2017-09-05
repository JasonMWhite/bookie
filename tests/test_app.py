import _pytest.monkeypatch
import flask
import flask.testing
import mock
from bookie import app_generator


def test_index(client: flask.testing.FlaskClient) -> None:
    res = client.get(flask.url_for('index'))
    assert res.status_code == 200


def test_search_unauthorized(client: flask.testing.FlaskClient) -> None:
    res = client.get(flask.url_for('search'))
    assert res.status_code == 401


def test_search(client: flask.testing.FlaskClient) -> None:
    with client.session_transaction() as sess:
        sess['user.email'] = 'me'

    res = client.get(flask.url_for('search'))
    assert res.status_code == 200


def test_search_isbn(client: flask.testing.FlaskClient, monkeypatch: _pytest.monkeypatch.MonkeyPatch) -> None:
    with client.session_transaction() as sess:
        sess['user.email'] = 'me'

    get_prices = mock.Mock()
    get_prices.return_value = {'Seller1': '100.00', 'Seller2': '99.00'}
    monkeypatch.setattr(app_generator.meta_scraper, 'get_resale_prices', get_prices)

    res = client.get(flask.url_for('search', isbn='1234'))
    assert res.status_code == 200
    assert get_prices.call_count == 1
