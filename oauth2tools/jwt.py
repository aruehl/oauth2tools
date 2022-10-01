import json
from ctypes import Union

import jwt


def _return(decoded_string: str, as_json: bool = False):
    if as_json:
        return json.loads(decoded_string)
    else:
        return decoded_string


def get_header(token: str, as_json: bool = False):
    """
    :param token:
    :param as_json:
    :return: decoded header
    """
    return _return(jwt.get_unverified_header(token), as_json)


def get_body(token: str, as_json: bool = False):
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


def validate_by_key(token: str, signing_key: str, algorithms: list = None, as_json: bool = False, **kwargs):
    """
    Using PyJWT (https://pyjwt.readthedocs.io/en/latest/usage.html) to validate the JWT.
    Algorithms are restricted to RS256 and ES256 by default.
    All keyword arguments are bypassed. For example:
    issuer="https://www.example.com/idp/test"
    audience=["my_service"]
    options={"verify_aud": False}
    Additional claims to be checked can be passed within the claims param. For example:
    The 'groups' claim must be equal to or contain the 'my_group'
    claims={"groups": "my_group"}
    The 'groups' claim must be equal to or contain one of the listed groups
    claims={"groups": ["my_group", "your_group"]}
    :param token: the jwt
    :param signing_key: the public key for checking the signature
    :param algorithms: list of valid algorithms
    :param as_json: choose whether the response should be string or json
    :param kwargs: everything supported by the PyJWT module
    :return: decoded body
    """
    if algorithms is None:
        algorithms = ["ES256", "RS256"]

    decoded = jwt.decode(
        token,
        signing_key,
        algorithms=algorithms,
        **kwargs
    )
    claims = kwargs.get("claims", {})
    for claim_name in claims:
        if claim_name in decoded:
            expected_value = claims.get(claim_name)
            claim_value = decoded.get(claim_name)
            if type(claim_value) is str:
                if type(expected_value) is str:
                    if claim_value != expected_value:
                        raise InvalidClaimValueError(f"invalid value '{claim_value}' for claim '{claim_name}' found")
                elif type(expected_value) is list:
                    if claim_value not in expected_value:
                        raise InvalidClaimValueError(f"claim '{claim_name}' does not contain the expected value '{claim_value}'")
                else:
                    raise SyntaxError(f"invalid type of for claim '{claim_name}'")
            elif type(claim_value) is list:
                if type(expected_value) is str:
                    if expected_value not in claim_value:
                        raise InvalidClaimValueError(f"no expected value ('{claim_value}') in claim '{claim_name}'")
                elif type(expected_value) is list:
                    if len(set(claim_value).intersection(expected_value)) == 0:
                        raise InvalidClaimValueError(f"no expected value ('{claim_value}') in claim '{claim_name}'")
                else:
                    raise SyntaxError(f"invalid type of for claim '{claim_name}'")
        else:
            raise MissingClaimError(f"required claim '{claim_name}' is missing")

    return _return(decoded, as_json)


def validate_by_jwks(token: str, jwks_url: str, algorithms: list = None, as_json: bool = False, **kwargs):
    """
    Using PyJWT (https://pyjwt.readthedocs.io/en/latest/usage.html) to validate the JWT.
    Algorithms are restricted to RS256 and ES256 by default.
    All keyword arguments are bypassed. For example:
    issuer="https://www.example.com/idp/test"
    audience=["my_service"]
    options={"verify_aud": False}
    Additional claims to be checked can be passed within the claims param. For example:
    The 'groups' claim must be equal to or contain the 'my_group' string
    claims={"groups": "my_group"}
    The 'groups' claim must be equal to or contain one of the listed groups
    claims={"groups": ["my_group", "your_group"]}
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


class InvalidClaimValueError(Exception):
    pass


class MissingClaimError(Exception):
    pass
