import investpy as inv
from datetime import datetime
import pandas as pd
import numpy as np


class PortfolioPrices(object):
    """
    Fetches historical data of assets given a date interval or a day, assuming today as end date.

    Constructor args:
    - assets_search_dict (dict<str, list>): dictionary of lists of assets names to search, indexed by asset type.
        currently supported asset types are: "stocks", "funds" and "etfs"
    - start_date (str): initial date of the historical data
    - [end_date] (str): end date of the historical data

    Methods:
    - refresh_assets_prices (None): updates historical data up to current date (to avoid creating a new object)
    - get_portfolio_prices (pd.DataFrame): returns historical data in a DataFrame
    """

    def __init__(self, assets_search_dict: dict, start_date: str, end_date: str = None):
        if end_date is None:
            end_date = datetime.today().strftime("%d/%m/%Y")
        self._assets_search_dict = assets_search_dict
        self._start_date = start_date
        self.portfolio_prices = self._fetch_portfolio_prices(
            assets_search_dict, start_date, end_date)

    def refresh_assets_prices(self):
        today = datetime.today().strftime("%d/%m/%Y")
        self.portfolio_prices = self._fetch_portfolio_prices(
            self._assets_search_dict, self._start_date, today)

    def get_portfolio_prices(self):
        return self.portfolio_prices

    def _get_assets_data_frames(self, assets: list, asset_function: list, country: str, start_date: str, end_date: str) -> list:
        """
        Get asset OHLCV values from investpy based on one country.

        Args: 
        - assets (list): assets to be downloaded
        - asset_function (list): investpy function that get historical data
        - country (str): origin country of the assets
        - start_date (str): initial date of the historical data
        - end_date (str): end date of the historical data

        Returns:
        - data_frame (list<pd.DataFrame>): assets data frames

        """

        data_frames = []

        for asset in assets:

            data_frame = asset_function(asset,
                                        country=country,
                                        from_date=start_date,
                                        to_date=end_date)

            data_frames.append(data_frame)

        return data_frames

    def _build_multi_index_tuples(self, header: list, sub_header: list) -> list:
        """
        Build list of tuples that construct a multiheader data frame.

        Args:
        - header (list): first header columns
        - sub_header (list): second header columns

        Returns:
        - tuples (list): multiheader pairs

        >>> build_multi_index_tuples(['Open', 'Close'], ['BPAC11', 'OIBR3', 'PETR4', 'MGLU3'])
        >>> [('Open', 'BPAC11'),
             ('Open', 'OIBR3'),
             ('Open', 'PETR4'),
             ('Open', 'MGLU3'),
             ('Close', 'BPAC11'),
             ('Close', 'OIBR3'),
             ('Close', 'PETR4'),
             ('Close', 'MGLU3')]

        """

        tuples = []

        for head in header:
            for sub_head in sub_header:
                tuples.append((head, sub_head))

        return tuples

    def _build_multi_index_data_frame(self, data_frames: list, sub_header: list, header_columns: list) -> pd.DataFrame:
        """
        Build a multiheader data frame. With Colums as header and assets as sub header.

        Args:
        - data_frames (list): list of data frames.
        - sub_header (list): sub header columns.
        - header_columns (list): header columns.
        """

        tuples = self._build_multi_index_tuples(header_columns, sub_header)

        multi_header = pd.MultiIndex.from_tuples(tuples)

        df = pd.concat(data_frames, axis=1).loc[:, dict(tuples).keys()]

        df.columns = multi_header

        return df

    def _fetch_portfolio_prices(self, assets_search_dict: dict, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get multiheader asset prices data frame. OHLC as principal header and asset names as sub header.

        Args: 
        - assets_search_dict (dict<str, list>): dictionary of lists of assets names to search, indexed by asset type.
            currently supported asset types are: "stocks", "funds" and "etfs"
        - start_date (str): initial date of the historical data
        - end_date (str): end date of the historical data

        Returns:
        - data_frame (list<pd.DataFrame>): assets data frames

        """
        data_frames = []

        for asset_type, assets_names in assets_search_dict.items():

            if asset_type == "stocks":

                stocks = assets_search_dict['stocks']

                data_frames_stocks = self._get_assets_data_frames(
                    stocks, inv.get_stock_historical_data, 'brazil', start_date=start_date, end_date=end_date)
                data_frames += [*data_frames_stocks]
                continue

            if asset_type == "funds":

                funds = assets_search_dict['funds']

                data_frames_funds = self._get_assets_data_frames(
                    funds, inv.get_fund_historical_data, 'brazil', start_date=start_date, end_date=end_date)
                data_frames += [*data_frames_funds]
                continue

            if asset_type == "etfs":

                etfs = assets_search_dict['etfs']

                data_frames_etfs = self._get_assets_data_frames(
                    etfs, inv.get_etf_historical_data, 'brazil', start_date=start_date, end_date=end_date)
                data_frames += [*data_frames_etfs]
                continue

        assets = [assets_names for assets_names in assets_search_dict.values()]

        columns = ['Open', 'High', 'Low', 'Close']

        portfolio_prices = self._build_multi_index_data_frame(
            data_frames, *assets, ['Close', 'Open', 'High', 'Low'])

        return portfolio_prices
