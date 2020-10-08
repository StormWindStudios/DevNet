# This script creates two objects (a host and a network)
# and then uses an HTTP DELETE call to remove them.
# There are several repetitive tasks that are well-suited
# to move to functions. Maybe give it a shot?

# Import the necessary modules
import pprint
import requests
from requests.auth import HTTPBasicAuth

# Don't generate HTTPS warnings
requests.urllib3.disable_warnings()

# Create a function to handle authentication
# Takes FMC object, returns x-auth header and domain_uuid
def authenticate(f):
    # Create authentication url
    auth_url = f["url"] + "/api/fmc_platform/v1/auth/generatetoken"

    # Send authentication request
    auth_resp = requests.post(url=auth_url,
                                  auth=HTTPBasicAuth(f["user"],f["pass"]),
                                  verify=False)

    # If authentication is successful, return the header and domain uuid
    # Otherwise, return False 
    if auth_resp.status_code >= 200 and auth_resp.status_code < 300:
        return { "headers": { "X-auth-access-token": auth_resp.headers["X-auth-access-token"] },
                 "domain_uuid": auth_resp.headers["DOMAIN_UUID"]
            }
    else:
        print("Failed to authenticate: status code {}".format(auth_resp.status_code))
        return False

# Simple function that makes sure response code is 200-300 (i.e., is successful)
def is_ok(s):
    if s.status_code >= 200 and s.status_code < 300:
        return True
    else:
        return False

# Define the basic variables needed to access the FMC API
# "Objects" is a list (denoted by square brackets)
# We will fill it with the objects created by the script
fmc = { "url": "https://fmcrestapisandbox.cisco.com",
        "user": "DevNetUsername",
        "pass": "Password",
        "objects": []
    }

# Create a pretty printer to make the JSON readable
pp = pprint.PrettyPrinter(width=30)

# Print current information and pause for user
print("\nInitial variables:\n")
pp.pprint(fmc)
input("\nPress Enter to authenticate...")

# Run authentication function with fmc dictionary
api_info = authenticate(fmc)

# Add resulting info to fmc IF it exists
# If it doesn't exist (is false), exit program
if api_info:
    fmc.update(api_info)
else:
    quit()

# Print current information and pause for user
print("\nAfter authentication:\n")
pp.pprint(fmc)
input("\nPress Enter to add host object...")

# Create URL for host objects
hosts_obj_url = fmc["url"] + "/api/fmc_config/v1/domain/{domainUUID}/object/hosts".format(domainUUID=fmc["domain_uuid"])

# Host object values (passed to FMC as JSON)
host_obj = {
  "name": "WebServer3",
  "type": "Host",
  "value": "56.45.21.5",
  "description": "Web Server (Managed via REST API)"
  }

# Send POST request to create the object
host_obj_resp = requests.post(url=hosts_obj_url, 
                              json=host_obj,
                              headers=fmc["headers"],
                              verify=False)

# If response is OK (code 200-299), save information about the new object
# by appending it as a dictionary to the fmc object:
#   - Name of object
#   - UUID
#   - link (a direct URL we can use to update or modify this object)
#   - type
if is_ok(host_obj_resp):
    fmc["objects"].append({
        "name": host_obj_resp.json()["name"],
        "id": host_obj_resp.json()["id"],
        "link": host_obj_resp.json()["links"]["self"],
        "type": host_obj_resp.json()["type"]
    })
else:
    print(host_obj_resp.text)
    quit()

# Print current information and pause for user
print("\nAfter creating new host object:\n")
pp.pprint(fmc)
input("\nPress Enter to add new network object...")

# Create URL for network objects
network_obj_url = fmc["url"] + "/api/fmc_config/v1/domain/{domainUUID}/object/networks".format(domainUUID=fmc["domain_uuid"])

# Network object values (passed to FMC as JSON)
network_obj = {
    "name": "Inside_Net_4",
    "type": "Network",
    "value": "172.16.4.0/24",
    "description": "Inside Network (Managed via REST API)"
  }

# Send POST request to create the object
network_obj_resp = requests.post(url=network_obj_url, 
                              json=network_obj,
                              headers=fmc["headers"],
                              verify=False)

# If response is OK (code 200-299), save information about the new object
# by appending it as a dictionary to the fmc object:
#   - Name of object
#   - UUID
#   - link (a direct URL we can use to update or modify this object)
#   - type
if is_ok(network_obj_resp):
    fmc["objects"].append({
        "name": network_obj_resp.json()["name"],
        "id": network_obj_resp.json()["id"],
        "link": network_obj_resp.json()["links"]["self"],
        "type": network_obj_resp.json()["type"]
    })
else:
    print(network_obj_resp.text)
    quit()

# Print current information and pause for user
print("\nAfter creating new network object:\n")
pp.pprint(fmc)

# While there are fmc objects in the list, send an HTTP DELETE request
# to each object's direct URL (provided in response when object created)
# We will always be using the first object of the list (index 0: [0]),
# because deleting it moves all remaining elements forward.
while fmc["objects"]:
    input("\nPress enter to delete {} ({})...".format(fmc["objects"][0]["name"], fmc["objects"][0]["type"]))
    del_obj_resp = requests.delete(url=fmc["objects"][0]["link"], 
                                   headers=fmc["headers"],
                                   verify=False)
    if is_ok(del_obj_resp):
        del fmc["objects"][0]
        print("\nAfter deleting object:\n")
        pp.pprint(fmc)
    else:
        print(del_obj_resp.text)
