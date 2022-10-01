# OAuth2Tools

A toolset for the most requirements dealing with OAuth2 and OpenID Connect.

## Samples

###  Building the URL for the authentication endpoint

    from oauth2tools import OAuthTools

    tools = OAuthTools(
        well_known_url="<url>", 
        client_id="<cid>", 
        client_secret="<secret>")
    auth_url = tools.authorization_url(redirect_uri="<uri>")

### Using the Browser in a CLI script for authentication

    from oauth2tools import OAuth4CLI

    o4c = OAuth4CLI(
        well_known_url="<url>", 
        client_id="<cid>", 
        client_secret="<secret>")
    response = o4c.login()
    access_token = response.get('access_token')

### Validate an received token

    from oauth2tools import jwt
    
    try:
        jwt.validate_by_jwks(
            token="<jwt>", 
            jwks_url="<jwks_url>",
            claims={"<claim_name>": "expected_value"})
    except Exception as e:
        ...