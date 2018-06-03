# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 10:05:17 2018

@author: mai1346
"""

import matplotlib.pyplot as plt
import seaborn as sns

def plot_equity_performance(output_df):
    sns.set()
    equity = output_df['strategy_equity']
    bench = output_df['bench_equity']
    st_drawdown = output_df['strategy_drawdown']
    bench_drawdown = output_df['bench_drawdown'] 
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (16,9), sharex=True)
    ax1.set_title('Equity Curve')
    ax1.plot(equity, color = 'green', label = 'Strategy')
    ax1.plot(bench, color = 'red', label = 'Benchmark')
    ax1.fill_between(output_df.index, equity, bench, where = equity >= bench, 
                     facecolor='green', alpha = 0.3, interpolate= True)
    ax1.fill_between(output_df.index, equity, bench, where = bench >= equity, 
                     facecolor='red', alpha = 0.3, interpolate= True)
    ax1.legend()
    
    ax2.set_title('Drawdown')
    ax2.plot(st_drawdown, color = 'blue', label = 'Strategy Drawdown')
    ax2.plot(bench_drawdown, color = 'black', label = 'Benchmark Drawdown')    
    ax2.legend()


def plot_trade(trade_log, symbol_data):
    sns.set()
    symbol_num = len(symbol_data)
    fig = plt.figure(figsize = (16,symbol_num / 2 * 9))
    for count, symbol in enumerate(symbol_data):
        bench = symbol_data[symbol]['close']
        entry_dates = trade_log[symbol]['entry_date']
        exit_dates = trade_log[symbol]['exit_date']
        entries = bench[bench.index.isin(entry_dates)]
        exits = bench[bench.index.isin(exit_dates)]
        
        ax = fig.add_subplot(symbol_num, 1, count+1)
        ax.set_title('%s Trades' % symbol)
        ax.plot(bench, color = 'blue', lw = 1.5, label = '_No display')
        ax.plot(entries, '^', markersize = 10, color='green', label = 'Entries')
        ax.plot(exits, 'v', markersize = 10, color='red', label = 'Exits')
        ax.legend()

        