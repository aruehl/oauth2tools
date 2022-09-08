import json
from oauth2tools import OAuthTools, OAuth4CLI

if '__main__' == __name__:
    try:
        with open("./config.json", "r") as json_file:
            app_config = json.load(json_file)

        tools = OAuthTools(**app_config.get('oidc'))
        auth_url = tools.authorization_url(redirect_uri="http://example.com/callback")
        print(f"authorization url: {auth_url}")

        post_data = tools.code_to_token_post_data(code="12345")
        print(f"post data: {post_data}")

        o4c = OAuth4CLI(**app_config.get('oidc'))
        response = o4c.login()
        print(f"access-token: {response.get('access_token')}")
    except Exception as e:
        print(e)
