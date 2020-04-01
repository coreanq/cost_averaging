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

def test_getDayCandle(UpbitObj ):
    count = 2
    result = UpbitObj.getDayCandle(count)

    if( "error" in result ):
        assert 0
    else:
        assert( len(result) == count )
        result = json.dumps(result, indent=2)
        print(result)

def test_makeDayCandle(UpbitObj):
# @pytest.mark.skip(reason="no test make json file purpose")
    str_date_time_from = '2018-01-05T01:00:00'
    date_time_format = "%Y-%m-%dT%H:%M:%S"
    date_time_from =  datetime.datetime.strptime(str_date_time_from, date_time_format)
    # print(date_time_from)


    output = []

    result = UpbitObj.getDayCandle(count, 200)

    for item in result:
        item['']

    if( "error" in result ):
        assert 0
    else:
        assert( len(result) == count )

        with open("xrp_day_caldles.json", "w") as json_file:
            json.dump(result, json_file)


