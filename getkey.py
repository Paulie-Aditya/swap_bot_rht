#-----
#Script to obtain api-key
#!/usr/bin/env python3
import sys
import requests

# get the token from command line
if len(sys.argv) != 2:
  print('Usage: ./getkey.py <bot token>')
  exit(1)

token = sys.argv[1]
# headers for all requests - content type and authorization
headers = {'Content-Type': 'application/json', 'Authorization': 'Bot ' + token}

# retrieve the dm channel with oknu
dm_response = requests.post('https://discord.com/api/users/@me/channels', data='{"recipient_id":"350270174462607360"}', headers=headers)
dm = dm_response.json()

# retrieve the dms
dms_response = requests.get('https://discord.com/api/channels/' + dm['id'] + '/messages', headers=headers)
messages = dms_response.json()

# get last message containing a possible api key
key = [msg for msg in messages if msg['content'].startswith('eyJ') and msg['author']['id'] == '350270174462607360'][-1]
# return it
print(key['content'])

