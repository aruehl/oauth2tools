import json
import time
import traceback

from oauth2tools import OAuthTools, OAuth4CLI, jwt_helper

if '__main__' == __name__:
    try:
        # load the required oidc config data
        with open("./config.json", "r") as json_file:
            app_config = json.load(json_file)

        oat = OAuthTools(**app_config.get('oidc'))
        auth_url = oat.authorization_url(redirect_uri="http://example.com/callback")
        print(f"authorization url: {auth_url}")

        post_data = oat.code_to_token_post_data(code="12345")
        print(f"post data: {post_data}")

        o4c = OAuth4CLI(**app_config.get('oidc'))
        response = o4c.login()
        print(f"access-token: {response.get('access_token')}")
        print(f"decoded body: {jwt_helper.get_body(response.get('access_token'))}")
        print(f"id-token: {response.get('id_token')}")
        print(f"decoded body: {jwt_helper.get_body(response.get('id_token'))}")
        print(f"refresh-token: {response.get('refresh_token')}")
        print(f"decoded body: {jwt_helper.get_body(response.get('refresh_token'))}")

        jwt_helper.validate_by_jwks(
            response.get('id_token'),
            o4c.well_known.get('jwks_uri'),
            options={"verify_aud": False}
        )
        print("id_token is valid")

        response = o4c.token_refresh(scope="openid email")
        print(f"new access-token: {response.get('access_token')}")
    except Exception as e:
        print(str(e))
