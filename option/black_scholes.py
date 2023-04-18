import calendar
import warnings
from scipy.stats import norm
from typing import Optional

from math import log, sqrt, exp
from datetime import date, datetime
from pydantic import BaseModel, Field, validator, root_validator, ValidationError

from constants import  (
    cDateFormat,
    cCallForwardPrice,
    cCallSpotOption,
    cPutForwardOption,
    cPutCallParityoption,
)

class black_scholes(BaseModel):
    f"""
    This allows for the calculations of forward, spot price call calculations, forward price put calls and put-call-parity calculations.
    all logic needed for black and scholes calculations as specified on https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model. 
    For a high-over explanation of the model see https://www.investopedia.com/terms/b/blackscholes.asp.

    Parameters
    ---------------
    spot_price: float
        Current market price of option.
    strike_price: float
        Also know as call option price. Right to buy shares of a company for given price.
    trade_date: datetime.date in {cDateFormat} format.
        Date the trade was executed
    expiry_date: datetime.date in {cDateFormat} format.
        Date contract comes to due. Must be > trade_date.
    time_to_maturity: float
        Ratio of the difference between trade date and expiry date vs days within the year. Must be > 0
    risk_free_intrest: float
        Theoretical return on investment that carries no risk. 0 < risk_free_intrest < 1
    risk_free_intrest_constant: float
        Log normal transformed risk_free_intrest. 0 < risk_free_intrest < 1
    forward_stock_price: float
        Delivery price of asset to be paid at a time in the future. Must be >= 0
    asset_volatility: float
        respresents the possible fluctiuation of asset value 
    convenience_yield: float
        Premium of holding said asset. 
    European_option: bool
        Implementation only handles european stock options as the model assumes that options cannot be traded prior to expiry date.
    """
    spot_price: float = Field(default=0, ge=0)
    strike_price: float = Field(default=0, ge=0)
    trade_date: date = Field()
    expiry_date: date = Field()
    time_to_maturity: Optional[float] = Field(default=None) # or price to expiration
    risk_free_intrest: float = Field(default=0.005, gt=0, le=1)
    risk_free_intrest_constant: float = Field(default = None, gt=0)
    forward_stock_price: float = Field(default=None, gt=0)
    asset_volatility: float = Field(default=0)
    convenience_yield: float = Field(default=0)
    European_option: bool = Field(default=False)

    @root_validator(pre=True)
    def validate_time_format(cls, values):
        f"""
        Dates should be in uniform {cDateFormat} format for calculations.
        """

        def helper_str_to_date(date_string):
            f"""
            convert string to cDateFormat or raise error.
            """
            if isinstance(date_string, str):
                try:
                    return datetime.strptime(date_string, cDateFormat).date()
                except ValueError:
                    raise ValueError(f"{date_string} could not be parsed towards {cDateFormat}")
        # if keys are missing give error
        if (not 'trade_date' in values.keys()) | (not 'expiry_date' in values.keys()):
            raise ValueError(f"trade and/or experiy date is missing. Please add them in the {cDateFormat} format")
        # Attempt date conversion for dates
        else:
            dates = {key: helper_str_to_date(value) for key, value in values.items() if key in ['trade_date','expiry_date']}
            values.update(dates)

        return values
    
    @root_validator
    def calculate_expiry_date(cls, values) -> float:
        """
        Calculates the ratio for experiation in time based on the amount of days in the year if no expiry is specified.       
        
        Parameters
        ----------------
        trade_date: datetime.date in {cDateFormat} format.
            Date the trade was executed
        expiry_date: datetime.date in {cDateFormat} format.
            Date contract comes to due. Must be > trade_date.
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
        risk_free_intrest: float
            Theoretical return on investment that carries no risk. 0 < risk_free_intrest < 1
        
        Returns
        ----------------
        risk_free_intrest_constant: float
        """
        if not "risk_free_intrest" in values.keys():
            raise ValueError(f"risk_free_intrest is missing. Please add a number greater than 0 and smaller than 1")
        calculated_risk_free_intrest_constant = log(1+values["risk_free_intrest"])
        if values['risk_free_intrest_constant'] is None:
            values['risk_free_intrest_constant'] = calculated_risk_free_intrest_constant
        return values
    
    @root_validator
    def calculate_forward_stock_price(cls, values) -> float: #TODO ask if in implementation using div yield is required. Currently not used in excel but is present in F equation.
        f"""
        Calculates the ratio for experiation in time based on the amount of days in the year if no expiry is specified.       
        
        Parameters
        ----------------
        trade_date: datetime.date in {cDateFormat} format.
            Date the trade was executed
        expiry_date: datetime.date in {cDateFormat} format.
            Date contract comes to due. Must be > trade_date.
        
        Returns
        ----------------
        time_to_maturity: float
        """
        calculated_forward_stock_price = values["spot_price"] * exp(values["risk_free_intrest_constant"] * values["time_to_maturity"])
        if values['forward_stock_price'] is None:
            values['forward_stock_price'] = calculated_forward_stock_price
        return values
            
    @validator('expiry_date')
    def validate_trade_and_expiry_date(cls, field_value, values):
        """
        expiry date must be larger than trade date
        """

        if not field_value >= values['trade_date']:
            raise ValueError(f"expiry date: {field_value} is smaller or equal than trade date: {values['trade_date']}. Please ensure that the trade date is larger than the expiry date.")
        return field_value

    @validator('spot_price','strike_price', 'forward_stock_price')
    def validate_stock_prices(cls, field_value):
        if field_value < 0:
            raise ValueError("Stock values cannot be lower than 0. Specified value of {field_value} must be changed.")
        return field_value

    def __calculate_spot_delta_one__(self, spot_price:float) -> float:
        """
        Calculates the first delta required for spot-price black and scholes

        Parameters
        ---------------
        spot_price: float
            Current market price of option.
        strike_price: float
            Also know as call option price. Right to buy shares of a company for given price.
        time_to_maturity: float
            Ratio of the difference between trade date and expiry date vs days within the year. Must be > 0
        risk_free_intrest_constant: float
            Log normal transformed risk_free_intrest. 0 < risk_free_intrest < 1
        forward_stock_price: float
            Delivery price of asset to be paid at a time in the future. Must be >= 0
        asset_volatility: float
            respresents the possible fluctiuation of asset value 
        convenience_yield: float
            Premium of holding said asset. 
        European_option: bool
            Implementation only handles european stock options as the model assumes that options cannot be traded prior to expiry date.
        
        Returns
        ---------------
        spot_price_delta_one: float
        """
        
        return(log(spot_price/self.strike_price)+(self.risk_free_intrest_constant+self.asset_volatility**2/2.)*self.time_to_maturity)/(self.asset_volatility*sqrt(self.time_to_maturity))
    
    def __calculate_forward_delta_one__(self, forward_price:float) -> float:
        """
        Calculate the delta one for forward pricing, difference with spot pricing is that the free_interest_rate_constant is not used.

        Parameters
        ---------------
        forward_stock_price: float
            Delivery price of asset to be paid at a time in the future. Must be >= 0
        strike_price: float
            Also know as call option price. Right to buy shares of a company for given price.
        time_to_maturity: float
            Ratio of the difference between trade date and expiry date vs days within the year. Must be > 0
        risk_free_intrest_constant: float
            Log normal transformed risk_free_intrest. 0 < risk_free_intrest < 1
        asset_volatility: float
            respresents the possible fluctiuation of asset value 

        Returns
        ---------------
        forward_price_delta_one: float

        """
        return (log(forward_price/self.strike_price)+(self.asset_volatility**2/2.*self.time_to_maturity))/(self.asset_volatility*sqrt(self.time_to_maturity))
    
    def __calculate_delta_two__(self, d1:float) -> float:
        """
        Calculates the second delta required for forward-price black and scholes

        Parameters
        ----------------
        d1: float
            First delta of forward or spot price.
        asset_volatility: float
            respresents the possible fluctiuation of asset value 
        time_to_maturity: float
            Ratio of the difference between trade date and expiry date vs days within the year. Must be > 0
        
        Returns
        ---------------
        delta_two: float
        """
        return d1 - (self.asset_volatility * sqrt(self.time_to_maturity))
    
    def __calculate_call_price__(self, price: float, d1:float, d2:float)-> float:
        """
        calculates price for call options

        Parameters
        ---------------
        price: float
            Spot or forward price.
        d1: float
            d1 for either spot or forward results
        d2: float
            generic d2 based on black and scholes.
        strike_price: float
            Also know as call option price. Right to buy shares of a company for given price.
        time_to_maturity: float
            Ratio of the difference between trade date and expiry date vs days within the year. Must be > 0
        risk_free_intrest_constant: float
            Log normal transformed risk_free_intrest. 0 < risk_free_intrest < 1

        Returns
        ---------------
        call price: float
            calculated price for either spot or forward pricing.
        """
        return exp(-self.risk_free_intrest_constant*self.time_to_maturity) * (price*norm.cdf(d1)-self.strike_price*norm.cdf(d2))

    def __calculate_put_price__(self, price: float, d1:float, d2:float) -> float:
        """
        calculates price for put options

        Parameters
        ---------------
        price: float
            Spot or forward price.
        d1: float
            d1 for either spot or forward results
        d2: float
            generic d2 based on black and scholes.
        strike_price: float
            Also know as call option price. Right to buy shares of a company for given price.
        time_to_maturity: float
            Ratio of the difference between trade date and expiry date vs days within the year. Must be > 0
        risk_free_intrest_constant: float
            Log normal transformed risk_free_intrest. 0 < risk_free_intrest < 1

        Returns
        ---------------
        put price: float
            calculated price for either spot or forward pricing.        
        """

        return exp(-self.risk_free_intrest_constant * self.time_to_maturity) * (self.strike_price*norm.cdf(-d2)-price*norm.cdf(-d1))
    
    def __calculate_put_call_parity__(self, forward_price:float)-> float:
        """
        calculates put-call parity using fowrad call and put calculations.

        Parameters
        ---------------
        forward_price: float
            forward price as calculated by black and scholes definition. 
        strike_price: float
            Also know as call option price. Right to buy shares of a company for given price.
        time_to_maturity: float
            Ratio of the difference between trade date and expiry date vs days within the year. Must be > 0
        risk_free_intrest_constant: float
            Log normal transformed risk_free_intrest. 0 < risk_free_intrest < 1

        Returns
        ---------------
        put_call_parity: float
            calculated put_call_parity for forward put and call.        
        """
          
        return forward_price - self.spot_price+self.strike_price*exp(-self.time_to_maturity*self.risk_free_intrest_constant)

    def calculate_option_premium(self) -> dict:
        f"""
        Calculate forward, spot price call, forward price put, forward price calls and forward price put-call-parity calculations.
        all logic needed for black and scholes calculations as specified on https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model. 

        Returns
        ---------------
        black and schole results: dict   
            {cCallSpotOption}: call_spot_price: float,
            {cCallForwardPrice} : call_forward_price: float,
            {cPutForwardOption}: put_price: float,
            {cPutCallParityoption}: put_call_parity: float
        """
        
        if not self.European_option:
            return UserWarning(f"Calculation only works for european stock options")
        
        #calculate base d1 and d2 parameters for forward and spot prices
        d1_spot = self.__calculate_spot_delta_one__(self.spot_price)
        d1_forward = self.__calculate_forward_delta_one__(self.forward_stock_price)

        d2_spot = self.__calculate_delta_two__(d1_spot)
        d2_forward = self.__calculate_delta_two__(d1_forward)

        #TODO ask if spot forward price should always be given, equation use din excel uses forward_stoch_price for both spot and forward call price. Looks like
        # mismatch with equations.
        call_spot_price = self.__calculate_call_price__(price=self.forward_stock_price, d1 = d1_spot, d2 = d2_spot)
        call_forward_price = self.__calculate_call_price__(price=self.forward_stock_price, d1 = d1_forward, d2 = d2_forward)

        #Calculate put parameters
        put_price = self.__calculate_put_price__(price=self.forward_stock_price, d1 = d1_forward, d2 = d2_forward)
        put_call_parity = self.__calculate_put_call_parity__(call_forward_price)

        return {
            cCallSpotOption: call_spot_price,
            cCallForwardPrice : call_forward_price,
            cPutForwardOption: put_price,
            cPutCallParityoption: put_call_parity,
        }