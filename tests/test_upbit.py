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

def test_makeDayCandle(UpbitObj):
# @pytest.mark.skip(reason="no test make json file purpose")
    str_date_time_target = '2018-01-08T01:00:00'
    date_time_format = "%Y-%m-%dT%H:%M:%S"

    date_time_target =  datetime.datetime.strptime(str_date_time_target, date_time_format)

    str_date_time_target = ''

    output_list = []


    isCompleted = False

    while (isCompleted == False):
        result = UpbitObj.getDayCandle(count = 200, last_date_time_to = str_date_time_target)
        if( result == None ):
            break

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
        time.sleep(0.1) # 시세 조회 제약 회피 
        
    # print(result)
    with open("{}_day_candles.json".format( UpbitObj.market_coede ), "w") as json_file:
        json.dump(output_list, json_file, indent= 2)

def test_makeWeekCandle(UpbitObj):
# @pytest.mark.skip(reason="no test make json file purpose")
    str_date_time_target = '2017-11-01T01:00:00'
    date_time_format = "%Y-%m-%dT%H:%M:%S"

    date_time_target =  datetime.datetime.strptime(str_date_time_target, date_time_format)

    str_date_time_target = ''

    output_list = []


    isCompleted = False

    while (isCompleted == False):
        result = UpbitObj.getWeekCandle(count = 200, last_date_time_to = str_date_time_target)
        if( result == None ):
            break

        for item in result :
            str_candle_date_time = item['candle_date_time_kst']
            high_price = item['high_price']
            low_price = item['low_price']
            ratio_of_high_low =  round( ((high_price - low_price) / low_price) * 100, 2)
            candle_date_time = datetime.datetime.strptime(str_candle_date_time, date_time_format)
            item['ratio'] = ratio_of_high_low
            if( date_time_target <= candle_date_time ):
                output_list.append(item)
            else:
                isCompleted = True
                break
        str_date_time_target = output_list[-1]['candle_date_time_kst'].replace('T', ' ' )
        output_list.pop(-1)
        time.sleep(0.1) # 시세 조회 제약 회피 
        
    # print(result)
    file_name = "{}_week_candles".format( UpbitObj.market_code )
    wb = openpyxl.Workbook()
    sheet = wb.active

    count = 1
    sheet['A{}'.format( count) ] = "기준날짜"
    sheet['B{}'.format( count) ] = '시가'
    sheet['C{}'.format( count) ] = '고가'
    sheet['D{}'.format( count) ] = '저가'
    sheet['E{}'.format( count) ] = '종가'
    sheet['F{}'.format( count) ] = '등락률'

    for count, item in enumerate(output_list):
        sheet['A{}'.format( count + 2)] = item['candle_date_time_kst']
        sheet['B{}'.format( count + 2)] = item['opening_price']
        sheet['C{}'.format( count + 2)] = item['high_price']
        sheet['D{}'.format( count + 2)] = item['low_price']
        sheet['E{}'.format( count + 2)] = item['trade_price']
        sheet['F{}'.format( count + 2)] = item['ratio']

    wb.save(file_name + '.xlsx' )
    # with open( file_name + '.json' ), "w") as json_file:
    #     json.dump(output_list, json_file, indent= 2)

def test_makeMinuteCandle(UpbitObj, minute_unit = '60'):

    str_date_time_target = '2018-01-07T00:00:00'
    date_time_format = "%Y-%m-%dT%H:%M:%S"

    date_time_target =  datetime.datetime.strptime(str_date_time_target, date_time_format)

    str_date_time_target = ''

    output_list = []


    isCompleted = False

    while (isCompleted == False):
        result = UpbitObj.getMinuteCandle(count = 200, last_date_time_to = str_date_time_target, minute_unit = minute_unit)
        if( result == None ):
            break

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
        time.sleep(0.1) # 시세 조회 제약 회피 



        
    # print(result)
    with open("{}_{}_minute_candles.json".format(UpbitObj.market_code, minute_unit), "w") as json_file:
        json.dump(output_list, json_file, indent= 2)



if __name__ == "__main__":
    import sys
    sys.path.append('D:\\1git\\cost_averaging')
    # setting path
    # print(sys.path)

    import UpbitWrapper
    with open("auth/access_info.json", "r") as json_file:
        access_info = json.loads(json_file.read())

    access_key = access_info["access_key"]
    secret_key = access_info["secret_key"]
    server_url = "https://api.upbit.com"
    # obj = UpbitWrapper.UpbitWrapper(secret_key, access_key, server_url, 'KRW-XRP')
    obj = UpbitWrapper.UpbitWrapper(secret_key, access_key, server_url, 'KRW-ETH')
    test_makeWeekCandle(obj)