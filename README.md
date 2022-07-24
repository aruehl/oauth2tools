# OAuth2Tools

A toolset for the most requirements dealing with OAuth2 and OpenID Connect.

###  building the URL for the authentication endpoint

    tools = OAuthTools(
        well_known_url="<url>", 
        client_id="<cid>", 
        client_secret="<secret>")
    auth_url = tools.authorization_url(redirect_uri="<uri>")

### Using the Browser in a CLI script for authentication

    o4c = OAuth4CLI(
        well_known_url="<url>", 
        client_id="<cid>", 
        client_secret="<secret>")
    response = o4c.login()
    access_token = response.get('access_token')