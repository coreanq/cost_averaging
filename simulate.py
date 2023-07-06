import json
import datetime

rebalance_ratio = 1.01

init_fiat_value = 0
additional_fiat = 10000 # 하루에 추가되는 금액 

buy_and_hold_crypto_amount = 0
fiat_part_value = init_fiat_value / 2
crypto_amount = 0
crypto_value = 0

isInit = True

def init():
    global buy_and_hold_crypto_amount, init_fiat_value, fiat_part_value, crypto_amount, crypto_value, isInit

    rebalance_ratio = 1.01

    init_fiat_value = 0
    additional_fiat = 10000 # 하루에 추가되는 금액 

    buy_and_hold_crypto_amount = 0
    fiat_part_value = init_fiat_value / 2
    crypto_amount = 0
    crypto_value = 0

    isInit = True


def rebalance(crypto_price : int, additional_fiat: int ) -> str : 

    global buy_and_hold_crypto_amount, init_fiat_value, fiat_part_value, crypto_amount, crypto_value, isInit
    # all in 했을때의 crypto 수량 
    if( isInit == True ):
        buy_and_hold_crypto_amount = round(init_fiat_value / crypto_price, 2)
        isInit = False

    buy_and_hold_crypto_amount = round(buy_and_hold_crypto_amount + additional_fiat / crypto_price, 2)

    isRebalance = False

    #처음인 경우 
    if( crypto_value == 0 ):
        crypto_amount = round(fiat_part_value / crypto_price , 2)
        isRebalance = True

    # 현재 가격을 통해 가치 계산 
    crypto_value = crypto_amount * crypto_price

    fiat_part_value = fiat_part_value + additional_fiat

    if( crypto_value > fiat_part_value * rebalance_ratio ):
        # crypto 가격이 오른 경우 
        diff_value = round((crypto_value - fiat_part_value)/2, 2)
        crypto_amount = round( crypto_amount - round(diff_value/crypto_price, 2) )
        fiat_part_value = round(fiat_part_value + diff_value, 2) 
        isRebalance = True
        pass
    elif( fiat_part_value > crypto_value * rebalance_ratio ):
        # crypto 가격이 내린 경우   
        diff_value = round((fiat_part_value - crypto_value)/2, 2)
        crypto_amount = round(crypto_amount + diff_value/crypto_price, 2)
        fiat_part_value = round(fiat_part_value - diff_value, 2)
        isRebalance = True
    

    
    result = ''

    if( isRebalance == True ):
        # 가치를 동일시 하고 난뒤 가치 다시 계산 
        crypto_value = round( crypto_amount * crypto_price, 2 )

        result = 'rebalance: fiat value {:,}, crypto amount: {}, crypto value: {:,}, total value: {:,}\n'.format(
            fiat_part_value, crypto_amount, crypto_value, round(fiat_part_value + crypto_value, 2) )
        result = result + 'in case of all in crypto amount {:,}, crypto value: {:,}\n\n'.format(  
            buy_and_hold_crypto_amount, round( buy_and_hold_crypto_amount * crypto_price, 2)  ) 
    else:
        result = 'nothing to rebalance\n\n'

    return result 

if __name__ == "__main__":

    all_data = ''

    # with open("xrp_day_candles_all.json", 'r') as f:
    #     all_data = f.read()

    with open("xrp_60_minute_candles.json", 'r') as f:
        all_data = f.read()

    sample_source = json.loads(all_data) 


    # best case
    from_date = datetime.date(2020, 3, 13)
    to_date = datetime.date(2021,4,15)

    count = 1

    result_all = '' 

    for item in reversed(sample_source):
        price = item['opening_price']
        date_str = item['candle_date_time_kst']
        source_date_time = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")


        if( source_date_time.date() >= from_date and source_date_time.date() <= to_date ):

            result = rebalance(price, additional_fiat)

            result_all = result_all + '{:<4} th {:,} added, {}: crypto price {}\n{}\n'.format(
                count, additional_fiat * count,  date_str, price, result)

            count = count + 1

    with open("_best_result.txt", 'w') as f:
        f.write(result_all)

    init()
    # worst case
    from_date = datetime.date(2018, 1, 8)
    to_date = datetime.date(2020,3,13)

    for item in reversed(sample_source):
        price = item['opening_price']
        date_str = item['candle_date_time_kst']
        source_date_time = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")

        if( source_date_time.date() >= from_date and source_date_time.date() <= to_date ):

            result = rebalance(price, additional_fiat)

            result_all = result_all + '{:<4} th {:,} added, {}: crypto price {}\n{}\n'.format(
                count, additional_fiat * count,  date_str, price, result)

            count = count + 1

    with open("_worst_result.txt", 'w')as f:
        f.write(result_all)

    init()
    # nomal case
    from_date = datetime.date(2019, 1, 1)
    to_date = datetime.date(2023,10,30)

    for item in reversed(sample_source):
        price = item['opening_price']
        date_str = item['candle_date_time_kst']
        source_date_time = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")

        if( source_date_time.date() >= from_date and source_date_time.date() <= to_date ):

            result = rebalance(price, additional_fiat)

            result_all = result_all + '{:<4} th {:,} added, {}: crypto price {}\n{}\n'.format(
                count, additional_fiat * count,  date_str, price, result)

            count = count + 1

    with open("_nomal_result.txt", 'w')as f:
        f.write(result_all)

    pass