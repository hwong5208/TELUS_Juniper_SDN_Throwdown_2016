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


# There should be a variable called 'downedLink' that contains the links that are down
downedLink = ['10.210.16.1', '10.210.16.2'];

# Start of API initializing
url = "https://10.10.2.29:8443/oauth2/token"

payload = {'grant_type': 'password', 'username': 'group7', 'password': 'Group7'}
response = requests.post (url, data=payload, auth=('group7','Group7'), verify=False)
json_data = json.loads(response.text)
authHeader= {"Authorization":"{token_type} {access_token}".format(**json_data)}

r = requests.get('https://10.10.2.29:8443/NorthStar/API/v1/tenant/1/topology/1/te-lsps/', headers=authHeader, verify=False)

our_lsps = [
    'GROUP_SEVEN_SF_NY_LSP1',
    'GROUP_SEVEN_SF_NY_LSP2',
    'GROUP_SEVEN_SF_NY_LSP3',
    'GROUP_SEVEN_SF_NY_LSP4',
    'GROUP_SEVEN_NY_SF_LSP1',
    'GROUP_SEVEN_NY_SF_LSP2',
    'GROUP_SEVEN_NY_SF_LSP3',
    'GROUP_SEVEN_NY_SF_LSP4']

p = json.dumps(r.json())
lsp_list = json.loads(p)

def apiCall(lsp, ero):
    # Fill only the required fields     
    new_lsp = {}
    for key in ('from', 'to', 'name', 'lspIndex', 'pathType'):
        new_lsp[key] = lsp[key]
    
    new_lsp['plannedProperties'] = {
        'ero': ero
    }
    
    # print ero
    # print 'welp'
    response = requests.put('https://10.10.2.29:8443/NorthStar/API/v1/tenant/1/topology/1/te-lsps/' + str(new_lsp['lspIndex']), 
                            json = new_lsp, headers=authHeader, verify=False)
    # print response.text




def switchERO(lsp, route):
    lspName = lsp['name']
    # print 'hello ', lspName
    ero = {}
    if route == 'r2':
        if lspName[12:17] == 'SF_NY':
            #dosomething
            ero= [ 
                            { 'topoObjectType': 'ipv4', 'address': '10.210.16.1'},
                            { 'topoObjectType': 'ipv4', 'address': '10.210.17.2'}
                           ]
            print lsp['name'], route
        elif lspName[12:17] == 'NY_SF':
            #dosomething
            ero= [
                            { 'topoObjectType': 'ipv4', 'address': '10.210.17.1'},
                            { 'topoObjectType': 'ipv4', 'address': '10.210.16.2'}
                           ]
            print lsp['name'], route
    elif route == 'r1':
        if lspName[12:17] == 'SF_NY':
            #dosomething
            ero= [ 
                            { 'topoObjectType': 'ipv4', 'address': '10.210.15.1'},
                            { 'topoObjectType': 'ipv4', 'address': '10.210.11.1'},
                            { 'topoObjectType': 'ipv4', 'address': '10.210.12.1'}
                           ]
            print lsp['name'], route
        elif lspName[12:17] == 'NY_SF':
            #dosomething
            ero= [ 
                            { 'topoObjectType': 'ipv4', 'address': '10.210.12.2'},
                            { 'topoObjectType': 'ipv4', 'address': '10.210.11.2'},
                            { 'topoObjectType': 'ipv4', 'address': '10.210.15.2'}
                           ]
            print lsp['name'], route
    else:
        print 'WARNING: SOMETHING WENT WRONG'


    apiCall(lsp, ero)
    # ero= [ 
    #                 { 'topoObjectType': 'ipv4', 'address': '10.210.15.2'},
    #                 { 'topoObjectType': 'ipv4', 'address': '10.210.13.2'},
    #                 { 'topoObjectType': 'ipv4', 'address': '10.210.17.1'}
    #                ]


    # new_lsp = {}
    # for key in ('from', 'to', 'name', 'lspIndex', 'pathType'):
    #     new_lsp[key] = lsp[key]
    
    # new_lsp['plannedProperties'] = {
    #     'ero': ero
    # }
    # print ero, '\n \n '
    
    # response = requests.put('https://10.10.2.29:8443/NorthStar/API/v1/tenant/1/topology/1/te-lsps/' + str(new_lsp['lspIndex']), 
    #                         json = new_lsp, headers=authHeader, verify=False)




# Find target LSP to use lspIndex

# Assume there is two routes (r1, r2) that are arrays of 
# strings specifying the routes (without terminating octet)

r1 = ['10.210.16','10.210.17']
r2 = ['10.210.15','10.210.11','10.210.12']

for lsp in lsp_list:
    if lsp['name'] in our_lsps:
        # print "found it!"
        # print 'here is the current ero'
        address_list = lsp['liveProperties']['ero']
        route = 0
        for adr in address_list:
            address = adr['address']
            if address[:-2] in r1:
                route = 'r1'
            elif address[:-2] in r2:
                route = 'r2'
            else:
                route = 'error'
            for deadAddress in downedLink:
                if deadAddress == address:
                    # Switch the LSP here
                    switchERO(lsp, route);
                    print "done!", lsp['name'], route, address[:-2], '\n'
            # print address['address']

print "hello everyone, so far so good!"
