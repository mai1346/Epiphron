# -*- coding: utf-8 -*-
"""
Created on Tue May 29 14:32:46 2018

@author: mai1346
"""
from Event import OrderEvent
from abc import ABC, abstractmethod



class RiskManager(ABC):
    '''
    所有riskmanager的父类。
    '''
    @abstractmethod
    def generate_order(self, signal):
        
        raise NotImplementedError("Should implement generate_order()")
        
    @abstractmethod
    def update_signal(self, event):
        
        raise NotImplementedError("Should implement update_signal()") 

class Naive_Riskmanager(RiskManager):
    '''
    简单的riskmanager，不包含任何风控，生成固定quantity的order事件。
    '''
    def __init__(self, events, portfolio, data_handler):

        self.events = events
        self.portfolio = portfolio
        self.data_handler = data_handler
    def generate_order(self, signal):

        order = None
    
        symbol = signal.symbol
        direction = signal.signal_type
        datetime = signal.datetime
    
        mkt_quantity = 10000
        max_quantity = self.portfolio.current_holdings['cash'] / self.data_handler.get_latest_bars_values(symbol, "close")[0]
        cur_quantity = self.portfolio.get_current_position(symbol)
        
        if mkt_quantity > max_quantity:
            mkt_quantity = int(max_quantity)
        if mkt_quantity > 0:
            if direction == 'LONG' and cur_quantity == 0:
                order = OrderEvent(datetime, symbol, direction, mkt_quantity, 'BUY')
            if direction == 'SHORT' and cur_quantity == 0:
                order = OrderEvent(datetime, symbol, direction, mkt_quantity, 'SELL')
        
        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(datetime, symbol, direction, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(datetime, symbol, direction, abs(cur_quantity), 'BUY')
        return order  
    
    def update_signal(self, event):
        '''
        生成order事件。
        '''
        if event.type == 'SIGNAL':
            order_event = self.generate_order(event)
            self.events.put(order_event)
