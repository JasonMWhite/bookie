def test_status_ok(client):
    res = client.get('/_ah/health')
    assert res.status_code == 200
