import os, sys, json, datetime
import util
import UpbitWrapper

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtCore import QObject, Slot, Signal, QUrl, QEvent, QTimer
from PySide6.QtStateMachine import QStateMachine, QState, QFinalState
from PySide6.QtWidgets import QApplication
from mainwindow_ui import Ui_MainWindow


class UpbitRebalancing(QObject):
    sigInitOk = Signal()
    sigError = Signal()
    sigStateStop = Signal()
    sigCryptoPercentChanged = Signal(str)
    sigFiatPercentChanged = Signal(str)

    sigCryptoBalanceChanged = Signal(str)
    sigFiatBalanceChanged = Signal(str)
    sigCurrentBalanceChanged = Signal(float, float)

    sigStyleSheetChanged = Signal(str)

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
        self.tradeOn = False



    def init(self):
        self.timerRequestOrderbook.setInterval(1000)
        self.timerRequestOrderbook.timeout.connect(self.onTimerRequestOrderbookTimeout) 

        self.timerRequestAccountInfo.setInterval(2000)
        self.timerRequestAccountInfo.timeout.connect(self.onTimerRequestAccountInfoTimeout) 

    @Slot()
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

    @Slot()
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
                    fiat_balance = round( float(item[balance_key]), 2 ) + self.external_wallet_amount
                    fiat_balance = fiat_balance + round( float(item[locked_key]), 2 )

                    # 매수 매도 진행 중이여서 잔고 정보가 업데이트 중이라면 리밸런싱 금지 
                    if( round( float(item[locked_key]), 2  > 100 ) ):
                        isLocked = True

                if( item[currency_key] == 'XRP' ):
                    #낮은게 좋으므로 매수 호가 기준으로 삼음
                    crypto_balance = round( float(item[balance_key]),  2 )
                    crypto_balance = crypto_balance + round( float(item[locked_key]),  2 )

                    # 매수 매도 진행 중이여서 잔고 정보가 업데이트 중이라면 리밸런싱 금지 
                    if( round( float(item[locked_key]), 2  > 100 ) ):
                        isLocked = True

            if( isLocked == True ):
                return

            # self.processShannonsDemonRebalance(fiat_balance, crypto_balance)


            #WARNING: 현금으로 매수 후 잔고 정보 조회시 crypto 잔고가 바로 업데이트 되지 않느 오류가 있으므로 주의 
            # 현재 거래 진행중이면 make order 수행 금지 
            if( self.upbitIf.hasWaitInOrder() == False ):
                
                if( fiat_balance > self.current_bid_price and fiat_balance > 5000 ): # 최소 주문 금액 충족 확인 
                    maemae_type = "매수"
                    order_type = 'bid'
                    order_price = self.current_bid_price
                    order_balance = fiat_balance * 0.9995  # 수수료 고려 제외 시킴 

                    if( self.tradeOn == True ):
                        printLog = '{} {} {} {}\n'.format( util.cur_time_msec(), maemae_type, order_price, order_balance ) 
                        print( printLog )
                        util.save_log( printLog, subject= "{} 요청".format( maemae_type ) )

                        print('잔고: \n{}\n'.format( json.dumps( self.current_account_info, indent=2, sort_keys=True) ) )
                        self.upbitIf.makeOrder(order_type, order_price, order_balance, False)
            else:
                print("\nMake Order avaliable {}".format( self.upbitIf.wait_order_uuids))

        pass

    def processShannonsDemonRebalance(self, fiat_balance, crypto_balance):

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

        self.sigCryptoBalanceChanged.emit('{:,.2f}({})'.format(crypto_balance, self.current_price) )
        self.sigFiatBalanceChanged.emit( '{:,.0f}'.format(fiat_balance) )

        self.sigCurrentBalanceChanged.emit(fiat_balance, crypto_balance)

        order_price = 0
        # 현재 거래 진행중인 거래 확인  
        self.upbitIf.getOrder()
        

        # 매수  
        if( order_type == 'bid' ):
            order_price = self.current_ask_price
        # 매도 
        elif( order_type == 'ask' ):
            order_price = self.current_bid_price
        else: # none
            return

        #WARNING: 현금으로 매수 후 잔고 정보 조회시 crypto 잔고가 바로 업데이트 되지 않느 오류가 있으므로 주의 
        # 현재 거래 진행중이면 make order 수행 금지 
        if( self.upbitIf.hasWaitInOrder() == False ):

            maemaeType = ''
            if( order_type == 'bid' ):
                maemaeType = '매수'
            else:
                maemaeType = '매도'

            if( self.tradeOn == True ):
                self.upbitIf.makeOrder(order_type, order_price, order_balance, False)

                printLog = '{} {} {} {}\n'.format( util.cur_time_msec(), maemaeType, order_price, order_balance ) 
                print( printLog )
                util.save_log( printLog, subject= "{} 요청".format( maemaeType ) )

                print('잔고: \n{}\n'.format( json.dumps( self.current_account_info, indent=2, sort_keys=True) ) )
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

    @Slot()
    def mainStateEntered(self):
        # print(util.whoami())
        pass

    @Slot()
    def initStateEntered(self):
        print(util.whoami())
        self.timerRequestOrderbook.start()
        self.timerRequestAccountInfo.stop()
        self.sigStyleSheetChanged.emit(
            " QMainWindow {"
                        " background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ff0000, stop: 1 #ffff00); "
                        "}" 
            )
    @Slot()
    def standbyStateEntered(self):
        print(util.whoami())
        self.timerRequestAccountInfo.start()
        self.sigStyleSheetChanged.emit(
            " QMainWindow {"
                       " background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #007f00, stop: 1 #aaffaa); "
                        "}" 
            )

    @Slot()
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

    myApp = QtWidgets.QApplication(sys.argv)
    obj = UpbitRebalancing(secret_key, access_key, server_url, external_wallet_amount)

    form = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(form)

    def onChkShowBalanceStateChanged(btnChkState):
        if( Qt.CheckState(btnChkState) == Qt.CheckState.Checked ):
            ui.lblCryptoBalance.setHidden(False)
            ui.lblFiatBalance.setHidden(False)
            ui.lblOriBalance.setHidden(False)
        else:
            ui.lblCryptoBalance.setHidden(True)
            ui.lblFiatBalance.setHidden(True)
            ui.lblOriBalance.setHidden(True)

    def onChkTradeOnStateChanged(btnChkState):
        if( Qt.CheckState(btnChkState) == Qt.CheckState.Checked ):
            obj.tradeOn = True
        else:
            obj.tradeOn = False
    
    def onStyleSheetChanged(strStyleSheet):
        myApp.setStyleSheet(strStyleSheet)

    def onCurrentCurrentBalanceChanged(fFiatBalance, fCryptoBalance):
        total_balance = fFiatBalance  + fCryptoBalance * obj.current_price 
        ui.lblOriBalance.setText( '{:,.0f}'.format( total_balance ))
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
    ui.chkTradeOn.stateChanged.connect( onChkTradeOnStateChanged )

    form.show()

    sys.exit(myApp.exec())