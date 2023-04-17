from pytest import fixture
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
                        trade_date= "23-11-2023",
                        expiry_date= "10-05-2024",
                        risk_free_intrest= 0.5,
                        asset_volatility= 0.3,
                        convenience_yield= 0,
                    )   

    assert round(test_scholes_leap_year.time_to_maturity, 3) == 0.463

### test spot price calculations

def test_spot_price_d1(default_scholes_class):
    """
    Test if the d1 value of the spot price black Scholes formula matches with value from original excel file. Accuracy set based on excel data
    """

    assert round(default_scholes_class.__calculate_forward_delta_one__(price=19), 5) == 0.65953

def test_spot_price_d2(default_scholes_class):
    """
    Test if the d1 value of the spot price black Scholes formula matches with value from original excel file. Accuracy set based on excel data
    """

    assert round(default_scholes_class.__calculate_forward_delta_two__(price=19), 5) == 0.45600

def test_spot_premium_call(default_scholes_class):
    """
    Test the to expected beheviour for spot price using call
    """

    assert round(default_scholes_class.calculate_option_premium(price_type='Spot price', option='Call'), 5) == 2.69688

def test_Forward_premium_call(default_scholes_class):
    """
    Test the to expected beheviour for spot price using call
    """

    assert round(default_scholes_class.calculate_option_premium(price_type='Forward', option='Call'), 5) == 2.69688
