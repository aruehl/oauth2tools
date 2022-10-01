import json
from ctypes import Union

import jwt


def _return(decoded_string: str, as_json: bool=False):
    if as_json:
        return json.loads(decoded_string)
    else:
        return decoded_string


def get_header(token: str, as_json: bool=False):
    """
    :param token:
    :param as_json:
    :return: decoded header
    """
    return _return(jwt.get_unverified_header(token), as_json)


def get_body(token: str, as_json: bool=False):
    """
    :param token: the jwt
    :param as_json: return the body as json
    :return: decoded body
    """
    return _return(jwt.decode(token, options={"verify_signature": False}), as_json)


def get_claim(token: str, claim: str):
    """
    :param token: the jwt
    :param claim: name or path of the claim to return
    :return: decoded body
    """
    body = get_body(token, True)
    return body.get(claim, None)


def validate_by_key(token: str, signing_key: str, algorithms: list=None, as_json: bool=False, **kwargs):
    """
    Using PyJWT (https://pyjwt.readthedocs.io/en/latest/usage.html) to validate the JWT.
    Algorithms are restricted to RS256 and ES256 by default.
    All keyword arguments are bypassed. For example:
    issuer="https://www.example.com/idp/test"
    audience=["my_service"]
    options={"verify_aud": False}
    :param token: the jwt
    :param signing_key: the public key for checking the signature
    :param algorithms: list of valid algorithms
    :param as_json: choose whether the response should be string or json
    :param kwargs: everything supported by the PyJWT module
    :return: decoded body
    """
    if algorithms is None:
        algorithms = ["ES256", "RS256"]

    data = jwt.decode(
        token,
        signing_key,
        algorithms=algorithms,
        **kwargs
    )
    for k in kwargs.get("claims", {}):
        if k in data:
            if data.get(k) != kwargs.get("claims").get(k):
                raise Exception(f"invalid value for claim '{k}'")
        else:
            raise Exception(f"required claim '{k}' is missing")

    return _return(data, as_json)


def validate_by_jwks(token: str, jwks_url: str, algorithms: list=None, as_json: bool=False, **kwargs):
    """
    Using PyJWT (https://pyjwt.readthedocs.io/en/latest/usage.html) to validate the JWT.
    Algorithms are restricted to RS256 and ES256 by default.
    All keyword arguments are bypassed. For example:
    issuer="https://www.example.com/idp/test"
    audience=["my_service"]
    options={"verify_aud": False}
    :param token: the jwt
    :param jwks_url: the url of the jwks
    :param algorithms: list of valid algorithms
    :param as_json: choose whether the response should be string or json
    :param kwargs: everything supported by the PyJWT module
    :return: decoded body
    """
    client = jwt.PyJWKClient(jwks_url)
    signing_key = client.get_signing_key_from_jwt(token)
    data = validate_by_key(token, signing_key.key, algorithms, **kwargs)

    return _return(data, as_json)
