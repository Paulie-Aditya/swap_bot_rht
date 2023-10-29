import nextcord 
from nextcord.ext import commands
import requests 
import asyncio
from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()
import urllib.request 
import json
from typing import Optional 

import config_swap_bot
import getcryptocurrencies_script
import balance_fetching_script
import refund
bot = commands.Bot(command_prefix="!", intents= nextcord.Intents.all())

emojis = {"BNB":'<:bnblogo:1132021009189445632>',"BUSD":"<:busdlogo:1132022417083088978>","RHT":"<:rhtlogo:1132022314469429268>"}


@bot.slash_command(name= "refund", description="to be used to refunds")
async def say(
    interaction: nextcord.Interaction,
    user:str =nextcord.SlashOption(
    required=True
    ),
    value:float = nextcord.SlashOption(
    required=True
    ),
    coin: str = nextcord.SlashOption(
    required= True
    ),
):
    if interaction.user.id in [464445762986704918 , 457040844105711616]:
        user = user.strip('<@>')
        coin = coin.upper()
        prev_value = float(value)
        x = refund.refund(user,value,coin)
        if x.status_code == 200:
            await interaction.response.send_message(f'Sent {prev_value} {coin} to <@{user}>')
        else:
            await interaction.response.send_message(f'An error has occured. <@464445762986704918> fix this.')
    else:
        await interaction.response.send_message("You aren't authorized to run this command")

