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

    for current_crypto_price in range(1000, 100, -1):
        result_list = UpbitObj.checkAssetInfo(fiat_balance, current_crypto_price, crypto_balance)
        assert "order_type" in result_list


        trade_type = result_list['order_type']
        order_balance = result_list['order_balance']

        # buy
        if( trade_type == 'bid' ):
            order_balance = order_balance * 0.9995 # 수수료
            crypto_balance += round(order_balance / current_crypto_price, 2)
            fiat_balance -= order_balance
            pass
        elif ( trade_type == 'ask' ):
            order_balance = order_balance * 0.9995 # 수수료
            crypto_balance -= round(order_balance / current_crypto_price, 2)
            fiat_balance += order_balance
            pass
        else:
            continue
        pass

    print( "shannon remain fiat {}, crypto price 100 {} total {}".format( 
        round(fiat_balance)
        ,round(1000 * crypto_balance)
        ,round(1000 * crypto_balance + fiat_balance)
        )
    )

    for current_crypto_price in range(100, 1000, 1):
        result_list = UpbitObj.checkAssetInfo(fiat_balance, current_crypto_price, crypto_balance)
        assert "order_type" in result_list


        trade_type = result_list['order_type']
        order_balance = result_list['order_balance']

        # buy
        if( trade_type == 'bid' ):
            # print('bid ', sep='')
            order_balance = order_balance * 0.9995 # 수수료
            crypto_balance += round(order_balance / current_crypto_price, 2)
            fiat_balance -= order_balance
            pass
        # sell
        elif ( trade_type == 'ask' ):
            # print('ask ', sep='')
            order_balance = order_balance * 0.9995 # 수수료
            crypto_balance -= round(order_balance / current_crypto_price, 2)
            fiat_balance += order_balance
            pass
        else:
            continue
        pass
    print( "shannon remain fiat {}, crypto price 100 {} total {}".format( 
        round(fiat_balance)
        ,round(1000 * crypto_balance)
        ,round(1000 * crypto_balance + fiat_balance)
        )
    )


    pass
