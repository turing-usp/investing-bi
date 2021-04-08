import investpy as inv
from datetime import datetime
import pandas as pd
import numpy as np

today = datetime.today().strftime("%d/%m/%Y")


def get_assets_data_frames(assets: list, asset_function: list, country: str, start_date: str, end_date: str) -> list:
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


def build_multi_index_tuples(header: list, sub_header: list) -> list:
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


def build_multi_index_data_frame(data_frames: list, sub_header: list, header_columns: list) -> pd.DataFrame:
    """
    Build a multiheader data frame. With Colums as header and assets as sub header.

    Args:
    - data_frames (list): list of data frames.
    - sub_header (list): sub header columns.
    - header_columns (list): header columns.
    """

    tuples = build_multi_index_tuples(header_columns, sub_header)

    multi_header = pd.MultiIndex.from_tuples(tuples)

    df = pd.concat(data_frames, axis=1).loc[:, dict(tuples).keys()]

    df.columns = multi_header

    return df


def get_portfolio_prices(stocks: list, funds: list, etfs: list, start_date: str, end_date=today) -> pd.DataFrame:
    """
    Get multiheader asset prices data frame. OHLC as principal header and asset names as sub header.

    Args: 
    - stocks (list): stock names
    - funds (list): funds names
    - etfs (str): etfs names
    - start_date (str): initial date of the historical data
    - end_date (str): end date of the historical data

    Returns:
    - data_frame (list<pd.DataFrame>): assets data frames
    
    """
    data_frames_stocks = get_assets_data_frames(
        stocks, inv.get_stock_historical_data, 'brazil', start_date=start_date, end_date=end_date)
    data_frames_funds = get_assets_data_frames(
        funds, inv.get_fund_historical_data, 'brazil', start_date=start_date, end_date=end_date)
    data_frames_etfs = get_assets_data_frames(
        etfs, inv.get_etf_historical_data, 'brazil', start_date=start_date, end_date=end_date)

    data_frames = [*data_frames_stocks, *data_frames_funds, *data_frames_etfs]

    assets = [*stocks, *funds, *etfs]
    
    columns = ['Open', 'High', 'Low', 'Close']

    portfolio_prices = build_multi_index_data_frame(
        data_frames, assets, ['Close', 'Open', 'High', 'Low'])

    return portfolio_prices
