import jwt
import logging
import requests
import time

from . import tools, jwt_helper
from .exceptions import ParameterError, TokenManipulationError


class OAuthTools(object):

    def __init__(self,
                 well_known_url: str,
                 client_id: str,
                 client_secret: str = None,
                 scope: str = None,
                 pkce: str = None,
                 oidc: bool = True):
        """
        Initiate the OAuthTools.
        :param well_known_url:
        :param client_id:
        :param client_secret:
        :param scope: space separated list of scopes
        :param pkce: if required, the type of pkce method. Valid are 'plain' and 'S256'. If possible use S256.
        :param oidc: if True (default), the additional nonce parameter will be used
        """
        self.well_known = tools.well_known_metadata(well_known_url)
        self.client_id = client_id
        self.client_secret = client_secret
        self.oidc = oidc
        self.pkce = pkce
        self.scope = scope if scope else "openid" if oidc else ""
        self.redirect_uri = None
        self.state = None
        self.nonce = None
        self.code_verifier = None
        self.refresh_token = None

    def _post_for_token(self, form_data: dict):
        response = requests.post(self.well_known.get('token_endpoint'), data=form_data)
        response.raise_for_status()
        response_json = response.json()
        if self.oidc and jwt_helper.get_claim(response_json.get('access_token'), "nonce") != self.nonce:
            raise TokenManipulationError('unexpected nonce value in access-token')
        self.refresh_token = response_json.get('refresh_token')
        return response_json

    def authorization_url(self, redirect_uri: str, scope: str = None):
        """
        Builds the full authorization url for an authorization code flow request
        :param redirect_uri:
        :param scope: optional scope (overwrites the scope from initiation)
        :return: authorization url
        """
        self.redirect_uri = redirect_uri
        self.state = tools.random_string(20)

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "state": self.state,
            "scope": scope if scope else self.scope,
            "redirect_uri": redirect_uri,
        }

        if self.pkce:
            code_challenge, self.code_verifier = tools.pkce_codes(self.pkce)
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = self.pkce

        if self.oidc:
            self.nonce = tools.random_string(25)
            params["nonce"] = self.nonce

        query_string = "&".join(f'{key}={value}' for key, value in params.items())
        auth_url = f"{self.well_known.get('authorization_endpoint')}?{query_string}"

        return auth_url

    def code_to_token_post_data(self, code: str, client_secret: str = None, redirect_uri: str = None):
        if redirect_uri:
            self.redirect_uri = redirect_uri
        elif not self.redirect_uri:
            raise ParameterError("redirect_uri is required")

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

    def code_to_token(self, code: str, client_secret: str = None):
        form_data = self.code_to_token_post_data(code, client_secret)

        return self._post_for_token(form_data)

    def client_credentials_grant(self):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        logging.debug("doing client credential authentication ... ")
        return self._post_for_token(params)

    def password_grant(self, username: str, password: str, scope: str = None):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'password',
            'username': username,
            'password': password,
            'scope': scope if scope is not None else self.scope
        }
        logging.debug("doing password based authentication with scope '%s' ... " % params['scope'])
        return self._post_for_token(params)

    def token_refresh(self, scope: str = None):
        if jwt_helper.get_claim(self.refresh_token, "exp") < time.time():
            raise jwt.exceptions.ExpiredSignatureError()
        params = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'scope': scope if scope is not None else self.scope
        }
        logging.debug("doing token refresh with scope '%s' ... " % params['scope'])
        return self._post_for_token(params)
