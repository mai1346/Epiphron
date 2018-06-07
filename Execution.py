# -*- coding: utf-8 -*-
"""
Created on Fri May 18 21:24:46 2018

@author: mai1346
"""

from Event import FillEvent
from abc import ABC, abstractmethod

class ExecutionHandler(ABC):
    @abstractmethod
    def execute_order(self, event):

        raise NotImplementedError("Should implement execute_order()")

class SimulatedExecutionHandler(ExecutionHandler):
    '''
    生成模拟的FILL事件。
    '''
    
    def __init__(self, events, data_handler):

        self.events = events
        self.data_handler = data_handler

    def execute_order(self, orderevent):

        if orderevent.type == 'ORDER':
            fill_event = FillEvent(
                                    orderevent.datetime, orderevent.symbol,
                                    'Test_Exchange', orderevent.quantity, orderevent.direction, orderevent.order_type, 
                                    self.data_handler.get_latest_bars_values(orderevent.symbol, "close")[0] # [0] because it's a np array
                                    )
            self.events.put(fill_event)