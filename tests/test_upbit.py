import pytest
import json
import datetime


@pytest.fixture
def UpbitObj(MarketCode):
    import UpbitWrapper  
    with open("access_info.json", "r") as json_file:
        access_info = json.loads(json_file.read())

    access_key = access_info["access_key"]
    secret_key = access_info["secret_key"]
    server_url = "https://api.upbit.com"
    obj = UpbitWrapper.UpbitWrapper(secret_key, access_key, server_url, MarketCode)
    return obj

@pytest.fixture
def MarketCode():
    return "KRW-XRP"

def test_getAccount(UpbitObj):
    result = UpbitObj.getAccountInfo()

    if( "error" in result ):
        assert 0
    else:
        result = json.dumps(result, indent=2)
        print(result)
        assert 1

def test_getOrderbook(UpbitObj ):
    result = UpbitObj.getOrderbook()

    if( "error" in result ):
        assert 0
    else:
        result = json.dumps(result, indent=2)
        print(result)
        assert 1

def test_getDayCandle(UpbitObj):
    count = 2
    result = UpbitObj.getDayCandle(count)

    if( "error" in result ):
        assert 0
    else:
        assert( len(result) == count )
        result = json.dumps(result, indent=2)
        print(result)

def test_makeOrder(UpbitObj):

    current_crypto_price = 100
    result = UpbitObj.checkAssetInfo(1000, current_crypto_price, 0)

    assert result != None
    assert 'order_type' in result

    result = UpbitObj.makeOrder(result['order_type'], current_crypto_price, result['order_balance'], test = True )


    current_crypto_price = 100
    result = UpbitObj.checkAssetInfo(1000, current_crypto_price, 20)

    assert result != None
    assert 'order_type' in result

    result = UpbitObj.makeOrder(result['order_type'], current_crypto_price, result['order_balance'], test = True )



    result = UpbitObj.checkAssetInfo(1000, current_crypto_price, 10)

    assert result != None
    assert 'order_type' in result

    result = UpbitObj.makeOrder(result['order_type'], current_crypto_price, result['order_balance'], test = True )

def test_makeDayCandle(UpbitObj):
# @pytest.mark.skip(reason="no test make json file purpose")
    str_date_time_target = '2018-01-03T01:00:00'
    date_time_format = "%Y-%m-%dT%H:%M:%S"

    date_time_target =  datetime.datetime.strptime(str_date_time_target, date_time_format)

    str_date_time_target = ''

    output_list = []


    isCompleted = False

    while (isCompleted == False):
        result = UpbitObj.getDayCandle(str_date_time_target)
        assert result != None

        for item in result :
            str_candle_date_time = item['candle_date_time_kst']
            candle_date_time = datetime.datetime.strptime(str_candle_date_time, date_time_format)
            if( date_time_target <= candle_date_time ):
                output_list.append(item)
            else:
                isCompleted = True
                break
        str_date_time_target = output_list[-1]['candle_date_time_kst'].replace('T', ' ' )
        output_list.pop(-1)
        
    # print(result)
    with open("xrp_day_candles.json", "w") as json_file:
        json.dump(output_list, json_file, indent= 2)


