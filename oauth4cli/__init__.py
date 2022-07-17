from flask import Flask, request
import requests
from requests_oauthlib import OAuth2Session
from threading import Thread
import time
import webbrowser
from werkzeug.serving import make_server

CALLBACK_URL = 'http://localhost:54345/callback'
SCOPE = 'openid'


def _get_well_known_metadata(well_known_url):
    response = requests.get(well_known_url)
    response.raise_for_status()
    return response.json()


class OAuth4CLI:

    def __init__(self, well_known_url, client_id, client_secret=None, flow='auth_code', **kwargs):
        self.well_known = _get_well_known_metadata(well_known_url)
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_code = None

    def _get_oauth2_session(self, **kwargs):
        oauth2_session = OAuth2Session(
            client_id=self.client_id,
            # scope=SCOPE,
            redirect_uri=CALLBACK_URL,
            **kwargs)
        return oauth2_session

    def callback(self):
        self.auth_code = request.args["code"]
        return "You can now close this Browser tab and go back to your CLI."

    class ServerThread(Thread):

        def __init__(self, app):
            Thread.__init__(self)
            self.server = make_server('127.0.0.1', 54345, app)
            self.ctx = app.app_context()
            self.ctx.push()

        def run(self):
            self.server.serve_forever()

        def shutdown(self):
            self.server.shutdown()

    def login(self):
        # logging.getLogger().addHandler(logging.StreamHandler())

        app = Flask(__name__)
        app.route('/callback')(self.callback)
        server = self.ServerThread(app)
        server.start()

        oauth_session = self._get_oauth2_session()
        auth_url, _ = oauth_session.authorization_url(self.well_known.get('authorization_endpoint'))
        webbrowser.open(auth_url)

        while self.auth_code is None:
            time.sleep(1)
        server.shutdown()

        oauth2token = oauth_session.fetch_token(
            token_url=self.well_known.get('token_endpoint'),
            client_secret=self.client_secret,
            code=self.auth_code)

        return oauth2token
