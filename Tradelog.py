# -*- coding: utf-8 -*-
"""
Created on Tue May 29 14:29:09 2018

@author: mai1346
"""
import pandas as pd
from collections import defaultdict

class Tradelog():
    '''
    本类记录所有交易细节，针对每种交易资产记录交易时间、交易价格、交易数量以及每次
    买卖的盈利，并计算交易的胜率，有助于投资者了解每笔交易的详细信息。
    '''
    def __init__(self):
        '''
        初始化 tradelog 字典，字典元素以symbol为key，对应trade的dataframe为value。
        '''
        self.columns = ['entry_date', 'entry_price', 'long_short', 'quantity',
                        'exit_date', 'exit_price', 'pl_points', 'pl_cash', 'pl_cumul']
        self._tlog = defaultdict(pd.DataFrame)

    def get_Tradelog(self):
        '''
        外部获取 tradelog 字典。
        '''
        return self._tlog
    
    def update(self, event):
        '''
        与交易同步更新 tradelog，DataFrame 包括 entry 日期，exit 日期，交易类型（long、short）
        交易数量，exit 日期，exit 市价，每笔交易盈利以及累计盈利。
        '''
        if event.type == 'FILL':
            symbol = event.symbol
            if event.fill_type in ('LONG','SHORT'):
                d = {'entry_date': event.datetime,'entry_price': event.fill_cost, 
                 'long_short': event.fill_type, 'quantity': event.quantity}
                tempdict = pd.DataFrame([d], columns = self.columns)
                self._tlog[symbol] = self._tlog[symbol].append(tempdict, ignore_index = True)
                
            elif event.fill_type == 'EXIT':
                # 找出含有NaN的行的Index，因为只有开仓没有平仓的话，trade所在行缺少exit的相关信息。
                boolean = self._tlog[symbol].isna().any(1)
                index = self._tlog[symbol].index[boolean]
                idx = index[0]
                # 计算Trade的进场出场价差，以及盈利
                entry_price = self._tlog[symbol]['entry_price'][idx]
                exit_price = event.fill_cost
                exit_date = event.datetime
                pl_points = exit_price - entry_price
                pl_cash = pl_points * event.quantity

                self._tlog[symbol].loc[idx, 'exit_date'] = exit_date
                self._tlog[symbol].loc[idx, 'exit_price'] = exit_price
                self._tlog[symbol].loc[idx, 'pl_points'] = pl_points
                self._tlog[symbol].loc[idx, 'pl_cash'] = pl_cash
                self._tlog[symbol].loc[idx, 'pl_cumul'] = self._tlog[symbol]['pl_cash'].sum()
    
    def create_trade_summary(self):
        '''
        生成 Trade 的统计信息，包括胜率、最大盈利，最大亏损等。
        '''
        for symbol in self._tlog:
            # 筛选出已经完成的trade，完成的trade为一次开仓和平仓
            completed_trade = self._tlog[symbol].dropna(how = 'any', axis = 0)
            # 如果没有一次完整的交易，则退出循环。
            if completed_trade.empty:
                print ('No trade is complete, please extend the backtest period.')
                break
            else:
                win_trades = (completed_trade['pl_cash'] > 0).sum()
                win_rate = win_trades / len(completed_trade.index)
                total_profit = completed_trade['pl_cumul'].iloc[-1]
                Max_trade_profit = completed_trade['pl_cash'].max()
                Min_trade_profit = completed_trade['pl_cash'].min()
                Average_trade_profit = total_profit / len(completed_trade.index)
                bound = '-' * 40
                stats = "Symbol: %s" \
                        "\nWinning rate: %0.4f%%" \
                        "\nTotal Profit: %0.2f" \
                        "\nMaximum Single Trade Profit: %0.2f" \
                        "\nMinimum Single Trade Profit: %0.2f" \
                        "\nAverage Trade Profit: %0.2f" \
                        "\n%s" % \
                        (symbol, win_rate * 100, total_profit, Max_trade_profit, 
                         Min_trade_profit, Average_trade_profit, bound)
                        
                print (self._tlog[symbol])
                print (stats)

            
                        