import pandas as pd 
import numpy as np
from matplotlib import pyplot as plt
import requests
import csv
from datetime import datetime

TODAY = datetime.today().strftime("%d/%m/%Y")

from utils import get_wallet
from prices import get_portfolio_prices

class Portfolio:
    
    def __init__(self, google_sheet_key: str):
        
        self.wallet = self._mount_wallet_data_frame(google_sheet_key)
        
        self.prices = self._get_portfolio_prices()
        
        self._mount_wallet_shares()
        
        self.allocations = self._get_allocation_time_series()
        
        self.portfolio = self._get_portfolio()
        
    def get_patrimony(self):

        patrimony = self.portfolio.sum(axis=1)

        return patrimony
    
    def get_returns(self):
    
        weights = self.portfolio.div(self.portfolio.sum(axis=1), axis=0).fillna(0)

        returns = pd.DataFrame(index = weights.index)
        returns['Returns'] = 0

        for time in weights.index:
            returns['Returns'].loc[time] = np.dot(self.prices['Close'].pct_change().loc[time], weights.loc[time])

        return returns
    
    def get_cumulative_returns(self):
    
        returns = self.get_returns()

        cumulative_returns = (1 + returns).cumprod()

        return cumulative_returns
        
    def _get_wallet(self, google_sheet_key: str) -> list: 
        """Gets wallet from google public spreadsheet
        Args
        - google_sheet_key (str): key placed on the url of the spreadsheet
        Returns
        - (list<dict>): each item represents a position on the wallet and the dict keys are: date, securitie and quantity

        >>> get_wallet('1KHC1z4eO7CSekLK0ZaypIzrO5c5pVCq8Gx-hxL-sUaM')
        >>> [{'data': '04/01/2021', 'ativo': 'ITSA4', 'quantidade': '200'},
             {'data': '11/01/2021', 'ativo': 'OIBR3', 'quantidade': '1000'},
             {'data': '22/07/2020', 'ativo': 'BPAC11', 'quantidade': '500'}]
        """
        google_sheet_url = f"https://docs.google.com/spreadsheet/ccc?key={google_sheet_key}&output=csv"
        r = requests.get(google_sheet_url) 
        
        assert r.status_code == 200 
        
        decoded_content = r.content.decode('utf-8') 
        reader = csv.DictReader(decoded_content.splitlines(), delimiter=',')
        
        return [row for row in reader]
    
    def _mount_wallet_data_frame(self, google_sheet_key: str) -> pd.DataFrame:
    
        wallet_items = self._get_wallet(google_sheet_key)

        wallet = pd.DataFrame(wallet_items).set_index('Date')

        wallet.index = pd.to_datetime(wallet.index)

        return wallet
    
    def _get_assets_by_type(self, wallet, asset_type):
    
        asset_filter = wallet[wallet.asset_type == asset_type]

        assets = set(asset_filter.asset_name.to_list())

        return assets
    
    def _get_portfolio_prices(self):
    
        funds = self._get_assets_by_type(self.wallet, 'fund')
        stocks = self._get_assets_by_type(self.wallet, 'stock')
        etfs = self._get_assets_by_type(self.wallet, 'etf')

        portfolio_prices = get_portfolio_prices(stocks, funds, etfs, start_date='01/01/2018').asfreq('B')

        return portfolio_prices
    
    def _mount_wallet_shares(self):

        wallet_shares = []

        for i in range(len(self.wallet)):

            asset_name = self.wallet.iloc[i].asset_name
            value = self.wallet.iloc[i].value
            date = self.wallet.index[i]

            shares = float(value) / self.prices['Close'][asset_name][date]

            wallet_shares.append(shares)

        self.wallet['shares'] = wallet_shares 

        for asset in self.wallet.asset_name.unique():

            self.wallet.loc[self.wallet.asset_name == asset, 'shares'] = self.wallet[self.wallet.asset_name == asset].shares.cumsum()
        
    def _get_allocation_time_series(self):
    
        allocations = self.wallet.pivot(columns = 'asset_name').shares.asfreq('B')

        last_date = allocations.index[-1]

        df = pd.DataFrame(pd.date_range(start=last_date, end=TODAY, freq='B'))
        df.columns = ['Date']

        allocations = allocations.merge(df, on='Date', how='outer').set_index('Date')

        allocations = allocations.fillna(method='ffill').astype(np.float64).asfreq('B')

        return allocations
    
    def _get_portfolio(self):
    
        portfolio = (self.prices['Close'].loc[:, self.allocations.columns] * self.allocations).asfreq('B').fillna(method='ffill')

        return portfolio
