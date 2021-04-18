import pandas as pd 
import numpy as np
from matplotlib import pyplot as plt

from utils import get_wallet
from portfolio_prices import get_portfolio_prices

def mount_wallet_data_frame(google_sheet_key: str) -> pd.DataFrame:
    
    wallet_items = get_wallet(google_sheet_key)
    
    wallet = pd.DataFrame(wallet_items).set_index('Date')
    
    wallet.index = pd.to_datetime(wallet.index, format = '%d/%m/%Y')
    
    return wallet

def get_assets_by_type(wallet, asset_type):
    
    asset_filter = wallet[wallet.asset_type == asset_type]
    
    assets = set(asset_filter.asset_name.to_list())
    
    return assets

def get_portfolio_performace(wallet):
    
    funds = get_assets_by_type(wallet, 'fund')
    stocks = get_assets_by_type(wallet, 'stock')
    etfs = get_assets_by_type(wallet, 'etf')
    
    allocations = wallet.pivot(columns = 'asset_name').value.fillna(0)
    
    portfolio_prices = get_portfolio_prices(stocks, funds, etfs, start_date='01/01/2018').asfreq('B')
    
    return portfolio_prices

def mount_wallet_shares(wallet, prices):
    
    wallet_shares = []
    
    for i in range(len(wallet)):
        
        asset_name = wallet.iloc[i].asset_name
        value = wallet.iloc[i].value
        date = wallet.index[i]
        
        shares = float(value) / prices[asset_name][date]
        
        wallet_shares.append(shares)
        
    wallet['shares'] = wallet_shares 
    
    for asset in wallet.asset_name.unique():
        
        wallet.loc[wallet.asset_name == asset, 'shares'] = wallet[wallet.asset_name == asset].shares.cumsum()
    
    return wallet

def get_allocation_time_series(wallet):
    
    allocations = wallet.pivot(columns = 'asset_name').shares.asfreq('B')
    
    last_date = allocations.index[-1]
    
    df = pd.DataFrame(pd.date_range(start=last_date, end='2021-04-09', freq='B'))
    df.columns = ['Date']
    
    allocations = allocations.merge(df, on='Date', how='outer').set_index('Date')
    
    allocations = allocations.fillna(method='ffill').astype(np.float64).asfreq('B')
    
    return allocations

def get_portfolio(prices, allocations):
    
    portfolio = (prices.loc[:, allocations.columns] * allocations).asfreq('B').fillna(method='ffill')
    
    return portfolio

def get_patrimony(portfolio):
    
    patrimony = portfolio.sum(axis=1)
    
    return patrimony

def get_returns(prices, portfolio):
    
    weights = portfolio.div(portfolio.sum(axis=1), axis=0).fillna(0)
    
    returns = pd.DataFrame(index = weights.index)
    returns['Returns'] = 0

    for time in weights.index:
        returns['Returns'].loc[time] = np.dot(prices.pct_change().loc[time], weights.loc[time])
        
    return returns

def get_cumulative_returns(prices, portfolio):
    
    returns = get_returns(prices, portfolio)
                          
    cumulative_returns = (1 + returns).cumprod()
                          
    return cumulative_returns
