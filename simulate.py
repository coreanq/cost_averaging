import json
import datetime

all_fiat_value = 10000000
original_crypto_amount = 0
fiat_part_value = all_fiat_value / 2
crypto_amount = 0
crypto_value = 0



def rebalance(crypto_price : int ) -> str : 

    global original_crypto_amount, all_fiat_value, fiat_part_value, crypto_amount, crypto_value
    # all in 했을때의 crypto 수량 
    if( original_crypto_amount == 0 ):
        original_crypto_amount = round(all_fiat_value / crypto_price, 2)

    isRebalance = False

    #처음인 경우 
    if( crypto_value == 0 ):
        crypto_amount = round(fiat_part_value / crypto_price , 2)
        isRebalance = True

    # 현재 가격을 통해 가치 계산 
    crypto_value = crypto_amount * crypto_price


    if( crypto_value > fiat_part_value * 1.01 ):
        # crypto 가격이 오른 경우 
        diff_value = round((crypto_value - fiat_part_value)/2, 2)
        crypto_amount = round( crypto_amount - round(diff_value/crypto_price, 2) )
        fiat_part_value = round(fiat_part_value + diff_value, 2) 
        isRebalance = True
        pass
    elif( fiat_part_value > crypto_value * 1.01):
        # crypto 가격이 내린 경우   
        diff_value = round((fiat_part_value - crypto_value)/2, 2)
        crypto_amount = round(crypto_amount + diff_value/crypto_price, 2)
        fiat_part_value = round(fiat_part_value - diff_value, 2)
        isRebalance = True

    
    result = ''

    if( isRebalance == True ):
        # 가치를 동일시 하고 난뒤 가치 다시 계산 
        crypto_value = crypto_amount * crypto_price

        result = 'rebalance: fiat value {:,}, crypto amount: {}, crypto value: {:,}, total value: {:,}\n'.format(
            fiat_part_value, crypto_amount, crypto_value, round(fiat_part_value + crypto_value, 2) )
        result = result + 'in case of all in crypto amount {:,}, crypto value:{:,}\n\n'.format(  
            original_crypto_amount, round( original_crypto_amount * crypto_price, 2)  ) 
    else:
        result = 'nothing to rebalance\n\n'

    return result 

if __name__ == "__main__":
    print("")

    # up and base
    test_data_list = [1000, 1100, 1200, 1300, 1200, 1100, 1000]
    # down and base
    test_data_list = [1000, 900, 800, 700, 800, 900, 1000]
    # down and down
    test_data_list = [1000, 900, 800, 700, 600, 700, 500]
    # up and up
    test_data_list = [1000, 1100, 1200, 1300, 1400, 1500 ]

    all_data = ''

    with open("xrp_day_candles_all.json", 'r') as f:
        all_data = f.read()

    sample_source = json.loads(all_data) 


    from_date = datetime.date(2019, 9, 1)
    to_date = datetime.date(2020,10,1)

    for item in reversed(sample_source):
        price = item['opening_price']
        date_str = item['candle_date_time_kst']
        source_date_time = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")

        if( source_date_time.date() >= from_date and source_date_time.date() <= to_date ):
            result = rebalance(price)
            result = '{}: crypto price {}\n{}'.format(date_str, price, result)

            with open("result.txt", 'a')as f:
                f.write(result)

    # for item in test_data_list:
    #     rebalance( item )
    pass