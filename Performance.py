# -*- coding: utf-8 -*-
"""
Created on Fri May 18 11:42:21 2018

@author: mai1346
"""

import numpy as np
import pandas as pd

def calSharpe(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on a 
    benchmark of zero (i.e. no risk-free rate information).

    args:
        returns - A pandas Series representing period percentage returns.
        periods - Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    returns:
        the sharpe ratio based on period chosen
    """
    return np.sqrt(periods) * returns.mean() / returns.std()

def calDrawdown(equity):
    """
    args:
        equity: a panda series represents the equity of a specific asset.
    returns:
        Max drawdown
        Calendar duration of the max drawdown
    """
    drawdown = equity/equity.cummax()-1
    maxdrawdown = drawdown.min() #the value of maxdrawdown
#    end = drawdown.idxmin()# find the date of maxdrawdown
#    start = equity[:end].idxmax() # find the starting date of maxdrawdown
#    duration = end - start # calendar duration of the maxdrawdown
    
    return drawdown, maxdrawdown


def create_equity_curve_dataframe(all_holdings):
    """
	Creates a pandas DataFrame from the all_holdings
	list of dictionaries.
	"""
    curve = pd.DataFrame(all_holdings)
    curve.set_index('datetime', inplace=True)
    curve['returns'] = curve['total'].pct_change()
    curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
    return curve


def output_summary_stats(curve):
    """
	Creates a list of summary statistics for the portfolio.
	"""
    total_return = curve['equity_curve'].iloc[-1]
    returns = curve['returns']
    equity = curve['equity_curve']
    equity.plot(figsize=(16, 9))

    sharpe_ratio = calSharpe(returns, periods=252)
    drawdown, max_dd = calDrawdown(equity)
    curve['drawdown'] = drawdown

    stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
             ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
             ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0))]

    return stats