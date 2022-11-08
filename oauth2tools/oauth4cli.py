import logging
import time
import webbrowser

from flask import Flask, request, render_template
from threading import Thread
from werkzeug.serving import make_server

from . import OAuthTools
from .jwt_helper import *
from .exceptions import WebBrowserSupportError

CALLBACK_URL = 'http://localhost:54345/callback'
DEFAULT_SCOPE = 'openid'
LOGIN_TIMEOUT = 90


class OAuth4CLI(OAuthTools):

    def __init__(self, well_known_url: str, client_id: str, client_secret: str = None, **kwargs):
        super().__init__(well_known_url, client_id, client_secret, **kwargs)

    class ServerThread(Thread):

        def __init__(self):
            Thread.__init__(self)
            app = Flask(__name__)
            app.route('/callback')(self.callback)
            self.server = make_server('localhost', 54345, app)
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
        logging.getLogger("werkzeug").disabled = True

        server = self.ServerThread()
        server.start()

        if not webbrowser.open(self.authorization_url(CALLBACK_URL)):
            raise WebBrowserSupportError('The OS has no webbrowser installed')

        count = 0
        while server.auth_code is None and count < LOGIN_TIMEOUT:
            time.sleep(1)
            count += 1
        server.shutdown()

        if server.auth_code is None:
            raise Exception(f"login timeout of {LOGIN_TIMEOUT} seconds reached")

        if self.state != server.state:
            raise Exception("manipulated state received")

        oauth2token = self.code_to_token(
            client_secret=self.client_secret,
            code=server.auth_code
        )

        data = validate_by_jwks(
            token=oauth2token.get('id_token', None),
            jwks_url=self.well_known.get('jwks_uri'),
            options={"verify_aud": False},
            claims={"nonce": self.nonce} if self.nonce else {}
        )
        logging.debug(f"decoded id_token body: {data}")
        return oauth2token
