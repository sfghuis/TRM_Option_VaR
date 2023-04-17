import calendar
import warnings
from scipy.stats import norm
from typing import Optional

from math import log, sqrt, exp
from datetime import date, datetime
from pydantic import BaseModel, Field, validator, root_validator

from constants import  cDateFormat, cSpotPrice, cCallOption

class black_scholes(BaseModel):
    """
    This class contains all logic needed for black and scholes calculations as specified on https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model. 
    Implementation inspired on https://www.codearmo.com/python-tutorial/options-trading-black-scholes-model.

    #TODO add risk scale from 0 to 1
    """
    spot_price: float = Field(default=0)
    strike_price: float = Field(default=0)
    trade_date: date = Field(default = date(year=1990, month=1, day=1))
    expiry_date: date = Field(default = date(year=1990, month=1, day=2))
    time_to_maturity: Optional[float] = Field(default=None) # or price to expiration
    risk_free_intrest: float = Field(default=0.005, gt=0)
    risk_free_intrest_constant: float = Field(default = None, gt=0)
    forward_stock_price: float = Field(default=None, gt=0)
    asset_volatility: float = Field(default=0)
    convenience_yield: float = Field(default=0)

    @root_validator
    def calculate_experiy_date(cls, values) -> float:
        """
        Calculates the ratio for experiation in time based on the amount of days in the year if no expiry is specified.       
        
        Parameters
        ----------------
        
        Returns
        ----------------
        time_to_maturity: float
        """
        calculated_time_to_maturity =  (values['expiry_date'] - values['trade_date']).days / (365 + calendar.isleap(datetime.now().year)) #account for leap year when calculating the expiry ratio.
        if values['time_to_maturity'] is None:
            values['time_to_maturity'] = calculated_time_to_maturity
        else:
            #Check if provided value matches with given values
            if values['time_to_maturity'] != calculated_time_to_maturity:
                warnings.warn(UserWarning(f"time_to_maturity: {values['time_to_maturity']} does not match calculated time_to_maturity: {calculated_time_to_maturity}, please check if this is desired."))
        return values
    
    @root_validator
    def calculate_risk_free_intrest_constant(cls, values) -> float:
        """
        Created the risk free intrest constant by taking the natural log 1 + risk free intrest rate.     
        
        Parameters
        ----------------
        #TODO
        
        Returns
        ----------------
        time_to_maturity: float
        """
        calculated_risk_free_intrest_constant = log(1+values["risk_free_intrest"])
        if values['risk_free_intrest_constant'] is None:
            values['risk_free_intrest_constant'] = calculated_risk_free_intrest_constant
        return values
    
    @root_validator
    def calculate_forward_stock_price(cls, values) -> float:
        """
        Calculates the ratio for experiation in time based on the amount of days in the year if no expiry is specified.       
        
        Parameters
        ----------------
        trade_date: date
            Date the asset was traded
        expiry_date: date
            date the asset expires, must always be larger than the trade date.
        
        Returns
        ----------------
        time_to_maturity: float
        """
        calculated_forward_stock_price = values["spot_price"] * exp(values["risk_free_intrest_constant"] * values["time_to_maturity"])
        if values['forward_stock_price'] is None:
            values['forward_stock_price'] = calculated_forward_stock_price
        return values


    @validator('trade_date',  'expiry_date', pre=True)
    def validate_time_format(cls, date_value):
        """
        Dates should be in uniform format for processing.
        """
        if isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, cDateFormat)
            except ValueError:
                raise ValueError(f"{date_value} could not be parsed towards YYYY-MM-DD")
        return date_value
            
    @validator('expiry_date')
    def validate_trade_and_expiry_date(cls, field_value, values):
        """
        expiry date must be larger than trade date
        """

        if not field_value > values['trade_date']:
            raise ValueError(f"expiry date: {values['expiry_date']} is smaller or equal than trade date: {values['trade_date']}. Please ensure that the trade date is larger than the expiry date.")
        else:
            return field_value


    def __calculate_spot_delta_one__(self, price:float) -> float:
        """
        Calculates the first delta required for forward-price black and scholes

        Parameters
        ----------------
        price: #TODO
        """
        
        return(log(price/self.strike_price)+(self.risk_free_intrest_constant+self.asset_volatility**2/2.)*self.time_to_maturity)/(self.asset_volatility*sqrt(self.time_to_maturity))
    
    def __calculate_forward_delta_one__(self, price:float):
        
    
    def __calculate_delta_two__(self, d1:float, price:float) -> float:
        """
        Calculates the second delta required for forward-price black and scholes

        Parameters
        ----------------
        spot_price: float
            Spot price of given asset

        """
        return d1 - (self.asset_volatility * sqrt(self.time_to_maturity))
    
    def __calculate_call_price__(self, price: float, spot_price: bool=True)-> float:
        """
        
        """
        if cSpotPrice:
            d1 = self.__calculate_spot_delta_one__(price)

        return price*norm.cdf(d1)-self.strike_price*exp(-self.risk_free_intrest_constant*self.time_to_maturity)*norm.cdf(self.__calculate_delta_two__(d1, price))

    
    def calculate_option_premium(self, spot_price: bool=True, option:str=cCallOption) -> float:
        """
        
        """

        # Deterime the price type to use for calculations

        if spot_price:
            price = self.spot_price
        else:
            price = self.forward_stock_price

        if option == cCallOption:
           return self.__calculate_call_price__(price=price, spot_price)

    

print(black_scholes(
    spot_price= 19,
    strike_price= 17,
    trade_date= "23-11-2022",
    expiry_date= "10-05-2023",
    risk_free_intrest= 0.005,
    asset_volatility= 0.3,
    convenience_yield= 0,
    ).calculate_option_premium(option='Call'))