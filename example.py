import json
from oauth2tools import OAuthTools, OAuth4CLI

if '__main__' == __name__:
    with open("./config.json", "r") as json_file:
        app_config = json.load(json_file)

    tools = OAuthTools(**app_config.get('oidc'))
    auth_url = tools.authorization_url(redirect_uri="http://example.com/callback")
    print("authorization url:")
    print(auth_url)

    post_data = tools.code_to_token_post_data("12345")
    print("post data:")
    print(post_data)

    o4c = OAuth4CLI(**app_config.get('oidc'))
    response = o4c.login()
    print(response.get('access_token'))
