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


def test_rebalance_simulate(UpbitObj):

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
