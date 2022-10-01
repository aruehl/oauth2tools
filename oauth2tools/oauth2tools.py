import base64
import hashlib
import random
import requests

from string import ascii_letters, digits


def random_string(str_size: int):
    chars = ascii_letters + digits + ".-_~"
    return ''.join(random.choice(chars) for x in range(str_size))


def well_known_metadata(well_known_url: str):
    response = requests.get(well_known_url)
    response.raise_for_status()
    return response.json()


def pkce_codes(methode: str="S256", length: int=64):
    """
    Generates the code_challenge and code_verifier for the OAuth2 PKCE extension.
    For more information about PKCE look at: https://www.oauth.com/oauth2-servers/pkce/authorization-request/
    :param methode: Type of encryption. Valid are plain and S256. If possible use S256.
    :param length: The length of the code_verifier. Valid strings are between 43 and 128 characters long.
    :return: tuple of code_challenge and code_verifier
    """
    code_verifier = random_string(length)
    if methode == "S256":
        code_digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(code_digest).decode('utf-8').replace('=', '')
    elif methode == "plain":
        code_challenge = code_verifier
    else:
        raise ValueError("Valid values for methode are only 'plain' and 'S256'.")
    return code_challenge, code_verifier


class OAuthTools(object):

    def __init__(self, well_known_url: str, client_id: str, client_secret: str=None, pkce: str=None,
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

    def _post_for_token(self, form_data: dict):
        response = requests.post(self.well_known.get('token_endpoint'), data=form_data)
        response.raise_for_status()

        return response.json()

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
            code_challenge, self.code_verifier = pkce_codes(self.pkce)
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = self.pkce

        if self.oidc:
            self.nonce = random_string(25)
            params["nonce"] = self.nonce

        query_string = "&".join(f'{key}={value}' for key, value in params.items())
        auth_url = f"{self.well_known.get('authorization_endpoint')}?{query_string}"

        return auth_url

    def code_to_token_post_data(self, code: str, client_secret: str=None, redirect_uri: str=None):
        if redirect_uri is not None:
            self.redirect_uri = redirect_uri
        elif self.redirect_uri is None:
            raise ValueError("redirect_uri is required")

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

    def client_credentials_grant(self):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        # print("doing client credential authentication ... ")
        return self._post_for_token(params)

    def password_grant(self, username: str, password: str, scope: str='openid'):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'password',
            'username': username,
            'password': password,
            'scope': scope
        }
        # print("doing password based authentication with scope '%s' ... " % params['scope'])
        return self._post_for_token(params)
