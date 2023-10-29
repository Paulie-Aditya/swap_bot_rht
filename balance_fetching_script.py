import requests
import config_swap_bot
def balance_fetching(code):
    x = requests.get(url = f'https://api.tip.cc/api/v0/account/wallets/{code}', headers= {'accept':'application/json','Authorization': f'Bearer {config_swap_bot.tipcc_api_key}'})
    return x.text

