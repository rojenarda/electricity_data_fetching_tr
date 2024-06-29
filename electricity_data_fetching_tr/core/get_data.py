from .constants import DATASETS_DIRECTORY, EXCHANGE_RATES_API_ACCESS_KEY
from ..models import *

import os
import pytz
import json
import requests
import pandas as pd
from dateutil import parser
from datetime import datetime, timedelta
from workalendar.europe import Turkey
from forex_python.converter import CurrencyRates

class GetData:
    def __init__(self, dataset_classes:list=None, tz:str='Europe/Istanbul', dataset_dir=None):
        """
            Initialize the GetData class.

        Args:
            dataset_url (dict, optional): Contains URLs of the datasets and the keys to exctract.
            Defaults to DATASET_CLASSES.
            tz (str, optional): Timezone. Defaults to 'Europe/Istanbul'.
            dataset_dir (str, optional): Directory to save the datasets. Defaults to None.
        """
        if dataset_classes is None:
            dataset_classes = DATASET_CLASSES
        
        self.dataset_dir = dataset_dir if dataset_dir is not None else DATASETS_DIRECTORY
        
        self.tz = tz
        self.dataset_classes = dataset_classes
        self.c = CurrencyRates()
    
    def _convert_datetime_str(self, dt:datetime) -> str:
        """
        Convert a datetime object to ISO 8601 format.

        Args:
            dt (str): Datatime string in the format 'YYYY-MM-DD HH:MM:SS'.

        Returns:
            str: Datetime string in ISO 8601 format.
        """
        tz = pytz.timezone(self.tz)
        dt_tz = dt.astimezone(tz)
        iso_format = dt_tz.isoformat()
        return iso_format
        
    def _parse_datetime(self, date_str:str) -> datetime:
        """
        Parse a string to a datetime object.
        Tries different formats to parse the string.
        
        Args:
            date_str (str): Datetime string.
        
        Returns:
            datetime: Datetime object.
        """
        return parser.parse(date_str)


    def _send_request(self, url:str, body:dict=None, headers:dict=None, method:str='GET'):
        """
        Send a request to the given URL.

        Args:
            url (str): URL to send the request to.
            body (dict, optional): Body of the request. Defaults to None.
            headers (dict, optional): Headers of the request. Defaults to None.
            method (str, optional): Method of the request. Defaults to 'GET'.

        Returns:
            dict: Response of the request.
        """
        if headers is None:
            headers = {}

        if body is not None:
            body = json.dumps(body)
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
        else: body = None
        
        response = requests.request(method, url, headers=headers, data=body)

        return response.json()
    
    def _get_exchange_rate_api(self, date:datetime, base:str='TRY', target:str='USD', shift_days:int=2):
        if EXCHANGE_RATES_API_ACCESS_KEY is None:
            EXCHANGE_RATES_API_ACCESS_KEY = input('Enter the exchange rates API access key (can be obtained from https://exchangeratesapi.io/): ')
        date = (date - timedelta(days=shift_days)).strftime('%Y-%m-%d')
        response = requests.get(f"http://api.exchangeratesapi.io/v1/{date}?access_key={EXCHANGE_RATES_API_ACCESS_KEY}&symbols={target},{base}")
        return response.json()['rates'][target] / response.json()['rates'][base]

    
    def _get_exchange_rate(self, date:datetime, base:str='TRY', target:str='USD'):
        return self.c.get_rate(base, target, date)
    
    def _convert_currency(self, df:pd.DataFrame, base:str='TRY', target:str='USD'):
        # TOO SLOW!!!!
        unique_dates = pd.Series(df.index.date).unique()
        exchange_rates = {date: self._get_exchange_rate(datetime(date.year, date.month, date.day), base, target) for date in unique_dates}
        df['ExchangeRate'] = df.index.map(lambda x: exchange_rates[x.date()])
        
        df['BalancingMarketPrice'] = df['BalancingMarketPrice'] * df['ExchangeRate']
        df['Price'] = df['Price'] * df['ExchangeRate']
        
        del df['ExchangeRate']
        return df
    
    def get_data(self, start_date:str, end_date:str, file_name='data', csv_to_update:str=None):
        """
        Get data from the dataset API and write it to a CSV file generated with start and end dates.
        If csv_to_update is not None, append the data to the file.
        Args:
            start_date (str): Start date in the format 'YYYY-MM-DD HH:MM:SS'.
            end_date (str): End date in the format 'YYYY-MM-DD HH:MM:SS'.
            csv_to_update (str, optional): Path of the CSV file to update. Defaults to None.
        """
        start_date_dt = self._parse_datetime(start_date)
        end_date_dt = self._parse_datetime(end_date)
        
        # add timezone to datetimes if they are not timezone aware
        
        
        if csv_to_update is not None:
            # Check if the file exists
            if not os.path.exists(csv_to_update):
                raise FileNotFoundError('The file does not exist.')
            self.csv_file_name = csv_to_update
        else:
            if file_name:
                self.csv_file_name = f"{self.dataset_dir}/{file_name}.csv"
            else:
                self.csv_file_name = f"{self.dataset_dir}/dataset_electricity_{start_date_dt.strftime('%Y-%m-%d')}_{end_date_dt.strftime('%Y-%m-%d')}.csv"
        
        if end_date_dt < start_date_dt:
            raise ValueError('End date must be greater than start date.')
        
        # try:
        #     if end_date_dt > datetime.now(tz=pytz.timezone(self.tz)):
        #         raise ValueError('End date must be less than current date.')
        # except TypeError as e:
        #     if end_date_dt > datetime.now():
        #         raise ValueError('End date must be less than current date.')
            
        windows = list()
        if end_date_dt - start_date_dt > timedelta(days=3*365):
            # API only accepts requests for 3 years at most, paginate if more is requested.
            while start_date_dt <= end_date_dt:
                temp_end_date = min(start_date_dt + timedelta(days=3*365), end_date_dt)
                windows.append((start_date_dt, temp_end_date))
                start_date_dt = temp_end_date + timedelta(days=1)
        else:
            windows.append((start_date_dt, end_date_dt))
        
        tr_calendar = Turkey()
        for index, (start_time, end_time) in enumerate(windows):
            df = pd.DataFrame()
            start_time_iso = self._convert_datetime_str(start_time)
            end_time_iso = self._convert_datetime_str(end_time)
            for dataset_class in self.dataset_classes:
                try:
                    df_temp = dataset_class(start_time_iso, end_time_iso, self.tz).get_data()
                    df = pd.concat([df, df_temp], axis=1)
                # Add Day, Month, Year, Hour, Weekday columns
                
                except Exception as e:
                    print(f"Error: {e}")
                    continue
            
            # Convert to datetime index
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
                
            # Add new columns
            df['Day'] = df.index.day.astype(float)
            df['Month'] = df.index.month.astype(float)
            df['Year'] = df.index.year.astype(float)
            df['Hour'] = df.index.hour.astype(float)
            df['Weekday'] = df.index.weekday.astype(float)
            df['Holiday'] = df.index.map(lambda x: tr_calendar.is_holiday(x.date())).astype(float)
            # Hour of the week
            df['Mod168'] = (df['Weekday']) * 24 + df['Hour'] # TODO: Fix this...
            
            # Get the currency using the price in TRY and USD
            # can't calculate exchange rate if price is 0. Try to get it another way.
            # Causes slight errors if the BalancingMarketPrices are shifted
            df['ExchangeRate'] = df['Price'] / df['PriceTry']
            
            # Find missing exchange rates _get_exchange_rate
            missing_exchange_rates = df[df['ExchangeRate'].isna()].index
            exchange_rates_cache = {}
            for date in missing_exchange_rates:
                try:
                    if date.date() not in exchange_rates_cache:
                        exchange_rates_cache[date.date()] = self._get_exchange_rate_api(date)
                    df.loc[date, 'ExchangeRate'] = exchange_rates_cache[date.date()]
                except:
                    continue
            
            # Fill the rest of na values with the previous value
            df['ExchangeRate'] = df['ExchangeRate'].ffill().astype('float')
            
            df['BalancingMarketPrice'] = df['BalancingMarketPrice'] * df['ExchangeRate']
            
            df.drop(columns=['PriceTry', 'ExchangeRate'], inplace=True)
            
            if index == 0 and csv_to_update == None:
                # If this is the first iteration, create the file and write the data to it.
                df.to_csv(self.csv_file_name)
            else:
                # Append the data to the file.
                df.to_csv(self.csv_file_name, mode='a', header=False)
