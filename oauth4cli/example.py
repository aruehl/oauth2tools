from oauth4cli import OAuth4CLI

if '__main__' == __name__:
    o4c = OAuth4CLI(
        client_id='my-client-id',
        client_secret='my-client-secret',
        well_known_url='https://www.example.com/.well-known'
    )
    tokens = o4c.login()
    print(tokens.get('access_token'))
