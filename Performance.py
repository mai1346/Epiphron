# -*- coding: utf-8 -*-
"""
Created on Fri May 18 11:42:21 2018

@author: mai1346
"""

import numpy as np
import pandas as pd
import tushare as ts


def calSharpe(returns, risk_free = 0, periods = 252):
    """
    Create the Sharpe ratio for the strategy, based on a 
    benchmark of zero (i.e. no risk-free rate information).

    args:
        returns - A pandas Series representing period percentage returns.
        periods - Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    returns:
        the sharpe ratio based on period chosen
    """
    return (periods * returns.mean() - risk_free) / (returns.std() * np.sqrt(periods))

def calSortino(returns, risk_free = 0, periods = 252):
    '''
    '''
    deviation = returns[returns < 0].std()
    return (periods * returns.mean() - risk_free) / (deviation * np.sqrt(periods))
    

def calDrawdown(equity):
    """
    args:
        equity: a panda series represents the equity of a specific asset.
    returns:
        Max drawdown
        Calendar duration of the max drawdown
    """
    drawdown = equity/equity.cummax()-1
    maxdrawdown = drawdown.min() #the value of maxdrawdown
#    end = drawdown.idxmin()# find the date of maxdrawdown
#    start = equity[:end].idxmax() # find the starting date of maxdrawdown
#    duration = end - start # calendar duration of the maxdrawdown
    
    return drawdown, maxdrawdown


def create_equity_curve_dataframe(all_holdings):
    """
    Creates a pandas DataFrame from the all_holdings
    list of dictionaries.
    """
    df = pd.DataFrame(all_holdings)
    df.set_index('datetime', inplace=True)
    df['equity_returns'] = df['total'].pct_change()
    df['equity_curve'] = (1.0 + df['equity_returns']).cumprod()
    return df

def benchmark_dataframe(symbol, start, end):
    '''
    '''    
#    if benchtype == 'BuyAndHold':
#        bench_dict = {}
#        for symbol in symbol_list:
#            bench_dict[symbol] = ts.get_k_data(symbol,start)
#            bench_dict[symbol]['date'] = pd.to_datetime(bench_dict[symbol]['date'])
#            bench_dict[symbol].set_index('date', inplace = True)
#        bench = sum([bench_dict[symbol]['close'] for symbol in symbol_list])
        # 
    start = start.strftime('%Y-%m-%d')
    end = end.strftime('%Y-%m-%d')
    bench = ts.get_k_data(symbol, start, end)
    bench['date'] = pd.to_datetime(bench['date'])
    bench.set_index('date', inplace = True)
    bench['bench_returns'] = bench['close'].pct_change()
    bench['bench_curve'] = (1.0 + bench['bench_returns']).cumprod()
    
    return bench[['bench_returns','bench_curve']]

def output_summary_stats(df, bench):
    """
	 Creates a list of summary statistics for the portfolio.
	 """
    strategy_total_return = df['equity_curve'].iloc[-1]
    strategy_returns = df['equity_returns']
    strategy_equity = df['equity_curve']
    strategy_sharpe_ratio = calSharpe(strategy_returns)
    strategy_sortino = calSortino(strategy_returns)
    strategy_drawdown, strategy_max_dd = calDrawdown(strategy_equity)
    
    bench_total_return = bench['bench_curve'].iloc[-1]
    bench_returns = bench['bench_returns']
    bench_equity = bench['bench_curve']
    bench_sharpe_ratio = calSharpe(bench_returns)
    bench_sortino = calSortino(bench_returns)
    bench_drawdown, bench_max_dd = calDrawdown(bench_equity)



    stats = "Strategy Total Return: %0.4f%%" \
            "\nStrategy Sharpe Ratio: %0.4f" \
            "\nStrategy Sortino Ratio: %0.4f" \
            "\nStrategy Max Drawdown: %0.4f%%" \
            "\nBenchmark Total Return: %0.4f%%" \
            "\nBenchmark Sharpe Ratio: %0.4f" \
            "\nBenchmark Sortino Ratio: %0.4f" \
            "\nBenchmark Max Drawdown: %0.4f%%" % \
            ((strategy_total_return - 1.0) * 100, strategy_sharpe_ratio, strategy_sortino, strategy_max_dd * 100.0,
             (bench_total_return - 1.0) * 100, bench_sharpe_ratio, bench_sortino, bench_max_dd * 100.0)

    return stats, strategy_drawdown, bench_drawdown


            
        