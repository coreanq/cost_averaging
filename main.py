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
    sigConnected = pyqtSignal()
    sigDisconnected = pyqtSignal()
    sigTryConnect = pyqtSignal()
    sigGetConditionCplt = pyqtSignal()
    sigSelectCondition = pyqtSignal()
    sigWaitingTrade = pyqtSignal()
    sigRefreshCondition = pyqtSignal()

    sigStateStop = pyqtSignal()
    sigStockComplete = pyqtSignal()

    sigConditionOccur = pyqtSignal()
    sigRequestInfo = pyqtSignal()
    sigRequestEtcInfo = pyqtSignal()

    sigGetBasicInfo = pyqtSignal()
    sigGetEtcInfo = pyqtSignal()
    sigGet5minInfo = pyqtSignal()
    sigGetHogaInfo = pyqtSignal()
    sigTrWaitComplete = pyqtSignal()

    sigBuy = pyqtSignal()
    sigNoBuy = pyqtSignal()
    sigRequestRealHogaComplete = pyqtSignal()
    sigError = pyqtSignal()
    sigRequestJangoComplete = pyqtSignal()
    sigCalculateStoplossComplete = pyqtSignal()
    sigStartProcessBuy = pyqtSignal()
    sigStopProcessBuy = pyqtSignal()
    sigTerminating = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.fsm = QStateMachine()
        self.timerRequestOrderbook = QTimer()
        self.currentTime = datetime.datetime.now()
        self.current_price = 0 # 현재 가격의 경우 매도호가 2로 정함 (1부터 시작 )
        self.crypto_market_name = 'KRW-XRP'
        self.account_info = []


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
        self.timerRequestOrderbook.setInterval(1000)
        self.timerRequestOrderbook.timeout.connect(self.onTimerRequestOrderbookTimeout) 

    @pyqtSlot()
    def onTimerRequestOrderbookTimeout(self):
        self.getOrderbook(self.crypto_market_name)
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
            if( item['currency'] == 'KRW'):
                print( round( float(item['balance']), 2 ))
            if( item['currency'] == 'XRP' ):
                print( round( float(item['balance']) * self.current_price, 2 )

    def getOrderbook(self, market_name):
        url =  server_url + "/v1/orderbook"
        querystring = {"markets": market_name }
        response = requests.request("GET", url, params=querystring)
        output_list = response.json()

        for item in output_list:
            if( len(item['orderbook_units']) == 15 ):
                # 1 매수호가
                bid_price = item[0]['bid_price']
                # 2 매수호가
                bid_price = item[1]['bid_price']
                # 현재가는 좀 낮아 보이는게 나으므로 매수호가로 처리함
                self.current_price = bid_price 
                # 2 매도호가
                # ask_price = item[1]['ask_price']

                self.getAccountInfo()

                print('ok')
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
        # print(util.whoami())
        self.timerRequestOrderbook.start()

    @pyqtSlot()
    def standbyStateEntered(self):
        print(util.whoami())

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

    # ui.btnMakeExcel.clicked.connect(objKiwoom.onBtnMakeExcelClicked )
    # ui.btnStart.clicked.connect(objKiwoom.onBtnStartClicked)

    # ui.btnYupjong.clicked.connect(objKiwoom.onBtnYupjongClicked)
    # ui.btnJango.clicked.connect(objKiwoom.onBtnJangoClicked)
    # ui.btnChegyeol.clicked.connect(objKiwoom.onBtnChegyeolClicked)
    # ui.btnCondition.clicked.connect(objKiwoom.onBtnConditionClicked)

    # ui.lineCmd.textChanged.connect(objKiwoom.onLineCmdTextChanged)
    # ui.btnRun.clicked.connect(objKiwoom.onBtnRunClicked)
    form.show()

    # obj.getAccountInfo()
    # obj.getOrderbook(["KRW-XRP"])
    # obj.getOrderbook(["KRW-BTC","KRW-XRP"])

    sys.exit(myApp.exec_())