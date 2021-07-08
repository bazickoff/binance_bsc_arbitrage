import websocket, json, requests,math, logging,os,time
from web3 import Web3
# Test phase with 10k
web3 = Web3(Web3.HTTPProvider(os.environ["ETH_PROVIDER_URL"]))

usdt = '0x55d398326f99059ff775485246999027b3197955'

def sell_to_binance(pair):     #function returns average selling price
    cc = pair
    binance_api = f'https://api.binance.com/api/v3/depth?symbol={cc}'
    bids = requests.get(binance_api).json()['bids'] #Uses the buy orderbook
    total = 0
    orders = 0
    avg =0
    for i,j in bids:
        total += float(i) * float(j)
        orders += float(j)
        if total >10000:   #If you are using 10,000 to arbitrage
            avg = total / orders #estimate
            break
    return round(avg,6)

def buy_from_binance(pair):     #function returns average buying price
    cc = pair
    binance_api = f'https://api.binance.com/api/v3/depth?symbol={cc}'
    asks = requests.get(binance_api).json()['asks'] #Uses sell orderbook
    total = 0
    orders = 0
    avg =0
    for i,j in asks:
        total += float(i) * float(j)
        orders += float(j)
        if total >10000:
            avg = total / orders 
            break
    return (round(avg,6))


def inch_price(addy,pair):
    buy = usdt
    sell = addy
    dex_quote = requests.get(f'https://api.1inch.exchange/v3.0/56/quote?fromTokenAddress={buy}&toTokenAddress={sell}&amount=10000000000000000000000').json()
    temp = float(dex_quote['fromTokenAmount']) / float(dex_quote['toTokenAmount']) #price of coin on 1inch
    if pair == 'DOGEUSDT':    #doge uses 8 decimal while most coins uses 16
        temp /= (10000000000)
    arbitrage = (( sell_to_binance(pair)- temp)/temp) * 100  #if arbitrage >0 : 1 inch price is higher ; if arbitrage <0 : binance price is higher
    if arbitrage >0:
            print(pair[0:-4], '    |   ',round(temp,6),'   |   ',sell_to_binance(pair), '   |   ',round(arbitrage,6),'%')
            
    else:    #Borrow from cream -> Short on 1inch -> Buy from Binance -> Cover position on cream
        buy = addy
        sell = usdt
        dex_quote = requests.get(f'https://api.1inch.exchange/v3.0/56/quote?fromTokenAddress={buy}&toTokenAddress={sell}&amount=10000000000000000000000').json()
        arbitrage = (( buy_from_binance(pair)- temp)/temp) * 100
        if arbitrage >0:
            print('No arbitrage opportunity due to low liquidity and high slippage')
        print(pair[0:-4], '    |   ',round(temp,6),'   |   ',buy_from_binance(pair), '   |   ',round(arbitrage,6),'%')

print('       1 inch   on bsc    |   Binance        ')
while True:
    inch_price('0xbf5140a22578168fd562dccf235e5d43a02ce9b1','UNIUSDT') #example

