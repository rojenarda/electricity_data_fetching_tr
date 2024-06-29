from .base import Data

class BalancingMarketPrices(Data):
    def __init__(self, start_date: str, end_date: str, tz:str, shift:bool=True):
        # If shift is True, the data is shifted by 24 hours.
        url = 'https://seffaflik.epias.com.tr/electricity-service/v1/markets/bpm/data/system-marginal-price'
        keys = ['date', 'systemMarginalPrice']
        self.shift = shift

        super().__init__(url, start_date, end_date, keys, tz)
    
    def get_data(self, lag_hours:int=48):
        df = super().get_data(lag_hours=lag_hours)
        
        df.rename(columns={'systemMarginalPrice': 'BalancingMarketPrice'}, inplace=True)
        

        return df