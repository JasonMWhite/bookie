import json
import uuid
import typing
import flask
from google.cloud import storage
import httplib2
from oauth2client.contrib import flask_util

oauth2 = flask_util.UserOAuth2()  # pylint: disable=invalid-name


def _get_google_secrets() -> typing.Dict[str, str]:
    gclient = storage.Client()
    bucket = gclient.bucket('bookie-178719.appspot.com')
    blob = bucket.blob('secrets/client_secrets.json')
    secrets = json.loads(blob.download_as_string())

    return {
        'GOOGLE_OAUTH2_CLIENT_ID': secrets['web']['client_id'],
        'GOOGLE_OAUTH2_CLIENT_SECRET': secrets['web']['client_secret'],
    }


def _request_user_info(credentials):
    http = httplib2.Http()
    credentials.authorize(http)
    resp, content = http.request(
        'https:// www.googleapis.com/oauth2/v3/userinfo')

    if resp.status != 200:
        flask.current_app.logger.error(
            "Error while obtaining user profile: \n%s: %s", resp, content)
        return None
    user_email = json.loads(content.decode('utf-8'))['email']

    if user_email in ['actinolite.jw@gmail.com']:
        flask.session['user.email'] = json.loads(content.decode('utf-8'))['email']
    else:
        return None


def create_app():
    # pylint: disable=unused-variable
    secrets = _get_google_secrets()
    secrets['SECRET_KEY'] = str(uuid.uuid4())

    app = flask.Flask(__name__)
    app.config.from_mapping(secrets.items())

    oauth2.init_app(
        app,
        scopes=['email', 'profile'],
        authorize_callback=_request_user_info
    )

    @app.route('/')
    def index():
        user = flask.session.get('user.email')
        return flask.render_template('index.html', user=user)

    @app.route('/login')
    @oauth2.required
    def login():
        return flask.redirect('/')

    @app.route('/logout')
    def logout():
        # Delete the user's profile and the credentials stored by oauth2.
        del flask.session['user.email']
        flask.session.modified = True
        oauth2.storage.delete()
        return flask.redirect('/')

    @app.route('/search')
    @oauth2.required
    def search():
        return flask.render_template('search.html')

    @app.route('/_ah/health')
    def status():
        return 'OK', 200

    return app
