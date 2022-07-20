import base64
import hashlib
import requests

from random import random
from string import ascii_letters, digits


def random_string(str_size: int):
    chars = ascii_letters + digits + ".-_~"
    return ''.join(random.choice(chars) for x in range(str_size))


def well_known_metadata(well_known_url: str):
    response = requests.get(well_known_url)
    response.raise_for_status()
    return response.json()


def pkce_codes():
    code_verifier = random_string(45)
    code_digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_digest).decode('utf-8').replace('=', '')
    return code_challenge, code_verifier


class OAuthTools(object):

    def __init__(self, well_known_url: str, client_id: str, client_secret: str=None, pkce: bool = False,
                 scope: str="openid", oidc: bool=True):
        self.well_known = well_known_metadata(well_known_url)
        self.client_id = client_id
        self.client_secret = client_secret
        self.oidc = oidc
        self.pkce = pkce
        self.scope = scope
        self.redirect_uri = None
        self.state = None
        self.nonce = None
        self.code_verifier = None

    def authorization_url(self, redirect_uri: str):
        self.redirect_uri = redirect_uri
        self.state = random_string(20)

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "state": self.state,

            "scope": self.scope,
            "redirect_uri": redirect_uri,
        }

        if self.pkce:
            code_challenge, self.code_verifier = pkce_codes()
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"

        if self.oidc:
            self.nonce = random_string(25)
            params["nonce"] = self.nonce

        query_string = "&".join(f'{key}={value}' for key, value in params.items())
        auth_url = f"{self.well_known.get('authorization_endpoint')}?{query_string}"

        return auth_url

    def code_to_token_post_data(self, code: str, client_secret: str=None):
        form_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
        }
        if client_secret:
            form_data['client_secret'] = client_secret
        elif self.client_secret:
            form_data['client_secret'] = self.client_secret

        if self.code_verifier:
            form_data['code_verifier'] = self.code_verifier

        return form_data

    def code_to_token(self, code: str, client_secret: str=None):
        form_data = self.code_to_token_post_data(code, client_secret)

        return self._post_for_token(form_data)

    def client_credentials_grant(self, validate=None):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        # wsout.printFlush("doing client credential authentication ... ")
        return self._postForToken(params, validate=validate)

    def password_grant(self, username: str, password: str, scope: str='openid', validate=None):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'password',
            'username': username,
            'password': password,
            'scope': scope
        }
        # wsout.printFlush("doing password based authentication with scope '%s' ... " % params['scope'])
        return self._postForToken(params, validate=validate)

    def _post_for_token(self, form_data: dict):
        response = requests.post(self.well_known.get('token_endpoint'), data=form_data)
        response.raise_for_status()

        return response.json()

