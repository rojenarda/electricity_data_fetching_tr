import pandas as pd

from .base import Data
from .forecasted_demand import ForecastedDemand
from .forecasted_supply import ForecastedSupply

class ForecastedDemandSupply(Data):
    def __init__(self, start_date: str, end_date: str, tz:str):
        self.start_date = start_date
        self.end_date = end_date
        self.tz = tz
        
    def get_data(self, lag_hours:int=24):
        forecasted_demand = ForecastedDemand(self.start_date, self.end_date, self.tz).get_data(lag_hours=lag_hours)
        forecasted_supply = ForecastedSupply(self.start_date, self.end_date, self.tz).get_data(lag_hours=lag_hours)
        
        if not forecasted_demand.index.equals(forecasted_supply.index):
            raise ValueError('Indices of the dataframes do not match.')
        
        demand_supply = forecasted_demand['ForecastedDemand'] / forecasted_supply['ForecastedSupply']
        
        return pd.DataFrame(demand_supply, columns=['ForecastedDemandSupply'])
        