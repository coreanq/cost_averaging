import os, sys, json, datetime
import jwt
import uuid
import hashlib
import util

from urllib.parse import urlencode
import requests
import UpbitWrapper

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QUrl, QEvent
from PyQt5.QtCore import QStateMachine, QState, QTimer, QFinalState
from PyQt5.QtWidgets import QApplication
from mainwindow_ui import Ui_MainWindow


class UpbitRebalancing(QObject):
    sigInitOk = pyqtSignal()
    sigError = pyqtSignal()
    sigStateStop = pyqtSignal()
    sigCryptoPercentChanged = pyqtSignal(str)
    sigFiatPercentChanged = pyqtSignal(str)

    sigCryptoBalanceChanged = pyqtSignal(str)
    sigFiatBalanceChanged = pyqtSignal(str)
    sigCurrentBalanceChanged = pyqtSignal(float, float)

    sigStyleSheetChanged = pyqtSignal(str)

    def __init__(self, 
        secret_key, access_key, server_url, 
        external_wallet_amount
        ):
        super().__init__()

        self.fsm = QStateMachine()
        self.timerRequestOrderbook = QTimer()
        self.timerRequestAccountInfo = QTimer()
        self.currentTime = datetime.datetime.now()

        self.init()
        self.createState()

        self.upbitIf = UpbitWrapper.UpbitWrapper(secret_key, access_key, server_url, 'KRW-XRP')
        self.current_price = 0
        self.current_ask_price = 0
        self.current_bid_price = 0
        self.external_wallet_amount = external_wallet_amount
        self.current_account_info = 0 



    def init(self):
        self.timerRequestOrderbook.setInterval(300)
        self.timerRequestOrderbook.timeout.connect(self.onTimerRequestOrderbookTimeout) 

        self.timerRequestAccountInfo.setInterval(2000)
        self.timerRequestAccountInfo.timeout.connect(self.onTimerRequestAccountInfoTimeout) 

    @pyqtSlot()
    def onTimerRequestOrderbookTimeout(self):
        output_list = self.upbitIf.getOrderbook()
        if( output_list == None ):
            self.sigError.emit()
            return

        for item in output_list:
            orderbook_key = 'orderbook_units'
            bid_price_key = 'bid_price'
            ask_price_key = 'ask_price'
            # 매수/매도 호가가 15호가 정보로 정확히 온경우 
            if( len(item[orderbook_key]) == 15 ):
                # print(item[orderbook_key])
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

                # 현재 계좌 정보 저장
                self.current_ask_price = ask_price
                self.sigInitOk.emit()
            else:
                self.sigError.emit()

        pass

    @pyqtSlot()
    def onTimerRequestAccountInfoTimeout(self):
        self.current_account_info = self.upbitIf.getAccountInfo()
        if( self.current_account_info == None ):
            self.sigError.emit()
            return

        crypto_balance = 0
        fiat_balance = 0
        isLocked = False

        if( len(self.current_account_info) != 0 ) :
            for item in self.current_account_info:
                currency_key = 'currency'
                balance_key = 'balance'
                locked_key  = 'locked'


                if( item[currency_key] == 'KRW'):
                    fiat_balance = round( float(item[balance_key]), 2 )
                    fiat_balance = fiat_balance + round( float(item[locked_key]), 2 )

                    # 매수 매도 진행 중이여서 잔고 정보가 업데이트 중이라면 리밸런싱 금지 
                    if( round( float(item[locked_key]), 2  > 100 ) ):
                        isLocked = True

                if( item[currency_key] == 'XRP' ):
                    #낮은게 좋으므로 매수 호가 기준으로 삼음
                    crypto_balance = round( float(item[balance_key]),  2 ) + self.external_wallet_amount
                    crypto_balance = crypto_balance + round( float(item[locked_key]),  2 )

                    # 매수 매도 진행 중이여서 잔고 정보가 업데이트 중이라면 리밸런싱 금지 
                    if( round( float(item[locked_key]), 2  > 100 ) ):
                        isLocked = True

            if( isLocked == True ):
                return

            result = self.upbitIf.checkAssetInfo(fiat_balance, self.current_price, crypto_balance)

            if( result == None ):
                self.sigError.emit()

            order_type = result['order_type']
            order_balance = result['order_balance']

            balance_sum = fiat_balance + crypto_balance * self.current_price
            fiat_percent = round(fiat_balance/balance_sum * 100, 2)
            crypto_percent = round( (crypto_balance * self.current_price )/balance_sum * 100, 2) 

            self.sigCryptoPercentChanged.emit( str(crypto_percent) + "%" )
            self.sigFiatPercentChanged.emit( str(fiat_percent) + "%" )

            self.sigCryptoBalanceChanged.emit('{:,.1f}'.format(crypto_balance) )
            self.sigFiatBalanceChanged.emit( '{:,.1f}'.format(fiat_balance) )

            self.sigCurrentBalanceChanged.emit(fiat_balance, crypto_balance)

            order_price = 0
            # 현재 거래 진행중인 거래 확인  
            self.upbitIf.getOrder()
            
            if( order_type == 'bid' ):
                order_price = self.current_ask_price
            elif( order_type == 'ask' ):
                order_price = self.current_bid_price
            else: # none
                return

            #WARNING: 현금으로 매수 후 잔고 정보 조회시 crypto 잔고가 바로 업데이트 되지 않느 오류가 있으므로 주의 
            # 현재 거래 진행중이면 make order 수행 금지 
            if( self.upbitIf.hasWaitInOrder() == False ):
                print('{} {} {} {}\n'.format( util.whoami(),  order_type, order_price, order_balance ) )
                print('{} \n{}\n'.format( util.whoami(), json.dumps( self.current_account_info, indent=2, sort_keys=True) ) )
                self.upbitIf.makeOrder(order_type, order_price, order_balance, False)
            else:
                print("\nMake Order pass {}".format( self.upbitIf.wait_order_uuids))

        pass
        
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
        self.sigStyleSheetChanged.emit(
            " QMainWindow {"
                        " background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ff0000, stop: 1 #ffff00); "
                        "}" 
            )
    @pyqtSlot()
    def standbyStateEntered(self):
        print(util.whoami())
        self.timerRequestAccountInfo.start()
        self.sigStyleSheetChanged.emit(
            " QMainWindow {"
                       " background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #007f00, stop: 1 #aaffaa); "
                        "}" 
            )

    @pyqtSlot()
    def finalStateEntered(self):
        print(util.whoami())

