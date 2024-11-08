import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import math

data = json.load(open('KRW-ETH_day_candles.json', 'r'))

def black_scholes(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    
    if option_type == 'call':
        price = S*norm_cdf(d1) - K*np.exp(-r*T)*norm_cdf(d2)
    else:
        price = K*np.exp(-r*T)*norm_cdf(-d2) - S*norm_cdf(-d1)
        
    return price

def norm_cdf(x):
    return (1 + math.erf(x/np.sqrt(2)))/2

def calculate_contracts(investment_per_side, option_price, max_contracts=300):
    return min(max_contracts, int(investment_per_side / option_price))

# Initial settings
initial_capital = 100000000  # 1억원
risk_free_rate = 0.03
investment_ratio = 0.1  # 전체 자본금의 10%


# Load and prepare data
df = pd.DataFrame([{
    'date': pd.to_datetime(d['time']),
    'close': d['close'],
    'ratio': d['ratio']
} for d in data])

df['returns'] = df['close'].pct_change()
df['volatility'] = df['returns'].rolling(30).std() * np.sqrt(252)
df['volatility'] = df['volatility'].fillna(0.5)

# Run backtest
results = []
capital = initial_capital

for i in range(len(df)):
    if df.iloc[i]['date'].weekday() == 3:  # Thursday
        if i + 7 >= len(df):
            break
            
        current_price = df.iloc[i]['close']
        expiry_price = df.iloc[i+7]['close']
        volatility = df.iloc[i]['volatility']
        
        total_investment = capital * investment_ratio
        investment_per_side = total_investment / 2
        
        call_strike = math.ceil(current_price/10000)*10000
        put_strike = math.floor(current_price/10000)*10000
        
        time_to_expiry = 7/365
        call_price = black_scholes(current_price, call_strike, time_to_expiry, 
                                 risk_free_rate, volatility, 'call')
        put_price = black_scholes(current_price, put_strike, time_to_expiry,
                                risk_free_rate, volatility, 'put')
        
        call_contracts = calculate_contracts(investment_per_side, call_price)
        put_contracts = calculate_contracts(investment_per_side, put_price)
        
        call_investment = call_contracts * call_price
        put_investment = put_contracts * put_price
        
        call_pnl = call_contracts * (max(0, expiry_price - call_strike) - call_price)
        put_pnl = put_contracts * (max(0, put_strike - expiry_price) - put_price)
        total_pnl = call_pnl + put_pnl
        
        capital += total_pnl
        
        results.append({
            'date': df.iloc[i]['date'].strftime('%Y-%m-%d'),
            'capital': round(capital),
            'eth_price': current_price,
            'eth_next_week_price': expiry_price,
            'expiry_price': expiry_price,
            'call_strike': call_strike,
            'put_strike': put_strike,
            'call_price': round(call_price),
            'put_price': round(put_price),
            'call_contracts': call_contracts,
            'put_contracts': put_contracts,
            'call_investment': round(call_investment),
            'put_investment': round(put_investment),
            'total_pnl': round(total_pnl),
            'total_investment': round(call_investment + put_investment)
        })

# Get final results
final_result = results[-1]
print("\n=== 최종 백테스팅 결과 ===")
print(f"마지막 거래일: {final_result['date']}")
print(f"최종 자본금: {final_result['capital']:,} KRW")
print(f"초기 자본금 대비 수익률: {((final_result['capital']/initial_capital)-1)*100:.2f}%")
print("\n=== 마지막 거래 상세 ===")
print(f"ETH 가격: {final_result['eth_price']:,} KRW")
print(f"만기 가격: {final_result['expiry_price']:,} KRW")
print(f"콜옵션 계약수: {final_result['call_contracts']} (투자금: {final_result['call_investment']:,} KRW)")
print(f"풋옵션 계약수: {final_result['put_contracts']} (투자금: {final_result['put_investment']:,} KRW)")
print(f"총 투자금액: {final_result['total_investment']:,} KRW")
print(f"손익: {final_result['total_pnl']:,} KRW")

# 전체 거래 통계
total_trades = len(results)
profitable_trades = sum(1 for r in results if r['total_pnl'] > 0)
loss_trades = sum(1 for r in results if r['total_pnl'] < 0)

with open('result.txt', 'w') as f:
    json.dump(results, f, indent=4)


print("\n=== 전체 거래 통계 ===")
print(f"총 거래 횟수: {total_trades}")
print(f"수익 거래: {profitable_trades}")
print(f"손실 거래: {loss_trades}")
print(f"승률: {(profitable_trades/total_trades)*100:.2f}%")