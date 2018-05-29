# -*- coding: utf-8 -*-
"""
Created on Tue May 29 14:29:09 2018

@author: mai1346
"""
import pandas as pd
from collections import defaultdict

class Tradelog():
    """ trade log """

    def __init__(self):
        self.columns = ['entry_date', 'entry_price', 'long_short', 'qty',
                        'exit_date', 'exit_price', 'pl_points', 'pl_cash']
        self._tlog = defaultdict(pd.DataFrame)

    def get_Tradelog(self):
        return self._tlog.values()
    
    def update(self, event):
        if event.type == 'FILL':
            symbol = event.symbol
            if event.fill_type in ('LONG','SHORT'):
                d = {'entry_date': event.datetime,'entry_price': event.fill_cost, 
                 'long_short': event.fill_type, 'qty': event.quantity}
                tempdict = pd.DataFrame([d], columns = self.columns)
                self._tlog[symbol] = self._tlog[symbol].append(tempdict, ignore_index = True)
                
            elif event.fill_type == 'EXIT':
                # 找出含有NaN的行的Index，因为只有开仓没有平仓的话，trade所在行没有exit的相关信息。
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
                        