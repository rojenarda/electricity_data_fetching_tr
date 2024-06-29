import pandas as pd

from datetime import datetime, timedelta
from dateutil import parser

from .base import Data

class DayAheadPrices(Data):
    """Gets the DayAheadPrices from the API. Extracts date, price in TRY and price in USD.
    Price in TRY is used to get the exchange rate in the given date.
    """
    def __init__(self, start_date: str, end_date: str, tz:str):
        url = 'https://seffaflik.epias.com.tr/electricity-service/v1/markets/dam/data/mcp'
        keys = ['date', 'price', 'priceUsd']
        super().__init__(url, start_date, end_date, keys)
        
    def get_data(self, lag_hours:int=0):
        
        # API throws an error if we are requesting the next day's day ahead prices before 14:00.
        end_date_dt = parser.parse(self.end_date).replace(hour=0)
        if end_date_dt.date() > datetime.now().date() and datetime.now().hour < 14:
            new_end_date_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            self.end_date = new_end_date_dt.astimezone(tz=pytz.timezone(self.tz)).isoformat() # Update the end date to the current date.
            
            # Create a new dataframe with the remaining hours of the day with empty values.
            index = pd.date_range(start=new_end_date_dt + timedelta(days=1), periods=24, freq='h')
            remaining_df = pd.DataFrame(columns=['PriceTry', 'Price'], index=index)
            
            if self.end_date < self.start_date:
                # No data left to fetch
                return remaining_df
        
        df = super().get_data(lag_hours=lag_hours)
        df.rename(columns={'price': 'PriceTry', 'priceUsd': 'Price'}, inplace=True)
        
        # if remaining_df is defined add it to the dataframe
        if 'remaining_df' in locals():
            df = pd.concat([df, remaining_df])
        
        return df