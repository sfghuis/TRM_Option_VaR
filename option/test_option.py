from pytest import fixture, raises
from black_scholes import black_scholes

def test_add():
    assert 1+1 == 2

@fixture()
def default_scholes_class():
    return black_scholes(
                    spot_price= 19,
                    strike_price= 17,
                    trade_date= "23-11-2022",
                    expiry_date= "10-05-2023",
                    risk_free_intrest= 0.005,
                    asset_volatility= 0.3,
                    convenience_yield= 0,
                    european_option=True
                )

### test time to maturity calculations
def test_time_to_maturity_regular_year(default_scholes_class):
    """
    Test if the calculation of date to matuirity checks out for normal year.
    """

    assert round(default_scholes_class.time_to_maturity, 3) == 0.460

def test_time_to_maturity_leap_year():
    """
    Test if the calculation of date to matuirity checks out for normal leap year
    """

    test_scholes_leap_year = black_scholes(
                        spot_price= 19,
                        strike_price= 17,
                        trade_date= "23-11-2023",
                        expiry_date= "10-05-2024",
                        risk_free_intrest= 0.5,
                        asset_volatility= 0.3,
                        convenience_yield= 0,
                        european_option=True
                    )   

    assert round(test_scholes_leap_year.time_to_maturity, 3) == 0.463

### test spot price calculations

spot_price=19
forward_price = 19.04367

def test_spot_price_d1(default_scholes_class):
    """
    Test if the d1 value of the spot price black Scholes formula matches with value from original excel file. Accuracy set based on excel data
    """

    assert round(default_scholes_class.__calculate_spot_delta_one__(spot_price), 5) == 0.65953

def test_forward_price_d1(default_scholes_class):
    """
    Test if the d1 value of the spot price black Scholes formula matches with value from original excel file. Accuracy set based on excel data
    """

    assert round(default_scholes_class.__calculate_forward_delta_one__(forward_price), 5) == 0.65953

def test_price_d2(default_scholes_class):
    """
    Test if the d1 value of the spot price black Scholes formula matches with value from original excel file. Accuracy set based on excel data
    """

    assert round(default_scholes_class.__calculate_delta_two__(d1 = default_scholes_class.__calculate_spot_delta_one__(spot_price)), 5) == 0.45600
    assert round(default_scholes_class.__calculate_delta_two__(d1 = default_scholes_class.__calculate_forward_delta_one__(forward_price)), 5) == 0.45600

def test_default_scholes_outcomes(default_scholes_class):
    """
    test default outputs and if they match with the beheviour found within the demo excel.
    """

    outcomes = default_scholes_class.calculate_option_premium()

    assert round(outcomes['Call Spot price'], 5) == 2.69688
    assert round(outcomes['Call Forward price'], 5) == 2.69688
    assert round(outcomes['Put forward price'], 5) == 0.65790
    assert round(outcomes['Put-call parity'], 5) == 0.65790

### test extremes

def test_missing_date_input():
    """
    Test extremely low inputs and missing dates
    """
    with raises(Exception):
        black_scholes(
                    trade_date= "",
                    expiry_date= "",
                    risk_free_intrest= 0.5,
                    asset_volatility= 0.3,
                    convenience_yield= 0,
                    european_option=True
                )   

def test_zero_input():
    """
    Test extremely low inputs
    """
    with raises(Exception):
        black_scholes(
                    spot_price= -10,
                    strike_price= 0,
                    trade_date= "23-11-2023",
                    expiry_date= "10-05-2024",
                    risk_free_intrest= 0.0,
                    asset_volatility= 0.0,
                    convenience_yield= 0,
                    european_option=True
                ) 
        
    with raises(Exception):
        black_scholes(
                    spot_price= 0,
                    strike_price= -17,
                    trade_date= "23-11-2022",
                    expiry_date= "10-05-2023",
                    risk_free_intrest= 0.005,
                    asset_volatility= 0.3,
                    convenience_yield= 0,
                    european_option=True
                )
    with raises(Exception):
        black_scholes(
                    spot_price= 19,
                    strike_price= 0,
                    trade_date= "23-11-2022",
                    expiry_date= "10-05-2023",
                    risk_free_intrest= 0.005,
                    asset_volatility= 0.3,
                    convenience_yield= 0,
                    european_option=True
                )
    with raises(Exception):
        black_scholes(
                    spot_price= 19,
                    strike_price= 17,
                    trade_date= "23-11-2022",
                    expiry_date= "10-05-2023",
                    risk_free_intrest= 0,
                    asset_volatility= 0,
                    convenience_yield= 0,
                    european_option=True
                )

def test_non_european_option():
    with raises(Exception):
        black_scholes(
                    spot_price= 19,
                    strike_price= 17,
                    trade_date= "23-11-2022",
                    expiry_date= "10-05-2023",
                    risk_free_intrest= 0.005,
                    asset_volatility= 0.3,
                    convenience_yield= 0,
                    european_option=False
                ).calculate_option_premium()