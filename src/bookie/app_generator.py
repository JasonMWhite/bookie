import json
import os
import typing
import flask
from google.cloud import storage
import httplib2
from flask_oauthlib.client import OAuth
from bookie.scrapers import meta_scraper

AUTHORIZED_USERS = [
    'actinolite.jw@gmail.com',
    'ola.white.ba@gmail.com',
]


def _get_google_secrets() -> typing.Dict[str, str]:
    gclient = storage.Client()
    bucket = gclient.bucket('bookie-178719.appspot.com')
    blob = bucket.blob('secrets/client_secrets.json')
    secrets = json.loads(blob.download_as_string())

    return {
        'GOOGLE_ID': secrets['web']['client_id'],
        'GOOGLE_SECRET': secrets['web']['client_secret'],
        'SECRET_KEY': secrets['web']['client_secret']
    }


def _request_user_info(credentials) -> None:
    http = httplib2.Http()
    credentials.authorize(http)
    resp, content = http.request(
        'https:// www.googleapis.com/oauth2/v3/userinfo')

    if resp.status != 200:
        flask.current_app.logger.error(
            "Error while obtaining user profile: \n%s: %s", resp, content)
        return

    user_email = json.loads(content.decode('utf-8'))['email']

    if user_email in AUTHORIZED_USERS:
        flask.session['user.email'] = json.loads(content.decode('utf-8'))['email']


oauth = OAuth()  # pylint: disable=invalid-name


def create_app() -> flask.Flask:
    # pylint: disable=unused-variable
    secrets = _get_google_secrets()

    templates = os.path.join(os.path.dirname(__file__), 'templates')
    app = flask.Flask(__name__, template_folder=templates)
    app.config.from_mapping(secrets.items())

    google = oauth.remote_app(
        'google',
        consumer_key=app.config.get('GOOGLE_ID'),
        consumer_secret=app.config.get('GOOGLE_SECRET'),
        request_token_params={
            'scope': 'email'
        },
        base_url='https://www.googleapis.com/oauth2/v3/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )

    @app.route('/')
    def index() -> str:
        user = flask.session.get('user.email')
        return flask.render_template('index.html', user=user)

    @app.route('/login')
    def login():
        return google.authorize(callback=flask.url_for('authorized', _external=True))

    @app.route('/login/authorized')
    def authorized():
        resp = google.authorized_response()
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                flask.request.args['error_reason'],
                flask.request.args['error_description']
            )
        flask.session['google_token'] = (resp['access_token'], '')

        user_email = google.get('userinfo').data['email']
        if user_email in ['actinolite.jw@gmail.com']:
            flask.session['user.email'] = google.get('userinfo').data['email']
            return flask.redirect(flask.url_for('index'))
        else:
            flask.abort(401)

    @app.route('/logout')
    def logout():
        # Delete the user's profile and the credentials stored by oauth2.
        if 'google_token' in flask.session:
            del flask.session['google_token']
            del flask.session['user.email']
            flask.session.modified = True
        return flask.redirect('/')

    @app.route('/_ah/health')
    def status():
        return 'OK', 200

    @google.tokengetter
    def get_google_oauth_token():
        return flask.session.get('google_token')

    @app.errorhandler(401)
    def unauthorized(_):
        return flask.Response('<b>Unauthorized</b><p>You are not authorized to use this application</p>', 401)

    @app.route('/search/')
    def search():
        if 'user.email' not in flask.session:
            flask.abort(401)

        isbn = flask.request.args.get('isbn')
        prices = meta_scraper.get_resale_prices(isbn) if isbn else {}
        return flask.render_template('search.html', isbn=isbn, prices=prices)

    return app
