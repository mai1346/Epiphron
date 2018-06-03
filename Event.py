# -*- coding: utf-8 -*-
"""
Created on Thu May 17 15:25:42 2018

@author: mai1346
"""

class Event(object):
    '''
    本类为所有事件的父类。
    '''
    pass

class MarketEvent(Event):
    '''
    本类为 Market 事件，由Data类产生。在回测平台中表现为从数据源读取的单个时间间隔（time step）
    的资产价格信息。
    Strategy类接收 Market 事件。
    '''
    def __init__(self):
        self.type = 'MARKET'
        
class SignalEvent(Event):
    '''
    本类为 Signal 事件，由 Strategy 类产生。表现为是否做多、做空或者平仓。
    RiskManager 类接收 Signal 事件。
    '''
    def __init__(self, symbol, datetime, signal_type):
        '''
        symbol - 交易标的
        datetime - Signal 产生的时间
        signal_type - 'LONG'、'SHORT'.
        '''

        self.type = 'SIGNAL'
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type


class OrderEvent(Event):
    '''
    本类为Order事件，由 RiskManager 类产生，RiskManager类通过筛选和判断发出Order事件。
    Execution 类接收 Order 事件。
    '''
    def __init__(self, datetime, symbol, order_type, quantity, direction):
        '''       
        symbol - 交易标的.
        order_type - 'LONG', 'SHORT' 或者 'EXIT'.
        direction - 'BUY'、'SELL'
        '''
        self.type = 'ORDER'
        self.datetime = datetime
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

class FillEvent(Event):
    '''
    本类为 Fill 事件，由 Execution 类产生，Execution 类模拟交易的结果并产生 Fill 事件。
    Portfolio 类接收 Fill 事件。
    '''
    def __init__(self, datetime, symbol, exchange, quantity, 
                 direction, fill_type, fill_cost, commission = None):
        '''

        datetime - Fill 的时间
        symbol - 交易标的
        exchange - 交易发生的交易所
        direction - 'BUY'、'SELL')
        fill_type - 'LONG', 'SHORT' 或 'EXIT'.
        fill_cost - 标的完成交易的价格
        commission - 手续费
        '''
        self.type = 'FILL'
        self.datetime = datetime
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_type = fill_type
        self.fill_cost = fill_cost

        # Calculate commission
        if commission is None:
            self.commission = 0
        else:
            self.commission = commission