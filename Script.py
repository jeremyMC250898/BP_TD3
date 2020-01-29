import json
import requests

url="http://api.binance.com/api/v3/exchangeInfo"
key = "KegqmLKeO6HiVeV4yue6Kt1AIucusHAHBex2MAqoMF3OqOttb5NUxgm3znuONHIT"
response=requests.get(url)
response_json = response.json()

allCrypto=[]
for i in range(0,len(response_json['symbols'])):
    if(response_json['symbols'][i]['baseAsset'] not in allCrypto):
        allCrypto.append(response_json['symbols'][i]['baseAsset'])


print(allCrypto)