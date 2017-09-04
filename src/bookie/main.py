import json
import logging

import flask
import httplib2
import uuid

from google.cloud import storage
from apiclient import discovery
from oauth2client import client
import tempfile

app = flask.Flask(__name__)
app.secret_key = str(uuid.uuid4())
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.secure_scheme_headers = {'X-FORWARDED-PROTOCOL': 'ssl', 'X-FORWARDED-PROTO': 'https', 'X-FORWARDED-SSL': 'on'}

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


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
        return flask.redirect(flask.url_for('index', _scheme='https', _external=True))


@app.route('/_ah/health')
def health_check():
    return 'ok', 200


def get_secrets() -> str:
    secrets_file = tempfile.NamedTemporaryFile(delete=False)
    gclient = storage.Client()
    bucket = gclient.bucket('bookie-178719.appspot.com')
    blob = bucket.blob('secrets/client_secrets.json')
    blob.download_to_filename(secrets_file.name)
    return secrets_file.name


SECRETS_FILENAME = get_secrets()


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.debug = False
    app.run(host="0.0.0.0", port=8000)
