from flask import Flask, request
import logging
import requests
from requests_oauthlib import OAuth2Session
from threading import Thread
import time
import webbrowser

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
        self.app = Flask(__name__)
        self.app.route('/callback')(self.callback)

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

        def __init__(self, parent):
            Thread.__init__(self)
            self.parent = parent

        def run(self):
            self.parent.app.run(
                port=54345,
                host='localhost'
            )

    def login(self):
        logging.getLogger().addHandler(logging.StreamHandler())

        thread = OAuth4CLI.ServerThread(self)
        # thread.daemon = True
        thread.start()

        oauth_session = self._get_oauth2_session()
        auth_url, _ = oauth_session.authorization_url(self.well_known.get('authorization_endpoint'))
        webbrowser.open(auth_url)

        while self.auth_code is None:
            time.sleep(1)

        oauth2token = oauth_session.fetch_token(
            token_url=self.well_known.get('token_endpoint'),
            client_secret=self.client_secret,
            code=self.auth_code)

        return oauth2token
