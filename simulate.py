

all_fiat_value = 10000000
original_crypto_amount = 0
fiat_part_value = all_fiat_value / 2
crypto_amount = 0
crypto_value = 0



def rebalance(crypto_price : int ):

    global original_crypto_amount, all_fiat_value, fiat_part_value, crypto_amount, crypto_value
    # all in 했을때의 crypto 수량 
    if( original_crypto_amount == 0 ):
        original_crypto_amount = all_fiat_value / crypto_price

    #처음인 경우 
    if( crypto_value == 0 ):
        crypto_amount = round(fiat_part_value / crypto_price , 2)

    # 현재 가격을 통해 가치 계산 
    crypto_value = crypto_amount * crypto_price

    if( crypto_value > fiat_part_value * 1.01 ):
        # crypto 가격이 오른 경우 
        diff_value = round((crypto_value - fiat_part_value)/2, 2)
        crypto_amount = crypto_amount - round(diff_value/crypto_price, 2)
        fiat_part_value = fiat_part_value + diff_value
        pass
    elif( fiat_part_value > crypto_value * 1.01):
        # crypto 가격이 내린 경우   
        diff_value = round((fiat_part_value - crypto_value)/2, 2)
        crypto_amount = crypto_amount + round(diff_value/crypto_price, 2)
        fiat_part_value = fiat_part_value - diff_value

    # 가치를 동일시 하고 난뒤 가치 다시 계산 
    crypto_value = crypto_amount * crypto_price
    
    print('fiat value {:,}, crypto price:{} crypto amount: {}, crypto value: {:,} total value: {:,}'.format(
        fiat_part_value, crypto_price, crypto_amount, crypto_value, fiat_part_value + crypto_value ))
    print('in case of all in crypto amount {:,}, crypto value:{:,}'.format(  
        original_crypto_amount, original_crypto_amount * crypto_price  ) )
    print('')
    pass

if __name__ == "__main__":
    print("")

    # up and base
    test_data_list = [1000, 1100, 1200, 1300, 1200, 1100, 1000]
    # down and base
    test_data_list = [1000, 900, 800, 700, 800, 900, 1000]
    # down and down
    test_data_list = [1000, 900, 800, 700, 600, 700, 500]
    # up and up
    # test_data_list = [1000, 1100, 1200, 1300, 1400, 1500 ]

    for item in test_data_list:
        rebalance( item )
    pass