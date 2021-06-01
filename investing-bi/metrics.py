from turingquant.metrics import *
from returns import Portfolio

def get_metrics(goog_sheet_key, window = 20, time_window = 3):
    
    p = Portfolio(goog_sheet_key)
    
    returns = p.get_returns()
    
    metrics = {'Sharpe Ratio'       : sharpe_ratio(returns),
               'Drawdown'           : drawdown(returns),
               'Rolling Sharpe'     : rolling_sharpe(returns, window = window),
               'EWMA Volatility'    : ewma_volatility(returns, window = window),
               'Cumulative Returns' : cumulative_returns(returns, return_type = 'simp'),
               'Rolling Std'        : rolling_std(returns, window = window),
               'CAGR'               : cagr(returns),
               'MAR Ratio'          : mar_ratio(returns, time_window = time_window),
               'Value at Risk'      : value_at_risk(returns)
    }
    
    return metrics
    