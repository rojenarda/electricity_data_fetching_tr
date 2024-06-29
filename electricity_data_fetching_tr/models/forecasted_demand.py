from .base import Data

class ForecastedDemand(Data):
    def __init__(self, start_date: str, end_date: str, tz:str):
        url = 'https://seffaflik.epias.com.tr/electricity-service/v1/consumption/data/load-estimation-plan'
        keys = ['date', 'lep']
        super().__init__(url, start_date, end_date, keys, tz)
    
    def get_data(self, lag_hours:int=24):
        df = super().get_data(lag_hours=lag_hours)
        df.rename(columns={'lep': 'ForecastedDemand'}, inplace=True)
        return df
