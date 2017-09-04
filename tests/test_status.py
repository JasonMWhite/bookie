import flask.testing


def test_status_ok(client: flask.testing.FlaskClient) -> None:
    res = client.get('/_ah/health')
    assert res.status_code == 200
