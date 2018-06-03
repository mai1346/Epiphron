# -*- coding: utf-8 -*-
"""
Created on Fri May 18 21:41:19 2018

@author: mai1346
"""

import datetime
import queue
import time
import pandas as pd
import Performance as pf
import Plot

class Backtest(object):
    """
    Enscapsulates the settings and components for carrying out
    an event-driven backtest.
    """

    def __init__(
        self, symbol_list, initial_capital,
        heartbeat, start_date, end_date, data_handler, 
        execution_handler, portfolio, risk_manager, strategy, benchmark
        ):
        """
        Initialises the backtest.

        args:
        symbol_list - The list of symbol strings.
        intial_capital - The starting capital for the portfolio.
        heartbeat - Backtest "heartbeat" in seconds
        start_date - The start datetime of the strategy.
        data_handler - (Class) Handles the market data feed.
        execution_handler - (Class) Handles the orders/fills for trades.
        portfolio - (Class) Keeps track of portfolio current and prior positions.
        strategy - (Class) Generates signals based on market data.
        """
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date
        self.end_date = end_date
        self.benchmark = benchmark

        self.data_handler_cls = data_handler
        self.execution_handler_cls = execution_handler
        self.portfolio_cls = portfolio
        self.strategy_cls = strategy
        self.risk_manager_cls = risk_manager

        self.events = queue.Queue()
        
        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1
       
        self._generate_trading_instances()

    def _generate_trading_instances(self):
        """
        Generates the trading instance objects from 
        their class types.
        """
        print(
            "Creating DataHandler, Strategy, Portfolio and ExecutionHandler"
        )
        self.data_handler = self.data_handler_cls(self.events, self.symbol_list, self.start_date,
                                                  self.end_date)
        self.strategy = self.strategy_cls(self.data_handler, self.events)
        self.portfolio = self.portfolio_cls(self.data_handler, self.events, self.start_date, 
                                            self.initial_capital)
        self.execution_handler = self.execution_handler_cls(self.events, self.data_handler)
        self.risk_manager = self.risk_manager_cls(self.events, self.portfolio)

    def _run_backtest(self):
        """
        Executes the backtest.
        """
            # Handle the events
        while True:
            try:
                event = self.events.get(False)
            except queue.Empty:                
                self.data_handler.update_bars()
            else:
                if not self.data_handler.continue_backtest:
                    break                
                elif event is not None:
                    if event.type == 'MARKET':
                        self.strategy.generate_signal(event)
                        self.portfolio.update_timeindex()
                    elif event.type == 'SIGNAL':
                        self.signals += 1                            
                        self.risk_manager.update_signal(event)

                    elif event.type == 'ORDER':
                        self.orders += 1
                        self.execution_handler.execute_order(event)

                    elif event.type == 'FILL':
                        self.fills += 1
                        self.portfolio.update_fill(event)
                


        time.sleep(self.heartbeat)

    def _output_performance(self):
        """
        Outputs the strategy performance from the backtest.
        """
        df= pf.create_equity_curve_dataframe(self.portfolio.all_holdings)
        print (df.tail(10))
        bench = pf.benchmark_dataframe(self.benchmark, self.start_date, self.end_date)
        print ("Creating summary stats...")
        stats, strategy_drawdown, bench_drawdown = pf.output_summary_stats(df, bench)
        
        output_df = pd.DataFrame({'strategy_equity':df['equity_curve'], 'bench_equity':bench['bench_curve'],
                                  'strategy_drawdown':strategy_drawdown, 'bench_drawdown':bench_drawdown}
                                )
        output_df.fillna(method = 'ffill', inplace = True)

        print ("Creating equity curve...")
        print (Plot.plot_equity_performance(output_df))
        print (stats)
        print ("Signals: %s" % self.signals)
        print ("Orders: %s" % self.orders)
        print ("Fills: %s" % self.fills)
        
        print ("Creating trade statistic")
        trade_log = self.portfolio.Tradelog        
        trade_log.create_trade_summary()
        print (Plot.plot_trade(trade_log.get_Tradelog(), self.data_handler.symbol_data))

    def simulate_trading(self):
        """
        Simulates the backtest and outputs portfolio performance.
        """
        self._run_backtest()
        self._output_performance()