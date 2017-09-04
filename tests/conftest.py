import typing
import pytest
from bookie import app_generator


@pytest.fixture
def app(monkeypatch):
    def _get_google_secrets() -> typing.Dict[str, str]:
        return {
            'GOOGLE_OAUTH2_CLIENT_ID': 'client_id',
            'GOOGLE_OAUTH2_CLIENT_SECRET': 'client_secret'
        }
    monkeypatch.setattr(app_generator, '_get_google_secrets', _get_google_secrets)
    return app_generator.create_app()
