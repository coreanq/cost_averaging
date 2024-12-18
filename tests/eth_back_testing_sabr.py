import pandas as pd
import numpy as np
import json
from datetime import datetime
from scipy.stats import norm
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# 다양한 포맷팅 함수들
def format_plain(x, pos):
    return f'{int(x)}'  # 기본 정수

def format_thousands(x, pos):
    return f'{int(x):,}'  # 천단위 구분기호

def format_millions(x, pos):
    return f'{x/1e6:.1f}M'  # 백만 단위

def format_billions(x, pos):
    return f'{x/1e9:.1f}B'  # 십억 단위

class ETHSABRAnalyzer:
    def __init__(self, data):
        # SABR 모델 기본 파라미터 - 암호화폐 시장 특성에 맞게 조정
        self.alpha = 0.5    # 초기 변동성 (더 높게 설정)
        self.beta = 0.5     # CEV 파라미터 (0.5로 조정)
        self.rho = -0.7     # 레버리지 효과 강화
        self.nu = 0.8       # 변동성의 변동성 증가
        self.risk_free_rate = 0.043
        
        self.df = self._preprocess_data(data)
    
    def _preprocess_data(self, data):
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        
        # 변동성 계산 강화
        df['returns'] = df['close'].pct_change()
        # 만기와 비슷한 기간을 사용하여 HV 계산
        df['volatility'] = df['returns'].rolling(window=7).std() * np.sqrt(365)  # 기간 단축
        df['volatility'] = df['volatility'].fillna(method='bfill').fillna(0.8)   # 기본값 증가
        
        # 최소 변동성 설정
        df['volatility'] = df['volatility'].clip(lower=0.35)  # ETH IV history from 35%
        
        return df

    def safe_sabr_vol(self, K, F, T, alpha, beta, rho, nu):
        """안전한 SABR 변동성 계산"""
        try:
            # ATM 근처에서의 특별 처리
            if abs(F - K) < F * 0.001:
                vol = alpha * (1 + ((2-3*rho**2)/24)*alpha**2*T + 
                             rho*beta*nu*alpha*T/4 + (2-beta)**2*nu**2*T/24)
                return max(0.5, min(2.0, vol))  # 최소/최대 범위 설정

            # 일반적인 케이스
            logFK = np.log(F/K)
            FK_beta = (F*K)**((1-beta)/2)
            z = (nu/alpha) * FK_beta * logFK

            # 수치 안정성을 위한 처리
            if abs(z) > 10:  # z값이 너무 큰 경우
                return max(0.5, alpha * np.exp(abs(logFK) * 0.5))

            denominator = 1-rho
            if abs(denominator) < 1e-8:
                denominator = 1e-8

            x = np.log((np.sqrt(1-2*rho*z + z*z) + z-rho)/denominator)
            
            # x가 너무 작은 경우 처리
            if abs(x) < 1e-8:
                x = 1e-8

            vol = (alpha/FK_beta) * (z/x)
            
            # 최종 결과 범위 제한
            return max(0.5, min(2.0, vol))

        except Exception as e:
            print(f"SABR vol calculation error: {e}")
            # 오류 발생시 현재 변동성 기반 대체값 반환
            return max(0.5, alpha * 1.5)

    def calculate_option_price(self, current_price, strike_price, time_to_expiry, 
                             current_vol, option_type='call'):
        """개선된 옵션 가격 계산"""
        try:
            # SABR 파라미터 동적 조정
            self.alpha = max(0.5, min(1.0, current_vol))
            self.nu = max(0.5, min(1.0, current_vol * 1.5))

            # 내재 변동성 계산 (안전 처리 포함)
            implied_vol = self.safe_sabr_vol(
                strike_price, current_price, time_to_expiry,
                self.alpha, self.beta, self.rho, self.nu
            )

            # Black-Scholes 가격 계산
            d1 = (np.log(current_price/strike_price) + 
                  (self.risk_free_rate + implied_vol**2/2)*time_to_expiry) / (implied_vol*np.sqrt(time_to_expiry))
            d2 = d1 - implied_vol*np.sqrt(time_to_expiry)

            discount = np.exp(-self.risk_free_rate*time_to_expiry)

            if option_type == 'call':
                price = current_price*norm.cdf(d1) - strike_price*discount*norm.cdf(d2)
            else:
                price = strike_price*discount*norm.cdf(-d2) - current_price*norm.cdf(-d1)

            # 가격 하한 설정
            min_price = current_price * 0.001  # 현재가의 0.1%를 최소가격으로 설정
            return max(min_price, price)

        except Exception as e:
            print(f"Option price calculation error: {e}")
            # 오류 발생시 단순화된 가격 계산
            return current_price * 0.05  # 현재가의 5%를 기본가격으로 반환

    def run_backtest(self, initial_capital=10000000, investment_ratio=0.5):
        results = []
        capital = initial_capital
        
        for i in range(len(self.df)):
            if self.df.iloc[i]['time'].weekday() == 3:  # Thursday
                if i + 7 >= len(self.df):
                    break
                    
                current_price = self.df.iloc[i]['close']
                expiry_price = self.df.iloc[i + 7]['close']
                current_vol = self.df.iloc[i]['volatility']

                if( capital < current_price):
                    continue
                
                total_investment = capital * investment_ratio
                investment_per_side = total_investment / 2
                
                # ATM 옵션 설정
                call_strike = round(current_price, -3)  # 천원 단위 반올림
                put_strike = call_strike  # ATM 옵션 사용
                
                time_to_expiry = 7/365
                
                # 옵션 가격 계산
                call_price = self.calculate_option_price(
                    current_price, call_strike, time_to_expiry, current_vol, 'call'
                )
                put_price = self.calculate_option_price(
                    current_price, put_strike, time_to_expiry, current_vol, 'put'
                )
                
                # 최소 가격 설정
                min_price = max(1000, current_price * 0.001)  # 최소 1000원 또는 현재가의 0.1%
                call_price = max(min_price, call_price)
                put_price = max(min_price, put_price)

                call_price = int( round(call_price, -2) )
                put_price = int( round(put_price, -2) )

                # 계약수 계산 (최소 1계약 보장)
                call_contracts = max(1, min(300, int(investment_per_side / call_price)))
                put_contracts = max(1, min(300, int(investment_per_side / put_price)))

                call_investment = call_contracts * call_price
                put_investment = put_contracts * put_price
                
                # 수수료 계산
                call_fee = min(call_strike * 0.0002, call_price * 0.125) * call_contracts
                put_fee = min(put_strike * 0.0002, put_price * 0.125) * put_contracts

                total_investment = call_contracts * call_price + put_contracts * put_price
                
                # 손익 계산
                call_pnl = call_contracts * (max(0, expiry_price - call_strike) - call_price) - call_fee
                put_pnl = put_contracts * (max(0, put_strike - expiry_price) - put_price) - put_fee
                
                if call_pnl > 0: call_pnl *= 0.99985  # 청산 수수료
                if put_pnl > 0: put_pnl *= 0.99985
                
                total_pnl = call_pnl + put_pnl
                capital += total_pnl
                
                results.append({
                    'date': self.df.iloc[i]['time'].strftime('%Y-%m-%d'),
                    'capital': round(capital),
                    'investment_ratio': round(investment_ratio, 2),
                    'eth_price': current_price,
                    'eth_next_week_price': expiry_price,
                    'volatility': round(current_vol, 4),
                    'call_strike': call_strike,
                    'put_strike': put_strike,
                    'call_price': round(call_price),
                    'put_price': round(put_price),
                    'call_contracts': call_contracts,
                    'put_contracts': put_contracts,
                    'call_investment': round(call_investment),
                    'put_investment': round(put_investment),
                    'total_pnl': round(total_pnl),
                    'total_investment': round(total_investment),
                    'implied_vol': round(self.safe_sabr_vol(
                        call_strike, current_price, time_to_expiry,
                        self.alpha, self.beta, self.rho, self.nu
                    ), 4)
                })
                
        # Get final results
        final_result = results[-1]
        first_result = results[0]

        print("\n=== 최종 백테스팅 결과 ===")
        print(f"투자비율: {investment_ratio*100:.2f}% | 거래일: {first_result['date']} ~ {final_result['date']}")
        print(f"최종 자본금: {final_result['capital']:,} KRW")
        print(f"초기 자본금 대비 수익률: {((final_result['capital']/initial_capital)-1)*100:.2f}%")

        # 전체 거래 통계
        total_trades = len(results)
        profitable_trades = sum(1 for r in results if r['total_pnl'] > 0)
        loss_trades = sum(1 for r in results if r['total_pnl'] < 0)

        info : str =  f"{investment_ratio*100:.2f}%_ {first_result['date']} ~ {final_result['date']}"

        with open(f"sabr_result_{info}.txt", 'w') as f:
            json.dump(results, f, indent=4)

        # print("\n=== 전체 거래 통계 ===")
        # print(f"총 거래 횟수: {total_trades}")
        # print(f"수익 거래: {profitable_trades}")
        # print(f"손실 거래: {loss_trades}")
        # print(f"승률: {(profitable_trades/total_trades)*100:.2f}%")
    
        return pd.DataFrame(results)

    def analyze_results(self, results_df, ratio):
        if len(results_df) == 0:
            print("No results to analyze")
            return

        initial_capital = results_df.iloc[0]['capital'] - results_df.iloc[0]['total_pnl']
        final_capital = results_df.iloc[-1]['capital']
        
        total_trades = len(results_df)
        profitable_trades = sum(results_df['total_pnl'] > 0)
        
        print("\n=== {}% 백테스팅 결과 분석 ===".format(ratio*100))
        print(f"테스트 기간: {results_df.iloc[0]['date']} ~ {results_df.iloc[-1]['date']}")
        print(f"초기자본: {initial_capital:,} KRW")
        print(f"최종자본: {final_capital:,} KRW")
        print(f"총 수익률: {((final_capital/initial_capital)-1)*100:.2f}%")
        print(f"총 거래 횟수: {total_trades}")
        print(f"수익 거래: {profitable_trades}")
        print(f"승률: {(profitable_trades/total_trades)*100:.2f}%")
        
        # if len(results_df) > 0:
        #     print("\n옵션 가격 통계:")
        #     print(f"평균 콜옵션 가격: {results_df['call_price'].mean():,.0f}")
        #     print(f"평균 풋옵션 가격: {results_df['put_price'].mean():,.0f}")
        #     print(f"평균 내재변동성: {results_df['implied_vol'].mean():.4f}")

