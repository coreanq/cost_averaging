import pytest
import json
import datetime
import time
import openpyxl


@pytest.fixture
def UpbitObj(MarketCode):
    import UpbitWrapper  
    with open("auth/access_info.json", "r") as json_file:
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
    test_count = 2
    result = UpbitObj.getDayCandle(count = test_count )

    if( "error" in result ):
        assert 0
    else:
        assert( len(result) == test_count )
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



def test_makeCandle(UpbitObj, time_type = 'week'):
# @pytest.mark.skip(reason="no test make json file purpose")
    date_time_format = "%Y-%m-%dT%H:%M:%S"
    # str_date_time_target = '2017-11-01T01:00:00'
    str_date_time_target = ''

    output_list = []


    isCompleted = False

    while (isCompleted == False):

        result = None
        if( time_type == 'week'):
            result = UpbitObj.getWeekCandle(count = 200, last_date_time_to = str_date_time_target)
        elif( time_type == 'day'):
            result = UpbitObj.getDayCandle(count = 200, last_date_time_to = str_date_time_target)
        elif( time_type == 'minute'):
            result = UpbitObj.getMinuteCandle(count = 200, last_date_time_to = str_date_time_target, minute_unit='240')

        if( result == None ):
            break

        for item in result :
            str_candle_date_time = item['candle_date_time_kst']
            open_price = item['opening_price']
            close_price = item['trade_price']
            ratio_of_open_close =  round( ((close_price - open_price) / open_price) * 100, 2)
            candle_date_time = datetime.datetime.strptime(str_candle_date_time, date_time_format)
            last_candle_date_time = None
            item['ratio'] = ratio_of_open_close

            last_candle_date_time_kst = ''
            if( len(output_list) != 0 ):
                last_candle_date_time_kst  =  output_list[-1]['candle_date_time_kst']
                last_candle_date_time = datetime.datetime.strptime(last_candle_date_time_kst, date_time_format)


            if( len(result) != 200): # 마지막 데이터
                isCompleted = True

            if( last_candle_date_time == None ):
                output_list.append(item)
            elif( last_candle_date_time > candle_date_time):
                output_list.append(item)
                str_date_time_target = item['candle_date_time_kst'].replace('T', ' ' )

        print(f'200_target: {str_date_time_target}, {UpbitObj.market_code}')
        time.sleep(0.1) # 시세 조회 제약 회피 


    # 기존 키 값의 용량 문제로 다른 키 값으로 변경 
    for item in output_list:
        item['time'] = item.pop('candle_date_time_kst')
        item['close'] = item.pop('trade_price')
        item.pop('market')
        # item.pop('opening_price')
        # item.pop('high_price')
        # item.pop('low_price')

    # print(result)
    with open("{}_{}_candles.json".format( UpbitObj.market_code, time_type ), "w") as json_file:
        json.dump(output_list[::-1], json_file, indent= 2)



if __name__ == "__main__":
    import sys
    sys.path.append('.')
    # setting path
    # print(sys.path)

    import UpbitWrapper
    with open("auth/access_info.json", "r") as json_file:
        access_info = json.loads(json_file.read())

    access_key = access_info["access_key"]
    secret_key = access_info["secret_key"]
    server_url = "https://api.upbit.com"

    coin_pair_list = [ 'KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL' ]
    for coin_pair in coin_pair_list:
        obj = UpbitWrapper.UpbitWrapper(secret_key, access_key, server_url, coin_pair)
        test_makeCandle(obj, 'minute')