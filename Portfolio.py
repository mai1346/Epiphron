# -*- coding: utf-8 -*-
"""
Created on Fri May 18 11:08:52 2018

@author: mai1346
"""

from Tradelog import Tradelog


class Portfolio(object):
    '''
    本类用于记录整个Portfolio的各个资产的仓位和市值。
    本类接收Fill事件，并根据事件调整持仓信息。
    '''

    def __init__(self, data_handler, events, start_date, initial_capital=100000):
        '''
        data_handler - 数据来源
        start_date - Portfolio 开始时间
        initial_capital - 初始本金.
        '''
        self.data_handler = data_handler
        self.events = events
        self.symbol_list = self.data_handler.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital

        self.all_positions = self._construct_all_positions()
        self.current_positions = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])

        self.all_holdings = self._construct_all_holdings()
        self.current_holdings = self._construct_current_holdings()
        self.Tradelog = Tradelog()

    def _construct_all_positions(self):

        d = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        return [d]

    def _construct_all_holdings(self):

        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return [d]

    def _construct_current_holdings(self):

        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return d

    def _update_positions_from_fill(self, fill):
        '''
        根据FILL事件更新资产的持仓信息
        '''
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1
        # Update positions list with new quantities
        self.current_positions[fill.symbol] += fill_dir * fill.quantity

    def _update_holdings_from_fill(self, fill):
        '''
        根据FILL事件更新portfolio的资金信息
        '''
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update holdings list with new quantities
        fill_cost = fill.fill_cost
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)
    
    def _update_tradelog_from_fill(self, fill):
        '''
        更新Tradelog
        '''
        self.Tradelog.update(fill)
    
    def get_current_position(self,symbol):
        
        return self.current_positions[symbol]
        

    def update_fill(self, event):

        if event.type == 'FILL':
            self._update_positions_from_fill(event)
            self._update_holdings_from_fill(event)
            self._update_tradelog_from_fill(event)

    def update_timeindex(self):
        
        latest_datetime = self.data_handler.get_latest_bar_datetime(self.symbol_list[0])

        positions = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        positions['datetime'] = latest_datetime

        for s in self.symbol_list:
            positions[s] = self.current_positions[s]

        self.all_positions.append(positions)

        holdings = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        holdings['datetime'] = latest_datetime
        holdings['cash'] = self.current_holdings['cash']
        holdings['commission'] = self.current_holdings['commission']
        holdings['total'] = self.current_holdings['cash']

        for s in self.symbol_list:

            market_value = self.current_positions[s] * \
                            self.data_handler.get_latest_bars_values(s, "close")[0]  # [0] because it's a np array
            holdings[s] = market_value
            holdings['total'] += market_value

        self.all_holdings.append(holdings)
