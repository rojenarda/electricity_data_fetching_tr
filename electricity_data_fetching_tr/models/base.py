import json
import requests
import pandas as pd
from datetime import timedelta
from dateutil import parser

class Data:
    def __init__(self, url:str, start_date:str, end_date:str, keys:list, tz:str='Europe/Istanbul'):
        self.url = url
        self.start_date = start_date
        self.end_date = end_date
        self.keys = keys
        self.tz = tz
        
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
    
    def _get_start_end_dates(self, start_date:str, end_date:str, lag_hours:int=0):
        """Get the start and end dates with lag hours added to the dates.
        Return a tuple containing 4 elements, start date in datetime format, start date in ISO 8601 format,
        end date in datetime format, end date in ISO 8601 format in this order.

        Args:
            start_date (str): Start date in ISO 8601 format.
            end_date (str): End date in ISO 8601 format.
            lag_hours (int, optional): number of hours to subtract from the dates. Defaults to 0.
        """
        
        start_date_dt = parser.parse(start_date) - timedelta(hours=lag_hours)
        end_date_dt = parser.parse(end_date) - timedelta(hours=lag_hours)
        
        new_start_date = start_date_dt.isoformat()
        new_end_date = end_date_dt.isoformat()
        
        return start_date_dt, new_start_date, end_date_dt, new_end_date
        
    
    def get_data(self, extra_params=None, lag_hours:int=0):
        if extra_params is None:
            extra_params = {}
        
        start_date_new_dt, start_date_new_str, end_date_new_dt, end_date_new_str = self._get_start_end_dates(self.start_date, self.end_date, lag_hours)
        
        body = {'startDate': start_date_new_str, 'endDate': end_date_new_str}
        for param in extra_params:
            body[param] = extra_params[param]
        
        response = self._send_request(url=self.url, body=body, method='POST')
        df = pd.DataFrame(response['items'], columns=self.keys)
        
        # Localize the time
        df['date'] = pd.to_datetime(df['date'], utc=True)
        df['date'] = df['date'].dt.tz_convert(self.tz)
        df['date'] = df['date'].dt.tz_localize(None)
        
        df['date'] = df['date'] + timedelta(hours=lag_hours)
        
        df.index = df['date']
        df.drop(columns=['date'], inplace=True)
        
        # Check if the data is complete for the given date range
        start_date_dt = parser.parse(self.start_date.split('T')[0]).replace(hour=0)
        end_date_dt = parser.parse(self.end_date.split('T')[0]).replace(hour=23)
        
        if len(df) == 0:
            raise ValueError('No data available for the given date range.')

        # If the data fetched is not complete, create a new dataframe with the missing dates.
        if start_date_dt < df.index[0]:
            temp_date = df.index[0] - timedelta(hours=1)
            date_range = pd.date_range(start=start_date_dt, end=temp_date, freq='h')
            df_temp = pd.DataFrame(index=date_range, columns=df.columns)
            df = pd.concat([df_temp, df])
        
        if end_date_dt > df.index[-1]:
            temp_date = df.index[-1] + timedelta(hours=1)
            date_range = pd.date_range(start=temp_date, end=end_date_dt, freq='h')
            df_temp = pd.DataFrame(index=date_range, columns=df.columns)
            df = pd.concat([df, df_temp])

        return df