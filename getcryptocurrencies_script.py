import requests
import json
x = requests.get(url='https://api.tip.cc/api/v0/currencies/cryptocurrencies', headers={'accept': 'application/json'})

crypto_dict = json.loads(x.text)
crypto_dict = crypto_dict['cryptocurrencies']


scaling_dict = {}
for i in range(len(crypto_dict)):
    name = crypto_dict[i]['code'].upper()
    scale = crypto_dict[i]['format']['scale']
    scaling_dict[name] = scale
