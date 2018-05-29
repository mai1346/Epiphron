# -*- coding: utf-8 -*-
"""
Created on Sat May 19 14:20:16 2018

@author: mai1346
"""
import datetime
#import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt

from Backtest import Backtest
from Data import HistoricSQLDataHandler
from Event import SignalEvent
from Execution import SimulatedExecutionHandler
from Portfolio import Portfolio
from Strategy import Strategy
from RiskManager import RiskManager

class EMACrossStrategy(Strategy):

    def __init__(self, data_handler, events, short_window = 5, long_window = 20):
        self.data_handler = data_handler
        self.symbol_list = self.data_handler.symbol_list
        self.events = events
        self.short_window = short_window
        self.long_window = long_window
        self.sema = {symbol: [] for symbol in self.symbol_list}
        self.lema = {symbol: [] for symbol in self.symbol_list}



        # Set to True if a symbol is in the market
        self.bought = self._initialize_bought()

    def _initialize_bought(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to 'OUT'.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = 'OUT'
        return bought

    def generate_signal(self, event):

        if event.type == 'MARKET':

            for symbol in self.symbol_list:
                bars = self.data_handler.get_latest_bars_values(symbol, "close", N = 0)
    #                print ('bars=', bars)
                if bars is not None:
                    sema = pd.Series.ewm(pd.Series(bars),
                                         span = self.short_window
                                         ).mean().iloc[-1]
    #                    sema = np.mean(bars[-self.short_window:])
                    self.sema[symbol].append(sema)
                    lema = pd.Series.ewm(pd.Series(bars),
                                         span = self.long_window
                                         ).mean().iloc[-1]
    #                    lema = np.mean(bars[-self.long_window:])
                    self.lema[symbol].append(lema)

                    dt = self.data_handler.get_latest_bar_datetime(symbol)
                    strength = 1.0
                    strategy_id = 1

                    if len(self.sema[symbol]) > 1:
                        if sema > lema and self.sema[symbol][-2] < self.lema[symbol][-2] and self.bought[symbol] == "OUT":
    #                        print('buy signal')
                            signal = SignalEvent(strategy_id, symbol, dt, 'LONG', strength)
                            self.events.put(signal)
                            self.bought[symbol] = 'LONG'


                        elif sema < lema and self.sema[symbol][-2] > self.lema[symbol][-2] and self.bought[symbol] == "LONG":
    #                        print('exit signal')
                            signal = SignalEvent(strategy_id, symbol, dt, 'EXIT', strength)
                            self.events.put(signal)
                            self.bought[symbol] = 'OUT'
    #        print (self.sema)


if __name__ == "__main__":
    login_info = {'username':'stockuser','password':'87566766','host':'localhost','db':'cnstock'}
    symbol_list = ['600050']
    initial_capital = 100000.0
    start_date = datetime.datetime(2015,1,1,0,0,0)
    heartbeat = 0.0

    backtest = Backtest(login_info,
                        symbol_list,
                        initial_capital,
                        heartbeat,
                        start_date,
                        HistoricSQLDataHandler,
                        SimulatedExecutionHandler,
                        Portfolio,
                        RiskManager,
                        EMACrossStrategy)

    backtest.simulate_trading()
