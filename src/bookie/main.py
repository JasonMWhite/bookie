import json
import logging
import uuid

import flask
from flask_oauthlib import client as oauth_client
from google.cloud import storage


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


app = flask.Flask(__name__)  # pylint: disable=invalid-name
app.secret_key = str(uuid.uuid4())
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.secure_scheme_headers = {'X-FORWARDED-PROTOCOL': 'ssl', 'X-FORWARDED-PROTO': 'https', 'X-FORWARDED-SSL': 'on'}


def get_google_oauth() -> oauth_client.OAuthRemoteApp:
    gclient = storage.Client()
    bucket = gclient.bucket('bookie-178719.appspot.com')
    blob = bucket.blob('secrets/client_secrets.json')
    secrets = json.loads(blob.download_as_string())

    client_id = secrets['web']['client_id']
    client_secret = secrets['web']['client_secret']

    oauth = oauth_client.OAuth(app)
    return oauth.remote_app('google',
                            consumer_key=client_id,
                            consumer_secret=client_secret,
                            request_token_params={'scope': 'email'},
                            base_url='https://www.googleapis.com/oauth2/v1/',
                            request_token_url=None,
                            access_token_method='POST',
                            access_token_url='https://accounts.google.com/o/oauth2/token',
                            authorize_url='https://accounts.google.com/o/oauth2/auth',
                            )


google = get_google_oauth()  # pylint: disable=invalid-name


@app.route('/')
def index():
    user = flask.session.get('user')
    return flask.render_template('index.html', user=user)


@app.route('/login')
def login():
    return google.authorize(callback=flask.url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    if 'google_token' in flask.session:
        flask.session.pop('google_token')
        flask.session.pop('user')
    return flask.redirect(flask.url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()

    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            flask.request.args['error_reason'],
            flask.request.args['error_description']
        )
    flask.session['google_token'] = (resp['access_token'], '')
    user = google.get('userinfo').data

    if user['email'] == 'actinolite.jw@gmail.com':
        flask.session['user'] = user
    else:
        flask.session.pop('google_token')
        return 'Access denied: access restricted'

    return flask.redirect(flask.url_for('index'))


@google.tokengetter
def get_google_oauth_token():
    return flask.session.get('google_token')


@app.route('/_ah/health')
def health_check():
    return 'ok', 200


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.debug = False
    app.run(host="0.0.0.0", port=8000)
