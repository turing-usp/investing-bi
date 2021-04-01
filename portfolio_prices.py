import investpy as inv
from datetime import datetime
import pandas as pd
import numpy as np

today = datetime.today().strftime("%d/%m/%Y")

def get_stock_data_frames(stocks, country, start_date, end_date):
    
    data_frames = []
    
    for stock in stocks:
        
        data_frame = inv.get_stock_historical_data(stock=stock,
                                                   country=country,
                                                   from_date=start_date,
                                                   to_date=end_date)
        
        data_frames.append(data_frame)
    
    return data_frames

def get_funds_data_frames(funds, country, start_date, end_date):
    
    data_frames = []
    
    for fund in funds:
        
        data_frame = inv.get_fund_historical_data(fund=fund,
                                                  country=country,
                                                  from_date=start_date,
                                                  to_date=end_date)
        
        data_frames.append(data_frame)
    
    return data_frames

def get_etfs_data_frames(etfs, country, start_date, end_date):
    
    data_frames = []
    
    for etf in etfs:
        
        data_frame = inv.get_etf_historical_data(etf=etf,
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
    
    data_frames_stocks = get_stock_data_frames(stocks, 'brazil', start_date=start_date, end_date=end_date)
    data_frames_funds = get_funds_data_frames(funds, 'brazil', start_date=start_date, end_date=end_date)
    data_frames_etfs = get_etfs_data_frames(etfs, 'brazil', start_date=start_date, end_date=end_date)
    
    data_frames = [*data_frames_stocks, *data_frames_funds, *data_frames_etfs]

    assets = [*stocks, *funds, *etfs]
    
    portfolio_prices = build_multi_index_data_frame(data_frames, assets, columns)
    
    return portfolio_prices