import pandas as pd
from math import log, sqrt, exp
from pydantic import BaseModel, validator, root_validator
from typing import List, Dict, Optional

#TODO can we expect that the date in data is always single day by order otherwise we need to validate that the date dif between rows is equal to time horizon? this would require calander work for weekends and other non trading days / missing days
#TODO what risktypes do we expect next to FX, is IR still a factor in use. What factor uses the relative type?
#TODO check potential mismatch of equations. Numbers check out but sensitivty seems to be ignored for the scenario calculations.
#TODO check required precision

class Portofolio_asset(BaseModel):
    asset_name:str
    risk_type: str
    asset_value: float
    asset_market_rates: Optional[pd.DataFrame]
    profit_loss_vector: Optional[pd.DataFrame]

    class Config:
        arbitrary_types_allowed = True # allows for use of dataframes
    
    @root_validator
    def validate_market_rates(cls, values):
        """ 
        Validate dat the dataframe contains asset that has the same name as the asset_name, index is date.
        """
        df_market_rates = values['asset_market_rates']
        if not set(['date', 'asset', 'market_rate']).issubset(df_market_rates.columns):
            raise ValueError(f"Asset market rates should contain, date, asset and market rate")
        else:
            #ensure only asset beloning to asset are added
            mask_asset = df_market_rates["asset"] == values["asset_name"]
            df_market_rates = df_market_rates[mask_asset].drop(columns="asset")

            #if dates are not a datetime, format as datetime
            if not 'datetime' in df_market_rates['date'].dtypes.name.lower():
                df_market_rates['date'] = pd.to_datetime(df_market_rates['date'])
            #ensure follow up descending order
            df_market_rates = df_market_rates.sort_values("date", ascending=False)
            df_market_rates = df_market_rates.set_index('date')

            #Check if market rate is a float.
            if not 'float' in df_market_rates['market_rate'].dtypes.name.lower():
                df_market_rates['market_rate'] = df_market_rates["market_rate"].str.replace(",", ".")
                avg_float_lenght = df_market_rates['market_rate'].apply(lambda x: len(x)).sum() / len(df_market_rates['market_rate'])
                # Check if values have the same precision
                if avg_float_lenght != abs(avg_float_lenght):
                    raise UserWarning(f"Asset market rates contain different precisions, {set(avg_float_lenght)}, where found. this can lead to numerical inacurracies")
            df_market_rates['market_rate'] = pd.to_numeric(df_market_rates['market_rate'])
            values["asset_market_rates"] = df_market_rates

        return values
    
    @validator('risk_type')
    def validate_supported_risk_factors(cls, field_value, values):
      supported_risk_vfactors = ['FX']
      if not field_value in supported_risk_vfactors:
            raise UserWarning(f"{field_value} not in {supported_risk_vfactors}")
      return field_value

class Value_at_risk(BaseModel):
    portofolio: Dict[str, List[Portofolio_asset]]
      
    def __calculate_profit_loss_vector__(self, asset, time_horizon: int=1):
        """ 
        Calculate the proft and loss vectors for a given asset given the assosiate risk type.
        """
        
        # Profit and loss vector using log shift
        if asset.risk_type == 'FX':
            #TODO apperent mismatch after 7thh decimal. aggergates to the 4th decimal. problem seems to be the exp function
            asset_shift_vector = (asset.asset_market_rates / asset.asset_market_rates.shift(periods=-time_horizon)).dropna() # due to shift the n time horizon rows are NaN at the end. These are dropped as they are redundant and a risk for further calculations.
            asset.profit_loss_vector = asset.asset_value * asset_shift_vector.apply(lambda x: exp(log(x)*sqrt(time_horizon))-1, axis=1)

        return asset        

    def __calculate_value_at_risk__(self,assets: list, time_horizon: int=1) -> pd.DataFrame:
        """ 
        Calculate the proft and loss vectors for a given asset given the assosiate risk type.
        """
        assets = [self.__calculate_profit_loss_vector__(asset=asset, time_horizon=time_horizon) for asset in assets]
        total_profit_loss = pd.concat([asset.profit_loss_vector for asset in assets]).groupby('date').sum().sort_values(ascending=True)

        return 0.4 * total_profit_loss[1] + 0.6 * total_profit_loss[2]


    def calculate_value_at_risk(self, time_horizon: int=1): #TODO ask, can FX and IR scneario's be calculated together in the asset pool. #TODO are other shift methods required?
        """
        Calculate the VaR for FX based risk assets.
        
        Parameters
        ------------
        asset_market_rates: pd.DataFrame
            the market rates for a given period of time
        """

        return {f"{portofolio_name} VaR": self.__calculate_value_at_risk__(assets=assets, time_horizon=time_horizon) for portofolio_name, assets in self.portofolio.items()}