import enum
import base64
import hashlib
import random
import requests

from string import ascii_letters, digits

from .oauth2tools import OAuthTools


class PKCE(enum.Enum):
    none = 0
    plain = 1
    S256 = 2


def random_string(str_size: int):
    chars = ascii_letters + digits + ".-_~"
    return ''.join(random.choice(chars) for x in range(str_size))


def well_known_metadata(well_known_url: str):
    response = requests.get(well_known_url)
    response.raise_for_status()
    return response.json()


def pkce_codes(methode: PKCE=PKCE.S256, length: int=64):
    """
    Generates the code_challenge and code_verifier for the OAuth2 PKCE extension.
    For more information about PKCE look at: https://www.oauth.com/oauth2-servers/pkce/authorization-request/
    :param methode: Type of encryption. If possible, use S256!
    :param length: The length of the code_verifier. Valid strings are between 43 and 128 characters long.
    :return: tuple of code_challenge and code_verifier
    """
    code_verifier = random_string(length)
    if methode == PKCE.S256:
        code_digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(code_digest).decode('utf-8').replace('=', '')
    else:
        code_challenge = code_verifier
    return code_challenge, code_verifier


