import investpy as inv
from datetime import datetime
import pandas as pd
import numpy as np

today = datetime.today().strftime("%d/%m/%Y")


def get_assets_data_frames(assets, asset_function, country, start_date, end_date):

    data_frames = []

    for asset in assets:

        data_frame = asset_function(asset,
                                    country=country,
                                    from_date=start_date,
                                    to_date=end_date)

        data_frames.append(data_frame)

    return data_frames


def build_multi_index_tuples(header, sub_header):

    tuples = []

    for head in header:
        for sub_head in sub_header:
            tuples.append((head, sub_head))

    return tuples


def build_multi_index_data_frame(data_frames, stocks, columns):

    tuples = build_multi_index_tuples(columns, stocks)

    multi_header = pd.MultiIndex.from_tuples(tuples)

    df = pd.concat(data_frames, axis=1).loc[:, dict(tuples).keys()]

    df.columns = multi_header

    return df


def get_portfolio_prices(stocks, funds, etfs, start_date, end_date=today):

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
        data_frames, assets, columns)

    return portfolio_prices
