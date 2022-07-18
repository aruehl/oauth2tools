import requests
import time
import webbrowser

from flask import Flask, request, render_template
from requests_oauthlib import OAuth2Session
from threading import Thread
from werkzeug.serving import make_server

CALLBACK_URL = 'http://localhost:54345/callback'
DEFAULT_SCOPE = 'openid'


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
        self.state = None

    def _get_oauth2_session(self, **kwargs):
        oauth2_session = OAuth2Session(
            client_id=self.client_id,
            # scope=SCOPE,
            redirect_uri=CALLBACK_URL,
            **kwargs)
        return oauth2_session

    class ServerThread(Thread):

        def __init__(self):
            Thread.__init__(self)
            app = Flask(__name__)
            app.route('/callback')(self.callback)
            self.server = make_server('127.0.0.1', 54345, app)
            self.auth_code = None
            self.state = None
            self.ctx = app.app_context()
            self.ctx.push()

        def run(self):
            self.server.serve_forever()

        def callback(self):
            self.auth_code = request.args["code"]
            self.state = request.args["state"]
            return render_template("close_me.html")

        def shutdown(self):
            self.server.shutdown()

    def login(self):
        # logging.getLogger().addHandler(logging.StreamHandler())

        server = self.ServerThread()
        server.start()

        oauth_session = self._get_oauth2_session()
        auth_url, state = oauth_session.authorization_url(self.well_known.get('authorization_endpoint'))
        webbrowser.open(auth_url)

        while server.auth_code is None:
            time.sleep(1)
        server.shutdown()

        if state != server.state:
            raise Exception("manipulated state received")
        oauth2token = oauth_session.fetch_token(
            token_url=self.well_known.get('token_endpoint'),
            client_secret=self.client_secret,
            code=server.auth_code)

        return oauth2token
