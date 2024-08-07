import logging
import sys
import time
import socket
import webbrowser

from flask import Flask, request, render_template
from threading import Thread
from werkzeug.serving import make_server

from . import OAuthTools
from .jwt_helper import *
from .exceptions import ServerError, WebBrowserSupportError

SERVER_PORT = 54345
CALLBACK_URL = f'http://localhost:{SERVER_PORT}/callback'
DEFAULT_SCOPE = 'openid'
LOGIN_TIMEOUT = 120


class OAuth4CLI(OAuthTools):

    def __init__(self, well_known_url: str, client_id: str, client_secret: str = None, **kwargs):
        super().__init__(well_known_url, client_id, client_secret, **kwargs)

    class ServerThread(Thread):

        def __init__(self):
            Thread.__init__(self)
            app = Flask(__name__)
            app.route('/callback')(self.callback)
            self.server = make_server('localhost', SERVER_PORT, app)
            self.auth_code = None
            self.state = None
            self.error = False
            self.ctx = app.app_context()
            self.ctx.push()

        def run(self):
            self.server.serve_forever()

        def callback(self):
            self.state = request.args["state"]
            try:
                self.auth_code = request.args["code"]
                return render_template("close_me.html")
            except:
                logging.debug("unexpected response from server:")
                for arg in request.args.keys():
                    logging.debug(f"{arg}: {request.args[arg]}")
                self.error = True
                return "unexpected error"

        def shutdown(self):
            self.server.shutdown()

    def login(self):
        logging.getLogger("werkzeug").disabled = True

        if socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(('localhost', SERVER_PORT)) == 0:
            raise ServerError(f"failed to start listener: port {SERVER_PORT} is in use")

        server = self.ServerThread()
        server.start()

        if not webbrowser.open(self.authorization_url(CALLBACK_URL)):
            raise WebBrowserSupportError('The OS has no webbrowser installed')

        count = 0
        try:
            while server.state is None and count < LOGIN_TIMEOUT:
                time.sleep(1)
                count += 1
        except KeyboardInterrupt:
            print("aborted by the user")
            sys.exit()
        finally:
            server.shutdown()

        if server.error:
            raise ServerError(f"unexpect server response")

        if server.state is None:
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
            options={"verify_aud": False}
        )
        logging.debug(f"decoded id_token body: {data}")
        return oauth2token
