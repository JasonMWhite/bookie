import flask
import flask.testing


def test_index(client: flask.testing.FlaskClient) -> None:
    res = client.get(flask.url_for('index'))
    assert res.status_code == 200
