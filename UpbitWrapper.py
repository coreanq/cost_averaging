import os, sys, json, datetime
import jwt
import uuid
import hashlib
import util

from urllib.parse import urlencode
import requests
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QUrl, QEvent
from PyQt5.QtCore import QStateMachine, QState, QTimer, QFinalState
from PyQt5.QtWidgets import QApplication
from mainwindow_ui import Ui_MainWindow


class UpbitWrapper(QObject):

    def __init__(self, secret_key, access_key, server_url, market_code):
        super().__init__()

        self.access_key = access_key 
        self.secret_key = secret_key 
        self.server_url = server_url

        self.market_code =  market_code
        self.account_info = []
        self.rebalance_start_percent = 2

    
    def checkAssetInfo(self, fiat_balance, current_crypto_price, crypto_balance):

        if( fiat_balance == 0 or current_crypto_price == 0 ):
            return {} 

        balance_sum = fiat_balance + crypto_balance * current_crypto_price
        fiat_percent = round(fiat_balance/balance_sum * 100, 2)
        crypto_percent = round( (crypto_balance * current_crypto_price )/balance_sum * 100, 2) 

        print( 'fiat: {} %, crypto {} %'.format(
            fiat_percent
            ,crypto_percent
        ))

        if( abs(fiat_percent - crypto_percent) > self.rebalance_start_percent ):
            if( fiat_percent > crypto_percent ):
                # 현금 비중이 높은 경우 
                #buy
                order_balance = round((fiat_balance - crypto_balance) )  / 2 
                return { "type": 'bid', "order_balance": order_balance }
            else:
                # 암호화폐 비중이 높은 경우
                #sell
                order_balance = round((crypto_balance - fiat_balance) ) / 2 
                return { "type": 'ask', "order_balance": order_balance }

            print( 'fiat: {} %, crypto {} %, rebalance amount {}'.format(
                fiat_percent
                ,crypto_percent
                ,order_balance / 2
            ))
        else:
            return {"type": "none", "order_balance": 0} 


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
            self.sigError.emit()
            return []
        except:
            print("except")
            self.sigError.emit()
            return []
        else:
            if( response.status_code != 200):
                print("error return")
                self.sigError.emit()
                return []
            else:
                output_list = response.json()
                return output_list



    def rebalancing(self, side, order_balance):
        print(util.whoami() )
        query = ''
        volume = 2.5 # for test
        if( side == 'bid' ):
            # 암호화폐 매수,매도호가 기준 
            volume = round(order_balance / self.current_ask_price, 2)
            query = {
                'market': self.market_code,
                'side': 'bid',
                'volume': volume,
                'price': str(self.current_ask_price),
                'ord_type': 'limit',
            }
        else:
            # 암호화폐 매도,매수호가 기준
            volume = round(order_balance / self.current_bid_price, 2)
            query = {
                'market': self.market_code,
                'side': 'ask',
                'volume': volume,
                'price': str(self.current_bid_price),
                'ord_type': 'limit',
            }

        print(query)

        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        url = server_url + "/v1/orders"
        try:
            response = requests.post( url, params=query, headers=headers)
        except requests.exceptions.SSLError:
            print("ssl error")
            self.sigError.emit()
            return []
        except:
            print("except")
            self.sigError.emit()
            return []
        else:
            if( response.status_code != 200):
                print("error return: \n{}\n{}".format(query, response.text ) )
                self.sigError.emit()
                return []
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
            self.sigError.emit()
            return []
        except:
            print("except")
            self.sigError.emit()
            return []
        else:
            if( response.status_code != 200):
                print("error return: \n{}\n{}".format(query, response.text ) )
                self.sigerror.emit()
                return []
            else:
                output_list = response.json()
                # print(json.dumps( output_list, indent=2, sort_keys=True) )
                return output_list

    def getDayCandle(self, max_count):
        url = self.server_url + "/v1/candles/days"
        query = {"market": self.market_code, "count": str(max_count) }

        try:
            response = requests.get( url, params= query)
        except requests.exceptions.SSLError:
            print("ssl error")
            self.sigError.emit()
            return []
        except:
            print("except")
            self.sigError.emit()
            return []
        else:
            if( response.status_code != 200):
                print("error return: \n{}\n{}".format(query, response.text ) )
                self.sigError.emit()
                return []
            else:
                output_list = response.json()
                return output_list

