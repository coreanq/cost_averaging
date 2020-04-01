import os, sys, json, datetime
import jwt
import uuid
import hashlib
import util

from urllib.parse import urlencode
import requests

'''
20200327
EXCHANGE API
[주문]
초당 8회, 분당 200회

[주문 외 API]
초당 30회, 분당 900회

[Exchange API 추가 안내 사항]

QUOTATION API
1) Websocket 연결 요청 수 제한
초당 5회, 분당 100회

2) REST API 요청 수 제한
분당 600회, 초당 10회 (종목, 캔들, 체결, 티커, 호가별)
'''
class UpbitWrapper():
    def __init__(self, secret_key, access_key, server_url, market_code):

        self.access_key = access_key 
        self.secret_key = secret_key 
        self.server_url = server_url

        self.market_code =  market_code
        self.account_info = []
        self.rebalance_start_percent = 2 

    def setRebalance_percent(self, iPercent):
        self.rebalance_start_percent = iPercent
    
    def checkAssetInfo(self, fiat_balance, current_crypto_price, crypto_balance):

        if( fiat_balance == 0 or current_crypto_price == 0 ):
            return None

        balance_sum = fiat_balance + crypto_balance * current_crypto_price
        fiat_percent = round(fiat_balance/balance_sum * 100, 2)
        crypto_percent = round( (crypto_balance * current_crypto_price )/balance_sum * 100, 2) 

        # print( 'fiat: {}[{} %], crypto price: {} amount: {} [{} %]'.format(
        #     fiat_balance
        #     ,fiat_percent
        #     ,current_crypto_price
        #     ,crypto_balance
        #     ,crypto_percent
        # ))

        if( abs(fiat_percent - crypto_percent) > self.rebalance_start_percent ):
            if( fiat_percent > crypto_percent ):
                # 현금 비중이 높은 경우 
                #buy
                order_balance = round((fiat_balance - crypto_balance * current_crypto_price) )  / 2 
                return { "order_type": 'bid', "order_balance": order_balance }
            else:
                # 암호화폐 비중이 높은 경우
                #sell
                order_balance = round((crypto_balance * current_crypto_price - fiat_balance ) ) / 2 
                return { "order_type": 'ask', "order_balance": order_balance }

        else:
            return {"order_type": "none", "order_balance": 0} 


    '''
    [
        {
            "avg_buy_price": "0",
            "avg_buy_price_modified": true,
            "balance": "2.27593723",
            "currency": "KRW",
            "locked": "0.0",
            "unit_currency": "KRW"
        },
        {
            "avg_buy_price": "217.4",
            "avg_buy_price_modified": false,
            "balance": "1.13438041",
            "currency": "XRP",
            "locked": "0.0",
            "unit_currency": "KRW"
        }
    ]
    '''
    def getAccountInfo(self):
        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
        }

        jwt_token = jwt.encode(payload, self.secret_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        url = self.server_url + "/v1/accounts" 

        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.SSLError:
            print("ssl error")
            return None 
        except:
            print("except")
            return None 
        else:
            if( response.status_code != 200):
                print("error return")
                return None 
            else:
                output_list = response.json()
                return output_list



    def makeOrder(self, order_type, order_price, order_balance, test = True):
        query = ''
        volume = 0 # for test
        if( order_type == 'none'):
            return None

        if( order_type == 'bid' ):
            # 암호화폐 매수,매도호가 기준 
            volume = round(order_balance / order_price, 2)
            query = {
                'market': self.market_code,
                'side': 'bid',
                'volume': volume,
                'price': str(order_price),
                'ord_type': 'limit',
            }
        else:
            # 암호화폐 매도,매수호가 기준
            volume = round(order_balance / order_price, 2)
            query = {
                'market': self.market_code,
                'side': 'ask',
                'volume': volume,
                'price': str(order_price),
                'ord_type': 'limit',
            }

        print(query)

        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        url = self.server_url + "/v1/orders"
        try:
            pass
            if( test == True ):
                query = ''
            response = requests.post( url, params=query, headers=headers)
            pass
        except requests.exceptions.SSLError:
            print("ssl error")
            return None 
        except:
            print("except")
            return None 
        else:
            if( response.status_code != 200):
                print("\n\nerror return: \n{}\n{}".format(query, response.text ) )
                return None 
            else:
                output_list = response.json()
                print(json.dumps( response.json(), indent=2, sort_keys=True) )
        pass


    def getOrderbook(self):
        url = self.server_url + "/v1/orderbook"
        query = {"markets": self.market_code }

        try:
            response = requests.get( url, params= query)
        except requests.exceptions.SSLError:
            print("ssl error")
            return None
        except:
            print("except")
            return None 
        else:
            if( response.status_code != 200):
                print("error return: \n{}\n{}".format(query, response.text ) )
                return None 
            else:
                output_list = response.json()
                # print(json.dumps( output_list, indent=2, sort_keys=True) )
                return output_list

    # 최대 200 개까지 가능 
    def getDayCandle(self, max_count):
        url = self.server_url + "/v1/candles/days"
        query = {"market": self.market_code, "count": str(max_count) }

        try:
            response = requests.get( url, params= query)
        except requests.exceptions.SSLError:
            print("ssl error")
            return None
        except:
            print("except")
            return None
        else:
            if( response.status_code != 200):
                print("error return: \n{}\n{}".format(query, response.text ) )
                self.sigError.emit()
                return None 
            else:
                output_list = response.json()
                return output_list

