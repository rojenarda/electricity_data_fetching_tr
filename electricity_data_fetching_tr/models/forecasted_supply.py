from .base import Data

class ForecastedSupply(Data):
    def __init__(self, start_date: str, end_date: str, tz:str):
        url = 'https://seffaflik.epias.com.tr/electricity-service/v1/generation/data/aic'
        keys = ['date', 'toplam']
        super().__init__(url, start_date, end_date, keys, tz)
    
    def get_data(self, lag_hours:int=24):
        extra_params = {'region': 'TR1'}
        df = super().get_data(extra_params=extra_params, lag_hours=lag_hours)
        df.rename(columns={'toplam': 'ForecastedSupply'}, inplace=True)
        return df
