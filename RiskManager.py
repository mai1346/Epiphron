# -*- coding: utf-8 -*-
"""
Created on Tue May 29 14:32:46 2018

@author: mai1346
"""
from Event import OrderEvent

class RiskManager():
    '''
    '''
    def __init__(self, events, portfolio):
        '''
        '''
        self.events = events
        self.portfolio = portfolio
        
    

    def generate_naive_order(self, signal):
        """
        Simply files an Order object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.
    
        Parameters:
        signal - The tuple containing Signal information.
        """
        order = None
    
        symbol = signal.symbol
        direction = signal.signal_type
        datetime = signal.datetime
    
        mkt_quantity = 1000
        #        mkt_quantity = self.current_holdings['cash']/self.data_handler.get_latest_bars_values(symbol, "close")[0]
        cur_quantity = self.portfolio.get_current_position(symbol)
    
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
        """
        Acts on a SignalEvent to generate new orders
        based on the portfolio logic.
        """
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)
