import json
import requests
from requests.auth import HTTPBasicAuth

# Disable warnings about not verifiying HTTPS
requests.urllib3.disable_warnings()

# Dictionary with DNAC basics
dna = { 
        "url": "https://sandboxdnac.cisco.com",
        "user": "devnetuser",
        "pass": "Cisco123!",
        "headers": 
            {
            "content-type": "application/json"
            }   
    }

# Create API URL using base URL and API path
dnac_token_url = dna["url"] + "/dna/system/api/v1/auth/token"

# Authenticate using username and password, and store the response
# HTTPBasicAuth encodes username and password delimited by colon follows:
#   BASE64("username:password") => dXNlcm5hbWU6cGFzc3dvcmQ=
#   HTTP header: "Authorization": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="
auth_resp = requests.post(url = dnac_token_url, 
                          headers=dna["headers"],
                          auth=HTTPBasicAuth(dna["user"],dna["pass"]),
                          verify=False)

# Add "X-auth-access-token" to dna["headers"]
# (We now have two headers defined, including content-type)
dna["headers"]["X-auth-token"] = auth_resp.json()["Token"]

# Create device list URL
dev_list_url = dna["url"] + "/api/v1/network-device"

# Create interface list URL
iface_list_url = dna["url"] + "/api/v1/interface"

# Retrieve device list with a GET request to the URL
# We now have the token in our headers, so we don't need to
# authenticate with username and passwords
dev_list_resp = requests.get(url = dev_list_url,
                            headers=dna["headers"],
                            verify=False)

# Loop over devices in response
for dev in dev_list_resp.json()["response"]:
    # Printing hostname, platform, and UUID
    # \n = new line
    # {}'s are replaced in order with the items specified in format()
    print("\n\nHostname: {}\nPlatform ID: {}\nUUID: {}\nInterfaces:".format(dev["hostname"],
                                                                            dev["platformId"],
                                                                            dev["instanceUuid"]))
    # For each device in the outer loop, request interface information
    # Params are appended to URL (e.g, test.co/api/stuff?instanceUuid=cats)
    iface_list_resp = requests.get(url = iface_list_url,
                                headers=dna["headers"],
                                params={"instanceUuid": dev["instanceUuid"]}, 
                                verify=False)

    # For each interface in the response, print the port name and UUID
    # {:26} and {:40} set aside 26- and 40-character columns for port
    # name and instanceUuid, respectively. \t = tab
    for iface in iface_list_resp.json()["response"]:
        print("\t==> {:26} {:40}".format(iface["portName"], 
                                         iface["instanceUuid"]))
