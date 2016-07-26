# This is an attempt to combine the redis listener of events failing with the lsp_ero switching


# Current implementation utilizes two routes that are statically defined in the code.

'''
Created on July 23, 2016

@author: jopika
@coauthor: hwong5208 & chrischu922

Thanks to azaringh for his example and templates
'''
import redis
import json
import pprint
import requests
requests.packages.urllib3.disable_warnings()

# Authentication Credentials
authUser = 'group7'
authPass = 'Group7'

# Redis Server IP
redisIP = '10.10.4.252'

# NorthStar Server IP
northStarIP = '10.10.2.29'
northStarPort = '8443'

# Debugging (if True, script prints out what it is doing)

DEBUG = False

# Initializing Redis channel
connectedRedis = redis.StrictRedis(host= redisIP, port=6379, db=0)
pubsub = connectedRedis.pubsub()
pubsub.subscribe('link_event')

# Start of API initializing
url = "https://" + northStarIP + ":"+ northStarPort +"/oauth2/token"

# Token Authentication
payload = {'grant_type': 'password', 'username': authUser, 'password': authPass}
response = requests.post (url, data=payload, auth=(authUser,authPass), verify=False)
json_data = json.loads(response.text)
authHeader= {"Authorization":"{token_type} {access_token}".format(**json_data)}

# GROUP_SEVEN LSP Declarations
# Modify this to determing which LSPs are controlled by this script
our_lsps = [
    'GROUP_SEVEN_SF_NY_LSP1',
    'GROUP_SEVEN_SF_NY_LSP2',
    'GROUP_SEVEN_SF_NY_LSP3',
    'GROUP_SEVEN_SF_NY_LSP4',
    'GROUP_SEVEN_NY_SF_LSP1',
    'GROUP_SEVEN_NY_SF_LSP2',
    'GROUP_SEVEN_NY_SF_LSP3',
    'GROUP_SEVEN_NY_SF_LSP4']

# Routes to switch to, dependant on direction

# Route 1: From SF to NY
r1_SF_NY = [
    {'topoObjectType': 'ipv4', 'address': '10.210.16.1'},
    {'topoObjectType': 'ipv4', 'address': '10.210.17.2'}
]
# Route 1: From NY to SF
r1_NY_SF = [
    {'topoObjectType': 'ipv4', 'address': '10.210.17.2'},
    {'topoObjectType': 'ipv4', 'address': '10.210.16.1'}
]
# Route 2: From SF to NY
r2_SF_NY = [
    {'topoObjectType': 'ipv4', 'address': '10.210.15.1'},
    {'topoObjectType': 'ipv4', 'address': '10.210.11.1'},
    {'topoObjectType': 'ipv4', 'address': '10.210.12.1'}
]
# Route 2: From NY to SF
r2_NY_SF = [
    {'topoObjectType': 'ipv4', 'address': '10.210.12.2'},
    {'topoObjectType': 'ipv4', 'address': '10.210.11.2'},
    {'topoObjectType': 'ipv4', 'address': '10.210.15.2'}
]

# ListOfString specifying the routes independant of direction 
# (without terminating octet)

r1 = ['10.210.16','10.210.17']
r2 = ['10.210.15','10.210.11','10.210.12']

###########################################################

# @Consumes a redis announcement from channel 'link_event'
# @Returns an ListOfString which represent the IPAddresses of the Failled links
def link_event_json_to_ip_lists(redisStatus):
    data = json.loads(redisStatus)
    failedaddresses = []
    if data["status"]=="failed":
        sourceipaddress = data["interface_address"]
        if sourceipaddress[-1:] == "1":
            destinationipaddress = sourceipaddress[0:10]+"2"
        else: 
            destinationipaddress = sourceipaddress[0:10]+"1"

        failedaddresses = [sourceipaddress, destinationipaddress]
    # Debugging Verbose print
    if DEBUG and data['status']=="failed":
        print "Retrieved failled addresses from RedisOuput", failedaddresses
    return failedaddresses

# Calls the API to switch the LSP to the new_ero
def switchLSP(lsp, new_ero):
    new_lsp = {}
    for key in ('from', 'to', 'name', 'lspIndex', 'pathType'):
        new_lsp[key] = lsp[key]

    new_lsp['plannedProperties'] = {
        'ero': new_ero
    }

    response = requests.put('https://'+ northStarIP +':'+ northStarPort +'/NorthStar/API/v1/tenant/1/topology/1/te-lsps/' + str(new_lsp['lspIndex']), 
                        json = new_lsp, headers=authHeader, verify=False)
    if DEBUG:
        print response.text


# Consumes an LSP and route name, and produces the coresponding ERO to be updated to
def determineERO(lsp, route):
    lspName = lsp['name']
    new_ero = {} # Initialized to Empty

    # Check which route it matches
    # STATIC allocation
    # TODO: Make ero construction more robust and allows for more than just two routes
    if route == 'r2':
        if lspName[12:17] == 'SF_NY':
            new_ero = r1_SF_NY
        elif lspName[12:17] == 'NY_SF':
            new_ero = r1_NY_SF
    elif route == 'r1':
        if lspName[12:17] == 'SF_NY':
            new_ero = r2_SF_NY
        elif lspName[12:17] == 'NY_SF':
            new_ero = r2_NY_SF

    print 'switching from ', route
    switchLSP(lsp, new_ero)


# Checks Which LSPs require updating, and calls procedure to update
def check_lsp(failedAddresses):
    # API Call to pull all LSPs
    returnData = requests.get('https://'+ northStarIP +':'+ northStarPort +'/NorthStar/API/v1/tenant/1/topology/1/te-lsps/', headers=authHeader, verify=False)
    dumpedData = json.dumps(returnData.json())
    lsp_list = json.loads(dumpedData)

    for lsp in lsp_list:
        if lsp['name'] in our_lsps:
            currentEro = lsp['liveProperties']['ero']
            currentRoute = 0 # Initializing to NULL
            for adr in currentEro:
                address = adr['address']
                if address[:-2] in r1:
                    currentRoute = 'r1'
                elif address[:-2] in r2:
                    route = 'r2'
                else:
                    route = 'error'
                for failedAddress in failedAddresses:
                    if failedAddresses == address:
                        if DEGUG:
                            print "Found an LSP to switch! Name: ", lsp['name'], " and Route: ", route
                        determineERO(lsp, route)

def redisListener():
    for item in pubsub.listen():
        print item['channel'], ":", item['data']
        if isinstance(item['data'], basestring):
            d = json.loads(item['data'])
            # pprint.pprint(d, width=1)
            # failedaddresses = link_event_json_to_ip_lists(d)
            failedaddresses = []
            failedaddresses = link_event_json_to_ip_lists(item['data'])
            if DEBUG:
                print 'Found event, checking if switching LSP is needed'
            check_lsp(failedaddresses)



# redisListener()




#########################################################


sampleRedisOutput = {"status": "failed", "router_id": "10.210.10.106", 
                    "timestamp": "Mon:21:50:09", "interface_address": "10.210.13.1", 
                    "interface_name": "ge-1/0/4", "router_name": "dallas"}


def debug(debugInput):
    failedaddresses = link_event_json_to_ip_lists(debugInput)
    check_lsp(failedaddresses)
