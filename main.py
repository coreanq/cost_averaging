import os, sys, json, datetime
import jwt
import uuid
import hashlib
import util

from urllib.parse import urlencode
import requests
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QUrl, QEvent
from PyQt5.QtCore import QStateMachine, QState, QTimer, QFinalState
from PyQt5.QtWidgets import QApplication
from mainwindow_ui import Ui_MainWindow

with open("access_info.json", "r") as json_file:
    access_info = json.loads(json_file.read())

access_key = access_info["access_key"]
secret_key = access_info["secret_key"]
server_url = "https://api.upbit.com"


class UpbitRebalancing(QObject):
    sigInitOk = pyqtSignal()
    sigError = pyqtSignal()
    sigStateStop = pyqtSignal()
    sigCryptoPercentChanged = pyqtSignal(str)
    sigFiatPercentChanged = pyqtSignal(str)

    sigCryptoBalanceChanged = pyqtSignal(str)
    sigFiatBalanceChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.fsm = QStateMachine()
        self.timerRequestOrderbook = QTimer()
        self.timerRequestAccountInfo = QTimer()
        self.currentTime = datetime.datetime.now()

        self.current_ask_price = 0         
        self.current_bid_price = 0 # 현재 가격의 경우 매수호가 2로 정함 (1부터 시작 )

        self.crypto_market_name = 'KRW-XRP'
        self.account_info = []
        self.fiat_balance = 0
        self.crypto_balance = 0

        self.fiat_percent = 0
        self.crypto_percent = 0


        self.init()
        self.createState()




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
    def init(self):
        self.timerRequestOrderbook.setInterval(500)
        self.timerRequestOrderbook.timeout.connect(self.onTimerRequestOrderbookTimeout) 

        self.timerRequestAccountInfo.setInterval(2000)
        self.timerRequestAccountInfo.timeout.connect(self.onTimerRequestAccountInfoTimeout) 

    @pyqtSlot()
    def onTimerRequestOrderbookTimeout(self):
        self.getOrderbook(self.crypto_market_name)
        pass

    @pyqtSlot()
    def onTimerRequestAccountInfoTimeout(self):
        self.getAccountInfo()
        pass


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
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
        }

        jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        response = requests.get(server_url + "/v1/accounts", headers=headers)

        self.account_info = response.json()
        # print(json.dumps(response.json(), indent=2, sort_keys=True))
        # print(type(self.account_info))

        self.checkAccountInfo()

    def checkAccountInfo(self):
        account_info = self.account_info

        for item in account_info:
            currency_key = 'currency'
            balance_key = 'balance'
            if( item[currency_key] == 'KRW'):
                self.fiat_balance = round( float(item[balance_key]), 2 )
            if( item[currency_key] == 'XRP' ):
                #낮은게 좋으므로 매수 호가 기준으로 삼음
                self.crypto_balance = round( float(item[balance_key]) * self.current_price, 2 ) 

        if( self.fiat_balance == 0 or self.crypto_balance == 0 ):
            return 


        balance_sum = self.fiat_balance + self.crypto_balance
        fiat_percent = round(self.fiat_balance/balance_sum * 100, 2)
        crypto_percent = round(self.crypto_balance/balance_sum * 100, 2) 
        self.fiat_percent = fiat_percent
        self.crypto_percent = crypto_percent

        self.sigCryptoPercentChanged.emit( str(crypto_percent) + "%" )
        self.sigFiatPercentChanged.emit( str(fiat_percent) + "%" )

        self.sigCryptoBalanceChanged.emit( str(self.crypto_balance) )
        self.sigFiatBalanceChanged.emit( str(self.fiat_balance) )

        if( abs(fiat_percent - crypto_percent) > 2 ):
            if( fiat_percent > crypto_percent ):

                # 현금 비중이 높은 경우 
                order_balance = round((self.fiat_balance - self.crypto_balance) / 2) 
                #buy
                self.rebalancing('bid', order_balance)
            else:
                # 암호화폐 비중이 높은 경우
                #sell
                order_balance = round((self.crypto_balance - self.fiat_balance) /2 )
                self.rebalancing('ask', order_balance )

            print( 'fiat: {} %, crypto {} %, rebalance amount {}'.format(
                fiat_percent
                ,crypto_percent
                ,order_balance
            ))



    def rebalancing(self, side, order_balance):
        print(util.whoami() )
        query = ''
        volume = 2.5 # for test
        if( side == 'bid' ):
            # 암호화폐 매수 매도호가 기준 
            volume = round(order_balance / self.current_ask_price, 2)
            query = {
                'market': 'KRW-XRP',
                'side': 'bid',
                'volume': volume,
                'price': str(self.current_ask_price),
                'ord_type': 'limit',
            }
        else:
            # 암호화폐 매도므로 매수호가 기준
            volume = round(order_balance / self.current_bid_price, 2)
            query = {
                'market': 'KRW-XRP',
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

        response = requests.post(server_url + "/v1/orders", params=query, headers=headers)
        print(json.dumps( response.json(), indent=2, sort_keys=True) )
        pass



    def getOrderbook(self, market_name):
        url =  server_url + "/v1/orderbook"
        querystring = {"markets": market_name }
        response = requests.request("GET", url, params=querystring)
        output_list = response.json()

        for item in output_list:
            orderbook_key = 'orderbook_units'
            bid_price_key = 'bid_price'
            ask_price_key = 'ask_price'
            if( len(item[orderbook_key]) == 15 ):
                # 1 매수호가 낮은 가격이 좋으므로 매수 1호가 기준으로 현재 가격 결정함
                self.current_price = item[orderbook_key][0][bid_price_key]
                # 2 매수호가
                bid_price = item[orderbook_key][1][bid_price_key]
                # 현재가는 좀 낮아 보이는게 나으므로 매수호가로 처리함
                self.current_bid_price = bid_price 

                # 1 매도호가
                ask_price = item[orderbook_key][0][ask_price_key]
                # 2 매도호가
                ask_price = item[orderbook_key][1][ask_price_key]
                self.current_ask_price = ask_price
                self.sigInitOk.emit()
            else:
                self.sigError.emit()

            pass
        # print(json.dumps( response.json(), indent=2, sort_keys=True) )



        
    def createState(self):
        # state defintion
        mainState = QState(self.fsm)       
        finalState = QFinalState(self.fsm)
        self.fsm.setInitialState(mainState)
        
        initState = QState(mainState)
        standbyState = QState(mainState)

        #transition defition
        mainState.setInitialState(initState)
        mainState.addTransition(self.sigStateStop, finalState)


        initState.addTransition(self.sigInitOk, standbyState)
        standbyState.addTransition(self.sigError, initState)

        # #state entered slot connect
        mainState.entered.connect(self.mainStateEntered)
        initState.entered.connect(self.initStateEntered)
        standbyState.entered.connect(self.standbyStateEntered)
        finalState.entered.connect(self.finalStateEntered)

        #fsm start
        self.fsm.start()

        pass

    @pyqtSlot()
    def mainStateEntered(self):
        # print(util.whoami())
        pass

    @pyqtSlot()
    def initStateEntered(self):
        print(util.whoami())
        self.timerRequestOrderbook.start()
        self.timerRequestAccountInfo.stop()

    @pyqtSlot()
    def standbyStateEntered(self):
        print(util.whoami())
        self.timerRequestAccountInfo.start()

    @pyqtSlot()
    def finalStateEntered(self):
        print(util.whoami())

if __name__ == "__main__":
    # putenv 는 current process 에 영향을 못끼치므로 environ 에서 직접 세팅 
    # print(os.environ['QML_IMPORT_TRACE'])
    myApp = QtWidgets.QApplication(sys.argv)
    obj = UpbitRebalancing()

    form = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(form)


    obj.sigCryptoBalanceChanged.connect(ui.lblCryptoBalance.setText)
    obj.sigCryptoPercentChanged.connect(ui.lblCryptoPercent.setText)

    obj.sigFiatBalanceChanged.connect(ui.lblFiatBalance.setText)
    obj.sigFiatPercentChanged.connect(ui.lblFiatPercent.setText)

    form.show()

    # obj.getAccountInfo()
    # obj.getOrderbook(["KRW-XRP"])
    # obj.getOrderbook(["KRW-BTC","KRW-XRP"])

    sys.exit(myApp.exec_())