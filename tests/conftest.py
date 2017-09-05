import typing
import _pytest.monkeypatch
import flask.testing
import mock
import pytest
from bookie import app_generator


@pytest.fixture
def app(monkeypatch: _pytest.monkeypatch.MonkeyPatch) -> flask.Flask:
    def _get_google_secrets() -> typing.Dict[str, str]:
        return {
            'GOOGLE_OAUTH2_CLIENT_ID': 'client_id',
            'GOOGLE_OAUTH2_CLIENT_SECRET': 'client_secret',
            'SECRET_KEY': 'secret_key',
        }
    monkeypatch.setattr(app_generator, '_get_google_secrets', _get_google_secrets)
    monkeypatch.setattr(app_generator, 'oauth', mock.Mock())

    return app_generator.create_app()
