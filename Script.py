import json
import requests
import pprint
import sqlite3
import time
import hmac
import hashlib
import datetime

def displayAllAsset():
    url="http://api.binance.com/api/v3/exchangeInfo"
    response=requests.get(url)
    response_json = response.json()
    allCrypto=[]
    for i in range(0,len(response_json['symbols'])):
        if(response_json['symbols'][i]['baseAsset'] not in allCrypto):
            allCrypto.append(response_json['symbols'][i]['baseAsset'])
    pprint.pprint(allCrypto)

def displayBidAsk(direction="asks", pair="BTCUSDT"):
    url="https://api.binance.com/api/v3/depth?symbol=%s&limit=10" %pair
    response=requests.get(url)
    response_json = response.json()
    pprint.pprint(response_json[direction])

def displayOrderBook(pair="BTCUSDT"):
    url="https://api.binance.com/api/v3/trades?symbol=%s&limit=10" %pair
    response=requests.get(url)
    response_json = response.json()
    pprint.pprint(response_json)

def refreshDataCandle(pair="BTCUSDT", duration="5m"):
    url="https://api.binance.com/api/v3/klines?symbol=%s&interval=%s&limit=1" %(pair, duration)
    response=requests.get(url)
    response_json = response.json() 
    return response_json

def creation_table(pair, duration,conn):
    c=conn.cursor()
    setTableName = str("binance_" + pair + "_"+ duration)
    c.execute( """CREATE TABLE IF NOT EXISTS """ +setTableName + """(Id INTEGER PRIMARY KEY, date INT, high REAL, low REAL, open REAL, close REAL,volume REAL, quotevolume REAL, weightedaverage REAL, sma_7 REAL, ema_7 REAL, sma_30 REAL,ema_30 REAL, sma_200 REAL, ema_200 REAL)""")
    c.execute("CREATE TABLE IF NOT EXISTS last_checks(Id INTEGER PRIMARY KEY, exchange TEXT, trading_pair TEXT, duration TEXT, table_name TEXT, last_check INT, startdate INT,last_id INT)")
    conn.commit()

def updateCandle(lastTime,pair, duration, setTableName,conn): 
        rep=refreshDataCandle(pair,duration) 
        c=conn.cursor()
        if int(round(time.time() * 1000)) >= lastTime :
            print("ajout")
            lastTime=rep[0][6]
            c.execute("INSERT INTO %s (date, high, low, open, close, volume, quotevolume, weightedaverage) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)" %(setTableName ,rep[0][0],rep[0][2], rep[0][3], rep[0][1],rep[0][4],rep[0][5],rep[0][7],rep[0][8]) )
            c.execute("select Id from %s" %setTableName)
            k=c.fetchone()[0]
            t=(pair, duration, setTableName, rep[0][0],k)
            c.execute("INSERT INTO last_checks (exchange,trading_pair, duration, table_name, last_check, last_id) VALUES('binance', ?,?, ?, ?,?)" ,t)
            conn.commit()
            return lastTime
        else:
            return lastTime  

def connection_sql(pair="BTCUSDT", duration="5m"):    
    conn= sqlite3.connect("mydb.db")
    creation_table(pair,duration,conn)
    c=conn.cursor()
    setTableName = str("binance_" + pair + "_"+ duration)
    rep=refreshDataCandle(pair,duration)    
    lastTime=rep[0][6]
    c.execute("select * from %s" %setTableName)
    if c.fetchone()==None:
        c.execute("INSERT INTO %s (date, high, low, open, close, volume, quotevolume, weightedaverage) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)" %(setTableName ,rep[0][0],rep[0][2], rep[0][3], rep[0][1],rep[0][4],rep[0][5],rep[0][7],rep[0][8]) )
        t=(pair, duration, setTableName, rep[0][0], rep[0][0],1)
        c.execute("INSERT INTO last_checks (exchange,trading_pair, duration, table_name, last_check, startdate, last_id) VALUES ('binance', ?,?, ?,?,?,?)", t )     
        conn.commit()      
    print("actualisation of candle ... press ctrl C to echap")
    while True :       
        lastTime= updateCandle(lastTime,pair, duration,setTableName, conn)
        time.sleep(30)
    conn.commit()
    conn.close()

def createOrder(api_key,secret_key, direction, price, amount, pair="BTCUSD_d",orderType="LimitOrder"):
    firstquery="symbol="+pair+"&side="+direction+"&type="+orderType+"&timeInForce=GTC&quantity="+amount+"&price="+price+"&recvWindow=5000&timestamp="+str(round(time.time() * 1000))
    a= hmac.new(bytes(secret_key,encoding='utf-8'), bytes(firstquery,encoding='utf-8'),hashlib.sha256).hexdigest()
    query="https://api.binance.com/api/v3/order?"+firstquery+"&signature="+a
    header="X-MBX-APIKEY: "+ api_key
    b= requests.Request(method='POST', url=query, headers=header)
    print(b)

def cancerOrder(api_key, secret_key, uuid):
    firstquery="symbol="+pair+"&timestamp="+str(round(time.time() * 1000))
    a= hmac.new(bytes(secret_key,encoding='utf-8'), bytes(firstquery,encoding='utf-8'),hashlib.sha256).hexdigest()
    query="https://api.binance.com/api/v3/order?"+firstquery+"&signature="+a
    header="X-MBX-APIKEY: "+ api_key
    b= requests.Request(method='DELETE', url=query, headers=header)
    print(b)

secret_key="NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j" #secret key from api binance docs, for test
api_key="vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A" #api key from api binance docs, for test

#createOrder(api_key,secret_key,"BUY","50","100")

