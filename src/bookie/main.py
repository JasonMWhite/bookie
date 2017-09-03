import json

import flask
import httplib2

from google.cloud import storage
from apiclient import discovery
from oauth2client import client
import tempfile

app = flask.Flask(__name__)


@app.route('/')
def index():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        drive = discovery.build('drive', 'v2', http_auth)
        files = drive.files().list().execute()
        return json.dumps(files)


SECRETS_FILENAME = 'client_secrets.json'


@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        SECRETS_FILENAME,
        scope='https://www.googleapis.com/auth/drive.metadata.readonly',
        redirect_uri=flask.url_for('oauth2callback', _external=True))
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('index'))


def get_secrets(filename: str) -> None:
    client = storage.Client()
    bucket = client.bucket('bookie-178719.appspot.com')
    blob = bucket.blob('secrets/client_secrets.json')
    blob.download_to_filename(filename)


if __name__ == '__main__':
    with tempfile.NamedTemporaryFile() as secrets_file:
        get_secrets(secrets_file.name)
        SECRETS_FILENAME = secrets_file.name

        # This is used when running locally. Gunicorn is used to run the
        # application on Google App Engine. See entrypoint in app.yaml.
        import uuid

        app.secret_key = str(uuid.uuid4())
        app.debug = False
        app.run(host="0.0.0.0", port=8000)