if __name__ == "__main__":
    # putenv 는 current process 에 영향을 못끼치므로 environ 에서 직접 세팅 
    # print(os.environ['QML_IMPORT_TRACE'])

    with open("auth/access_info.json", "r") as json_file:
        access_info = json.loads(json_file.read())

    access_key = access_info["access_key"]
    secret_key = access_info["secret_key"]
    server_url = "https://api.upbit.com"


    # 외부 개인지갑 암호화폐 보유 갯수 
    external_wallet_amount = access_info['external_wallet_amount']
    fOriginalFiatBalance = access_info["original_fiat_balance"]

    myApp = QtWidgets.QApplication(sys.argv)
    obj = UpbitRebalancing(secret_key, access_key, server_url, external_wallet_amount)

    form = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(form)

    def onChkShowBalanceStateChanged(btnChkState):
        if( btnChkState == Qt.Checked ):
            ui.lblCryptoBalance.setHidden(False)
            ui.lblFiatBalance.setHidden(False)
            ui.lblOriBalance.setHidden(False)
        else:
            ui.lblCryptoBalance.setHidden(True)
            ui.lblFiatBalance.setHidden(True)
            ui.lblOriBalance.setHidden(True)
    
    def onStyleSheetChanged(strStyleSheet):
        myApp.setStyleSheet(strStyleSheet)


    # 기존 투입 자산 대비 현재 얼마나 가치를 가지고 있나 측정 
    # access_info 의 original_fiat_balance 의 경우 추가 금액을 입금할 경우 그 금액만큼 수동으로 늘려준다 
    # 기존 투입 금액의 반보다 현재 보유한 fiatbalance 가 크다면 수익이고 아니면 손해지만 crypto balance 가 늘어난 상태임 
    def onCurrentCurrentBalanceChanged(fFiatBalance, fCryptoBalance):
        fCurrentFiatBalance = round( fFiatBalance, 3)
        fCurrentCryptoBalance = round( fCryptoBalance, 3)

        result =  str( round((fCurrentFiatBalance / (fOriginalFiatBalance / 2) ) * 100, 2 ) )
        ui.lblOriPercent.setText( result + '%' )
        ui.lblOriBalance.setText( '{:,.1f}'.format( fOriginalFiatBalance ))
        pass

    obj.sigCryptoBalanceChanged.connect(ui.lblCryptoBalance.setText)
    obj.sigCryptoPercentChanged.connect(ui.lblCryptoPercent.setText)

    obj.sigFiatBalanceChanged.connect(ui.lblFiatBalance.setText)
    obj.sigFiatPercentChanged.connect(ui.lblFiatPercent.setText)

    obj.sigCurrentBalanceChanged.connect(onCurrentCurrentBalanceChanged)

    obj.sigStyleSheetChanged.connect(onStyleSheetChanged)

    ui.lblCryptoBalance.setHidden(True)
    ui.lblFiatBalance.setHidden(True)
    ui.lblOriBalance.setHidden(True)

    ui.chkShowBalance.stateChanged.connect( onChkShowBalanceStateChanged )

    form.show()

    sys.exit(myApp.exec_())