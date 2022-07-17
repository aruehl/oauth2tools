import json
from oauth4cli import OAuth4CLI

if '__main__' == __name__:
    with open("./config.json", "r") as json_file:
        app_config = json.load(json_file)
    o4c = OAuth4CLI(**app_config.get('oauth4cli'))
    response = o4c.login()
    print(response.get('access_token'))
