import os
import jwt
import uuid
import hashlib
import json

from urllib.parse import urlencode

import requests

with open("access_key.json", "r") as json_file:
    access_info = json.loads(json_file.read())

access_key = access_info["access_key"]
secret_key = access_info["secret_key"]
server_url = "https://api.upbit.com"

payload = {
    'access_key': access_key,
    'nonce': str(uuid.uuid4()),
}

jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
authorize_token = 'Bearer {}'.format(jwt_token)
headers = {"Authorization": authorize_token}

res = requests.get(server_url + "/v1/accounts", headers=headers)

print(res.json())