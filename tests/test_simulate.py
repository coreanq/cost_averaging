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


    for current_crypto_price in range(100, 50, -1):
        result_list = UpbitObj.checkAssetInfo(fiat_balance, current_crypto_price, crypto_balance)
        assert "type" in result_list


        trade_type = result_list['type']
        order_balance = result_list['order_balance']

        # sell
        if( trade_type == 'bid' ):
            crypto_balance += round(order_balance / current_crypto_price, 2)
            fiat_balance -= order_balance
            pass
        elif ( trade_type == 'ask' ):
            crypto_balance -= round(order_balance / current_crypto_price, 2)
            fiat_balance += order_balance
            pass
        else:
            continue
        pass

    print( "remain fiat {}, crypto {}".format( fiat_balance, current_crypto_price * crypto_balance))


    pass


def test_makeDayCandle(UpbitObj):
# @pytest.mark.skip(reason="no test make json file purpose")
    str_date_time_from = '2018-01-05T01:00:00'
    date_time_format = "%Y-%m-%dT%H:%M:%S"
    date_time_from =  datetime.datetime.strptime(str_date_time_from, date_time_format)
    # print(date_time_from)

    result = UpbitObj.getDayCandle(count, 200)

    if( "error" in result ):
        assert 0
    else:
        assert( len(result) == count )

        with open("xrp_day_caldles.json", "w") as json_file:
            json.dump(result, json_file)


