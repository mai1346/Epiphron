# -*- coding: utf-8 -*-
"""
Created on Fri May 18 21:41:19 2018

@author: mai1346
"""

import queue
import time
import pandas as pd
import Performance as pf
import Plot


class Backtest(object):
    '''
    回测类，
    '''
    def __init__(
        self, symbol_list, initial_capital,
        heartbeat, start_date, end_date, data_handler, 
        execution_handler, portfolio, risk_manager, strategy, benchmark
        ):
        '''
        初始化回测，

        symbol_list - 应用策略的标的资产列表
        intial_capital - 初始资金
        heartbeat - 等待间隔，回测中默认为0，实盘系统则按需求进行调整
        start_date - 回测开始日期
        end_date - 回测结束日期
        data_handler - 数据源类
        execution_handler - 执行类
        portfolio - Portfolio类
        strategy - 策略类
        '''
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
       
        self._create_trading_instances()

    def _create_trading_instances(self):
        '''
        根据输入信息实例化所有类
        '''
        print(
            "Creating DataHandler, Strategy, Portfolio and ExecutionHandler"
        )
        self.data_handler = self.data_handler_cls(self.events, self.symbol_list, self.start_date,
                                                  self.end_date)
        self.strategy = self.strategy_cls(self.data_handler, self.events)
        self.portfolio = self.portfolio_cls(self.data_handler, self.events, self.start_date, 
                                            self.initial_capital)
        self.execution_handler = self.execution_handler_cls(self.events, self.data_handler)
        self.risk_manager = self.risk_manager_cls(self.events, self.portfolio, self.data_handler)

    def _run_backtest(self):
        '''
        回测主循环
        '''
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
        '''
        输出所有Performance
        '''
        print ("Creating equity curve...")
        df= pf.create_equity_curve_dataframe(self.portfolio.all_holdings)
        print (df.head(40))
        bench = pf.create_benchmark_dataframe(self.benchmark, self.start_date, self.end_date)
        print ("Creating summary stats...")
        stats, strategy_drawdown, bench_drawdown = pf.output_summary_stats(df, bench)
        print (stats)
        print ("Signals: %s" % self.signals)
        print ("Orders: %s" % self.orders)
        print ("Fills: %s" % self.fills)
        
        output_df = pd.DataFrame({'strategy_equity':df['equity_curve'], 'bench_equity':bench['bench_curve'],
                                  'strategy_drawdown':strategy_drawdown, 'bench_drawdown':bench_drawdown})
        output_df.fillna(method = 'ffill', inplace = True)
        Plot.plot_equity_performance(output_df)
        
        print ("Creating trade statistics...")
        trade_log = self.portfolio.Tradelog        
        trade_log.create_trade_summary()
        
        trade_plot_data = pf.create_trade_plot_dataframe(self.symbol_list, self.data_handler)
        Plot.plot_trade(trade_log.get_Tradelog(), trade_plot_data)

    def simulate_trading(self):
        '''
        进行模拟回测
        '''
        self._run_backtest()
        self._output_performance()