import requests
requests.packages.urllib3.disable_warnings()
import json

url = "https://10.10.2.29:8443/oauth2/token"

payload = {'grant_type': 'password', 'username': 'group7', 'password': 'Group7'}
response = requests.post (url, data=payload, auth=('group7','Group7'), verify=False)
json_data = json.loads(response.text)
authHeader= {"Authorization":"{token_type} {access_token}".format(**json_data)}

r = requests.get('https://10.10.2.29:8443/NorthStar/API/v1/tenant/1/topology/1/nodes/', headers=authHeader, verify=False)

p = json.dumps(r.json())


print 'Hello'

print r.text