def filter_json_by_date(data, start_date, end_date):
    """
    Filter JSON data based on start and end dates.
    
    Parameters:
    data (list): List of dictionaries containing time series data
    start_date (str): Start date in format 'YYYY-MM-DD'
    end_date (str): End date in format 'YYYY-MM-DD'
    
    Returns:
    list: Filtered data between start_date and end_date (inclusive)
    """
    # Convert string dates to datetime objects
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Filter the data
    filtered_data = [
        item for item in data
        if start_dt <= datetime.strptime(item['time'].split('T')[0], '%Y-%m-%d') <= end_dt
    ]
    
    return filtered_data
# 사용 예시
def main():
    # 데이터 로드
    with open('KRW-ETH_day_candles.json', 'r') as f:
        data = json.load(f)

    # 특정 기간 데이터 선택하기
    # all
    # start_date = '2017-10-01'
    # end_date = '2024-12-31'

    # bear
    # start_date = '2018-07-01'
    # end_date = '2020-10-31'

    # bull
    # start_date = '2020-11-01'
    # end_date = '2021-12-31'

    # hard core
    start_date = '2022-10-01'
    end_date = '2023-12-01'


    filtered_result = filter_json_by_date(data, start_date, end_date)   

    analyzer = ETHSABRAnalyzer(filtered_result)
    
    # 백테스팅 실행

    all_results_df = []
    for ratio in [round(x*0.1, 1) for x in range(1, 8)]:
        results = analyzer.run_backtest(investment_ratio=ratio)
        all_results_df.append(results)
    

    # capital 데이터 그래프화
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    for idx, df in enumerate(all_results_df):
        ax1.plot(df['date'], df['capital'], label='{}%'.format(df.iloc[0]['investment_ratio'] * 100) )
        ax1.yaxis.set_major_formatter(FuncFormatter(format_millions))
        ax1.set_xlabel('Date')
        ax1.title.set_text('Capital')
        ax1.legend(loc='upper left')

        # 변동성 추이
        if( idx == 0 ):
            ax2.plot(df['date'], df['volatility'], label='historical_vol')
            ax2.plot(df['date'], df['implied_vol'], label='implied_vol')
            ax2.title.set_text('Historical Volatility')
            ax2.set_xlabel('Date')
            ax2.legend(loc='upper left')

        # 손익 분포
        ax3.hist(df['total_pnl'], bins=50, label='{}%'.format(df.iloc[0]['investment_ratio'] * 100) )
        ax3.xaxis.set_major_formatter(FuncFormatter(format_millions))
        ax3.title.set_text('PnL Distribution')
        ax3.set_title('total_pnl Distribution')
        ax3.legend(loc='upper left')

        if( idx == 0):
            ax4.plot(df['date'], df['call_price'], label= 'call price')
            ax4.plot(df['date'], df['put_price'], label= 'put_price')
            ax4.yaxis.set_major_formatter(FuncFormatter(format_plain))
            ax4.set_xlabel('Date')
            ax4.set_title('Option Prices')

    plt.show()

if __name__ == "__main__":
    main()