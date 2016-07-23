# This file is a testing file
# This is not a final product
# This is an attempt to combine the redis listener of events failing with the lsp_ero switching


# Current implementation utilizes two routes that are statically defined in the code.

'''
Created on July 23, 2016

@author: jopika

Thanks to azaringh for his example and templates
'''

import redis
import json
import pprint
import requests
requests.packages.urllib3.disable_warnings()

# Initializing Redis channel
r = redis.StrictRedis(host='10.10.4.252', port=6379, db=0)
pubsub = r.pubsub()
pubsub.subscribe('link_event')

def redisChannel():
    
    for item in pubsub.listen():
        print item['channel'], ":", item['data']
        if isinstance(item['data'], basestring):
            d = json.loads(item['data'])
    return;


# Start of API initializing
url = "https://10.10.2.29:8443/oauth2/token"

payload = {'grant_type': 'password', 'username': 'group7', 'password': 'Group7'}
response = requests.post (url, data=payload, auth=('group7','Group7'), verify=False)
json_data = json.loads(response.text)
authHeader= {"Authorization":"{token_type} {access_token}".format(**json_data)}

r = requests.get('https://10.10.2.29:8443/NorthStar/API/v1/tenant/1/topology/1/te-lsps/', headers=authHeader, verify=False)

p = json.dumps(r.json())
lsp_list = json.loads(p)
# Find target LSP to use lspIndex
for lsp in lsp_list:
    if lsp['name'] == 'GROUP_SEVEN_SF_NY_LSP1':
        print "found it!"
        print lsp['liveProperties']['ero']
        break

print "hello everyone, so far so good!"