import pytest
import json
import datetime

@pytest.fixture
def UpbitObj(MarketCode):
    import UpbitWrapper  
    # with open("access_info.json", "r") as json_file:
    #     access_info = json.loads(json_file.read())

    # access_key = access_info["access_key"]
    # secret_key = access_info["secret_key"]
    # server_url = "https://api.upbit.com"
    obj = UpbitWrapper.UpbitWrapper('', '', '', MarketCode)
    return obj

@pytest.fixture
def MarketCode():
    return "KRW-XRP"


def test_rebalance_normal_simulate(UpbitObj):

    fiat_balance = 10000000
    crypto_balance = 0

    iStartPrice = 1000
    iEndPrice = 100

    result = UpbitObj.simulateReblance(fiat_balance, crypto_balance, iStartPrice, iEndPrice)
    result_fiat = result['fiat_balance']
    result_crypto = result['crypto_balance']

    print( "shannon remain fiat {}, crypto {}, original price total {} expected price total {}\n".format( 
        round( result_fiat )
        ,round(iStartPrice * result_crypto )
        ,round(iEndPrice * result_crypto + result_fiat)
        ,round(iStartPrice * result_crypto + result_fiat)
        )
    )

    # fiat_balance = 10000000
    # crypto_balance = 0

    fiat_balance = result_fiat
    crypto_balance = result_crypto 

    iStartPrice = 100
    iEndPrice = 1000


    result = UpbitObj.simulateReblance(fiat_balance, crypto_balance, iStartPrice, iEndPrice)
    result_fiat = result['fiat_balance']
    result_crypto = result['crypto_balance']

    print( "shannon remain fiat {}, crypto {}, price total {}\n".format( 
        round( result_fiat )
        ,round(iEndPrice * result_crypto )
        ,round(iEndPrice * result_crypto + result_fiat)
        )
    )


    pass

def test_rebalance_xrp_simulate(UpbitObj):

    price_list = []
    with open("xrp_day_candles.json", "r") as json_file:
        price_list = json.load(json_file)

    fiat_balance = 10000000
    crypto_balance = 0

    price_histroy_info = []
    for item_list in reversed(price_list):
        price_histroy_info.append( item_list['opening_price'] )
        price_histroy_info.append( item_list['high_price'] )
        price_histroy_info.append( item_list['low_price'] )
        price_histroy_info.append( item_list['trade_price'] )


    # 시작가 설정 
    while( True ):
        if( price_histroy_info[0] <= 2100 ):
            break
        price_histroy_info.pop(0)

    # open - high - low - close
    while (len(price_histroy_info ) > 1 ):
        iStartPrice = price_histroy_info[0]
        iEndPrice = price_histroy_info[1]

        result = UpbitObj.simulateReblance(fiat_balance, crypto_balance, int(iStartPrice), int(iEndPrice) )
        fiat_balance = result['fiat_balance']
        crypto_balance = result['crypto_balance']
        price_histroy_info.pop(0)

    print( "shannon remain fiat {}, crypto {}, price total {}\n".format( 
        round( fiat_balance )
        ,round( crypto_balance )
        ,round(iEndPrice * crypto_balance + fiat_balance)
        )
    )


    pass