@bot.slash_command(name = "bals", description= 'Balances')
async def bals(
    interaction: nextcord.Interaction
):
    embed = nextcord.Embed(title="BALANCES", color= 0xee2ef)
    for coin in ["BNB","BUSD","RHT"]:
        dict_ = json.loads(balance_fetching_script.balance_fetching(coin))
        balance = round(float(int(dict_["balance"]['value'])/(10**getcryptocurrencies_script.scaling_dict[coin])),5)
        price_conversion = round(float(balance*prices[coin]), 3)
        if balance == 0:
            value = f'None'
        else:
            value = f'**{balance}**  **(${price_conversion})**'

        embed.add_field(name = f'{emojis[coin]} {coin}', value= value, inline= False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(name="rates", description='Rates')
async def rates(
    interaction: nextcord.Interaction,
    coin: Optional[str] = nextcord.SlashOption(
    name= "coin",
    description="Rate of any particular coin/token you want",
    choices=['RHT','BNB','BUSD'],
    )
):
    embed = nextcord.Embed(title='RATES', color= 0xee2ef)
    if coin:
        embed.add_field(name = f'{emojis[coin]} {coin}', value=f'{rates[coin]}:1',inline=False)
    else:
        for coin in supported:
            embed.add_field(name = f'{emojis[coin]} {coin}', value=f'{rates[coin]}:1',inline=False)
    
    await interaction.response.send_message(embed = embed,ephemeral=True)
@bot.slash_command(name='rhthelp',description='Help Command')
async def help_command(
    interaction: nextcord.Interaction,
):
    embed = nextcord.Embed(title='Help Command', description= '''
To Start a Swap, tip the bot using <@617037497574359050>, and follow the following format:\n**$tip <@1123156309588574218> <amount> <coin you are sending> W <coin you want>** \n\nSuppose you want to exchange 1$ BNB to RHT.\nDo the following: **$tip <@1123156309588574218> $1 BNB w RHT**\n\n
                           And that's it! You will receive 1$ of RHT in your tip.cc wallet!''', color= 0xee2ef)
    embed.add_field(name='`/rates`', value='Rates for selling respective coins are listed here',inline=False)
    embed.add_field(name = '`/rhthelp`', value='That is what brought you here!',inline=False)
    embed.add_field(name = "`/bals`",value="Shows balances of the Bot.",inline=False)
    await interaction.response.send_message(embed = embed, ephemeral=True)
#PAIRS
'''
RHT/BNB
RHT/BUSD
BNB/BUSD
'''
rht_price = 0
bnb_price = 0
busd_price = 1

prices = {"RHT":rht_price,"BNB": bnb_price,"BUSD":1}
supported = ["RHT","BNB","BUSD"]
rates = {"RHT": 0.9, "BNB":1, "BUSD":1}

def fail(tipping_json, amount, currency, tipping_url):
    previous_amount = float(amount)
    try:
        amount = amount* (10**getcryptocurrencies_script.scaling_dict[currency])
    except:
        return f'An Error Occured, Refund will be handled by <@464445762986704918>'
    tipping_json["amount"]['value'] = amount
    tipping_json["amount"]['currency'] = currency
    x = requests.post(tipping_url, json = tipping_json, headers={'accept':'application/json','Authorization': f'Bearer {config_swap_bot.tipcc_api_key}', 'Content-Type': 'application/json'})

    return f'You have been refunded {previous_amount} {currency}', x

def success(tipping_json, value, want_coin, tipping_url):
    if want_coin == 'BNB':
        previous_value = round(float(value),8)
    else:
        previous_value = round(float(value),5)
    value = int(value* (10**getcryptocurrencies_script.scaling_dict[want_coin]))
    tipping_json["amount"]['value'] = value
    tipping_json["amount"]['currency'] = want_coin
    x = requests.post(tipping_url, json = tipping_json, headers={'accept':'application/json','Authorization': f'Bearer {config_swap_bot.tipcc_api_key}', 'Content-Type': 'application/json'})

    return f'You have received {previous_value} {want_coin}' , x

def currency_handling(currency, amount):
    currency = str(currency).strip("*.")
    currency = currency.upper()
    if currency in supported:
        return currency, amount, True
    else:
        if currency in ["SATOSHI","MBTC","WEI", "GWEI"]:
            if currency in ['SATOSHI','MBTC']:
                #1 sat = 10^-8 BTC
                #1 MBTC = 10^-3 BTC
                if currency == 'SATOSHI':
                    amount = amount * (10**-8)
                elif currency == 'MBTC':
                    amount = amount* (10**-3)
                currency = "BTC"
                
            elif currency in ['WEI', 'GWEI']:
                #1 wei = 10^-18 ETH
                #1 gwei = 10^-9 ETH
                if currency  == 'GWEI':
                    amount = amount * (10**-9)
                elif currency == 'WEI':
                    amount = amount * (10**-18)
                currency = "ETH"
        return currency, amount, False

def want_coin_handling(want_coin):
    if want_coin in supported:
        return want_coin, True
    else:
        if want_coin in ["SATOSHI","MBTC","WEI", "GWEI"]:
            if want_coin in ['SATOSHI', "MBTC"]:
                want_coin = "BTC"
            elif want_coin in ['WEI', 'GWEI']:
                want_coin = "ETH"
        return want_coin, False
                

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message) and message.mention_everyone is False and message.channel.id in [1130988523898535997, 1132035939070386277, 1132059203452817458]:
        
        if message.content.startswith('$tip') and len(bot.parse_mentions(message.content))==1:
            message.content = message.content.lower()
            want_coin = message.content.split() [-1]
            want_coin = want_coin.upper()
            msg = await bot.wait_for('message')
            if msg.author.id in [617037497574359050]and bot.user.mentioned_in(msg):
                msg.content = msg.content.strip("*")
                info = msg.content.split()
                user = str(message.author.id)
                amount = float(info[4].strip("*"))
                currency = (info[5])
                currency, amount, to_do_currency= currency_handling(currency, amount)

                tipping_url = 'https://api.tip.cc/api/v0/tips'
                tipping_json = { 
                    "service": "discord", 
                    "recipient": user ,
                    "amount": {
                        "value": "",
                        "currency": ""
                    }
                }

                want_coin, to_do_wantcoin = want_coin_handling(want_coin)

                
                if not(to_do_currency and to_do_wantcoin):
                    if to_do_currency is False:
                        await message.channel.send(f'**{currency}** is not supported.')
                        return_message,x = fail(tipping_json, amount, currency, tipping_url)
                        embed = nextcord.Embed(title='Swap Failed', color= 0xef0707, description= return_message)
                        await message.channel.send(embed = embed)
                    elif to_do_wantcoin is False:
                        if want_coin == 'DONATE':
                            embed = nextcord.Embed(title='Donation', color=0x26f304, description= f'Thanks for the donation!')
                            await message.channel.send(embed = embed)
                            exit
                        else:
                            await message.channel.send(f'**{want_coin}** is not supported.') 
                            return_message,x = fail(tipping_json, amount, currency, tipping_url)
                            embed = nextcord.Embed(title='Swap Failed', color= 0xef0707, description= return_message)
                            await message.channel.send(embed = embed)
                    exit
                else:
                    value = (amount * prices[currency] * rates[currency] )/ prices[want_coin]
                    return_message, x = success(tipping_json, value, want_coin, tipping_url)


                    if x.status_code == 200:
                        embed = nextcord.Embed(title='Swap Completed!', color=0x26f304, description=f'{emojis[want_coin]} {return_message}\nThanks for Using RHT SWAP!')
                        pass
                    else:
                        return_message,x = fail(tipping_json, amount, currency, tipping_url)
                        embed = nextcord.Embed(title='Swap Failed', color= 0xef0707, description= f'The Transaction has failed. Causes may be insufficient balance or an Internal Error. Please try again if the desired balances are available.\n{return_message}')

                        
                    await message.channel.send(embed = embed)


def rht_price_fetch():
    rht_contract_address = "0xeaf363ae88e8d4083b5deb78eca37cd848c75b90"

    api_url = f'https://api.dev.dex.guru/v1/chain/56/tokens/{rht_contract_address}/market/?api-key={config_swap_bot.dex_guru_api_key}'
    webUrl = urllib.request.urlopen(api_url)
    info = webUrl.read()
    info = str(info,'UTF-8')
    info.replace("'",'"')
    info_json = json.loads(info)

    price = (round(float(info_json['price_usd']),6))
    return price

async def do():
    async def again():
        info = cg.get_price(ids = ["binancecoin"], vs_currencies="usd")
        for coin in supported:
            if coin in ["BNB"]:
                cg_fetch = {"BNB":"binancecoin"}
                prices[coin] = info[cg_fetch[coin]]['usd']
            elif coin in ["RHT"]:
                prices[coin] = rht_price_fetch()
            elif coin in ["BUSD"]:
                prices[coin] = 1
                

    while True:
        await again()
        await asyncio.sleep(5*60)
        
        continue
    

#last bot only
@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Activity(type = nextcord.ActivityType.watching, name = f'/rhthelp'))
    await do()


bot.run(config_swap_bot.swap_bot_token)