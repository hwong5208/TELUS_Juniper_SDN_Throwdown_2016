import redis
import json
import pprint


d = '{"status": "failed", "router_id": "10.210.10.106", "timestamp": "Sat:13:27:35", "interface_address": "10.210.11.1", "interface_name": "ge-1/0/3", "router_name": "dallas"}'
#ith open(d) as data_file:
e = '{"status": "healed", "router_id": "10.210.10.106", "timestamp": "Sat:13:34:41", "interface_address": "10.210.11.1", "interface_name": "ge-1/0/3", "router_name": "dallas"}'

# json-> list[sourceip,destinationip]
# json ->None
def link_event_json_to_ip_lists(s):
	data = json.loads(s)

	if data["status"]=="failed":
		sourceipaddress = data["interface_address"]
		if sourceipaddress[-1:] == "1":
			destinationipaddress = sourceipaddress[0:10]+"2"
		else: 
			destinationipaddress = sourceipaddress[0:10]+"1"

		failedaddresses = [sourceipaddress, destinationipaddress]
		return failedaddresses
	return 
# test for "failed json"
print(link_event_json_to_ip_lists(d))
# test for "healed json"
print(link_event_json_to_ip_lists(e))