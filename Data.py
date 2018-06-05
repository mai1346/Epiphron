# -*- coding: utf-8 -*-
"""
Created on Thu May 17 16:42:31 2018

@author: mai1346
"""


import pandas as pd
import sqlalchemy as sqla
import numpy as np
import tushare as ts

from abc import ABC, abstractmethod
from Event import MarketEvent

class DataHandler(ABC):
    '''
    本类为抽象类，用于规范所有子类的必要方法。
    '''
    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        '''
        返回最新的bars
        '''
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        '''
        返回最新的时间戳
        '''
        raise NotImplementedError("Should implement get_latest_bar_datetime()")

    @abstractmethod
    def get_latest_bars_values(self, symbol, val_type, N=1):
        '''
        返回最新的bars value，比如open，close，high，low等
        '''
        raise NotImplementedError("Should implement get_latest_bars_values()")

    @abstractmethod
    def update_bars(self):
        '''
        生成Market事件。
        '''
        raise NotImplementedError("Should implement update_bars()")
        
class HistoricSQLDataHandler(DataHandler):
    '''
    本类从已有的MySQL database中获取数据，用于生成market 事件。
    '''
    def __init__(self, events, symbol_list, start_date, end_date):

        self.events = events
        self.login_info = {'username':'stockuser','password':'87566766',\
                           'host':'localhost','db':'cnstock'}
        self.conn = self._connection(**self.login_info)
        self.start_date = start_date
        self.end_date = end_date
        self.symbol_list = symbol_list
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self.continue_iteration = {}
        
        self._loaddata()

    def _connection(self, **login):
        '''
        建立数据库连接。
        '''
        engine=sqla.create_engine('mysql://%s:%s@%s/%s?charset=utf8' % 
                                 (login['username'],login['password'],login['host'],login['db']))
        return engine
    
    def _loaddata(self):
        '''
        载入数据库数据。
        '''
        DB = pd.read_sql("select date,open,high,low,close,volume,code from cnstock.rawdata", self.conn)
        DB['date'] = pd.to_datetime(DB['date'])
        DB.set_index('date',inplace = True)
        mask = (DB.index >= self.start_date) & (DB.index <= self.end_date)
        DB = DB.loc[mask]
        comb_index = None
        
        for s in self.symbol_list:
            self.symbol_data[s] = DB[DB['code'] == s]
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)
            self.latest_symbol_data[s] = []
            self.continue_iteration[s] = True
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s]. \
                                reindex(index = comb_index, method = 'ffill').iterrows()
                
    def _get_new_bar(self, symbol):
        '''
        从generator中获取最新的数据信息。
        '''
        for b in self.symbol_data[symbol]:
            yield b
            
    def get_latest_bars(self, symbol, N=1):

        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, symbol):

        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1][0]
    
    def get_latest_bars_values(self, symbol, val_type, N=1):

        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return np.array([b[1].loc[val_type] for b in bars_list])

    def update_bars(self):

        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))                
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
            except StopIteration:
                self.continue_iteration[s] = False
                if all(value == False for value in self.continue_iteration.values()):
                    self.continue_backtest = False

        self.events.put(MarketEvent())



class TushareDataHandler(DataHandler):
    
    def __init__(self, events, symbol_list, start_date, end_date):
        self.events = events
        self.symbol_list = symbol_list
        self.start_date = start_date.strftime('%Y-%m-%d')
        self.end_date = end_date.strftime('%Y-%m-%d')
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self.continue_iteration = {}    
        self._getdata()
    
    def _getdata(self):
        comb_index = None
        for symbol in self.symbol_list:
            self.symbol_data[symbol] = ts.get_k_data(symbol, self.start_date, self.end_date)
            self.symbol_data[symbol]['date'] = pd.to_datetime(self.symbol_data[symbol]['date'])
            self.symbol_data[symbol].set_index('date',inplace = True)
            self.symbol_data[symbol].drop('code', axis = 1, inplace = True)
            if comb_index is None:
                comb_index = self.symbol_data[symbol].index
            else:
                comb_index = comb_index.union(self.symbol_data[symbol].index)
            self.latest_symbol_data[symbol] = []
            self.continue_iteration[symbol] = True   
        for symbol in self.symbol_list:
            self.symbol_data[symbol] = self.symbol_data[symbol]. \
            reindex(index = comb_index, method = 'ffill').iterrows()
                                
    def _get_new_bar(self, symbol):

        for b in self.symbol_data[symbol]:
            yield b
            
    def get_latest_bars(self, symbol, N=1):

        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, symbol):

        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1][0]
    
    def get_latest_bars_values(self, symbol, val_type, N=1):

        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return np.array([b[1].loc[val_type] for b in bars_list])

    def update_bars(self):

        
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
            except StopIteration:
                self.continue_iteration[s] = False
                if all(value == False for value in self.continue_iteration.values()):
                    self.continue_backtest = False

        self.events.put(MarketEvent())
        
    