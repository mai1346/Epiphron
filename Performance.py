# -*- coding: utf-8 -*-
"""
Created on Fri May 18 11:42:21 2018

@author: mai1346
"""

import numpy as np
import pandas as pd
import tushare as ts


def calSharpe(returns, risk_free = 0, periods = 252):
    '''
    计算sharpe比率，默认为日sharpe 比率的年化，risk free rate 为 0。
    '''
    return (periods * returns.mean() - risk_free) / (returns.std() * np.sqrt(periods))

def calSortino(returns, risk_free = 0, periods = 252):
    '''
    计算sortino 比率
    '''
    deviation = returns[returns < 0].std()
    return (periods * returns.mean() - risk_free) / (deviation * np.sqrt(periods))
    
def calTreynor(strategy_returns, bench_returns, risk_free = 0, periods = 252):
    '''
    计算Treynor 比率
    '''
    df = pd.DataFrame({'strategy_returns':strategy_returns, 'bench_returns':bench_returns}).dropna()
    cov_mat = np.cov(df['strategy_returns'], df['bench_returns'])
#    print (cov_mat, cov_mat[0,1], cov_mat[1,1])
    beta = cov_mat[0,1] / cov_mat[1,1]
    alpha = df['strategy_returns'].mean()-beta * df['bench_returns'].mean()
    treynor = (periods * df['strategy_returns'].mean() - risk_free) / (beta * np.sqrt(periods))
    return treynor, beta, alpha * periods

def calIR(strategy_returns, bench_returns, periods = 252):
    '''
    计算Information Ratio
    '''
    diff = strategy_returns - bench_returns   
    return periods * diff.mean() / (diff.std() * np.sqrt(periods))

def calDrawdown(equity):
    '''
    计算策略回撤和最大回撤
    '''
    drawdown = equity/equity.cummax()-1
    maxdrawdown = drawdown.min() #the value of maxdrawdown
    
    return drawdown, maxdrawdown


def create_equity_curve_dataframe(all_holdings):
    '''
    生成portfolio的资金曲线
    '''
    df = pd.DataFrame(all_holdings)
    df.set_index('datetime', inplace=True)
    df['equity_returns'] = df['total'].pct_change()
    df['equity_curve'] = (1.0 + df['equity_returns']).cumprod()
    return df

def create_benchmark_dataframe(symbol, start, end):
    '''
    生成基准的资金曲线
    '''    
    start = start.strftime('%Y-%m-%d')
    end = end.strftime('%Y-%m-%d')
    bench = ts.get_k_data(symbol, start, end)
    bench['date'] = pd.to_datetime(bench['date'])
    bench.set_index('date', inplace = True)
    bench['bench_returns'] = bench['close'].pct_change()
    bench['bench_curve'] = (1.0 + bench['bench_returns']).cumprod()
    
    return bench[['bench_returns','bench_curve']]

def create_trade_plot_dataframe(symbol_list, data_handler):
    '''
    生成用于trade plot的symbol 市价信息
    '''
    symbol_data ={}
    for symbol in symbol_list:
        data = [x[1] for x in data_handler.get_latest_bars(symbol,0)]
        idx = [x[0] for x in data_handler.get_latest_bars(symbol,0)]
        symbol_data[symbol] = pd.DataFrame(data, index = idx) 
    return symbol_data

def output_summary_stats(df, bench):
    '''
    生成策略Performance信息。
    '''
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

    strategy_treynor, beta, alpha = calTreynor(strategy_returns, bench_returns)

    strategy_ir = calIR(strategy_returns, bench_returns)
    stats = "Strategy Total Return: %0.4f%%" \
            "\nStrategy Sharpe Ratio: %0.4f" \
            "\nStrategy Sortino Ratio: %0.4f" \
            "\nStrategy Treynor Ratio: %0.4f" \
            "\nStrategy Information Ratio: %0.4f" \
            "\nStrategy beta: %0.4f" \
            "\nStrategy alpha: %0.4f" \
            "\nStrategy Max Drawdown: %0.4f%%" \
            "\nBenchmark Total Return: %0.4f%%" \
            "\nBenchmark Sharpe Ratio: %0.4f" \
            "\nBenchmark Sortino Ratio: %0.4f" \
            "\nBenchmark Max Drawdown: %0.4f%%" % \
            ((strategy_total_return - 1.0) * 100, strategy_sharpe_ratio, strategy_sortino,
             strategy_treynor, strategy_ir, beta, alpha, strategy_max_dd * 100.0,
             (bench_total_return - 1.0) * 100, bench_sharpe_ratio, bench_sortino, bench_max_dd * 100.0)

    return stats, strategy_drawdown, bench_drawdown

#            "\nStrategy Treynor Ratio: %0.4f" \
#            "\nStrategy Information Ratio: %0.4f" \
 #
            
        