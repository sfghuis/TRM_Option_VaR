import pandas as pd
from value_at_risk import Value_at_risk

test_data = pd.read_csv(r"value_at_risk\cyy_market_rates.csv", parse_dates=['date'], sep=";", infer_datetime_format="%d-%m-%Y", thousands='.')

test_asset_ccy1 = {"asset_name":"ccy-1","risk_type": "FX","asset_value":  153084.81, "asset_market_rates":test_data[test_data.asset == 'ccy-1']}
test_asset_ccy2 = {"asset_name":"ccy-2","risk_type": "FX", "asset_value":  95891.51, "asset_market_rates":test_data[test_data.asset == 'ccy-2']}

def test_default_fx_VaR():
    """ 
    Test VaR as defined in intial excel.
    """
    assert round(Value_at_risk(portofolio = {"SPOT Portfolio value": [test_asset_ccy1, test_asset_ccy2]}).calculate_value_at_risk()["SPOT Portfolio value VaR"], 3) == -13572.734

test_asset_ccy1 = {"asset_name":"ccy-1","risk_type": "FX","asset_value":  253084.81, "asset_market_rates":test_data[test_data.asset == 'ccy-1']}
test_asset_ccy2 = {"asset_name":"ccy-2","risk_type": "FX", "asset_value":  5891.51, "asset_market_rates":test_data[test_data.asset == 'ccy-2']}

def test_random_fx_VaR():
    """ 
    Test VaR as defined in intial excel.
    """
    assert round(Value_at_risk(portofolio = {"SPOT Portfolio value": [test_asset_ccy1, test_asset_ccy2]}).calculate_value_at_risk()["SPOT Portfolio value VaR"], 3) ==  -22416.742 

test_asset_ccy1 = {"asset_name":"ccy-1","risk_type": "FX","asset_value":  0, "asset_market_rates":test_data[test_data.asset == 'ccy-1']}
test_asset_ccy2 = {"asset_name":"ccy-2","risk_type": "FX", "asset_value":  5891.51, "asset_market_rates":test_data[test_data.asset == 'ccy-2']}

def test_zero_value_fx_VaR():
    """ 
    Test VaR as defined in intial excel.
    """
    assert round(Value_at_risk(portofolio = {"SPOT Portfolio value": [test_asset_ccy1, test_asset_ccy2]}).calculate_value_at_risk()["SPOT Portfolio value VaR"], 3) ==  -46.258 

test_asset_ccy1 = {"asset_name":"ccy-1","risk_type": "FX","asset_value":  0, "asset_market_rates":test_data[test_data.asset == 'ccy-1']}
test_asset_ccy2 = {"asset_name":"ccy-2","risk_type": "FX", "asset_value":  0, "asset_market_rates":test_data[test_data.asset == 'ccy-2']}

def test_all_zero_value_fx_VaR():
    """ 
    Test VaR as defined in intial excel.
    """
    assert round(Value_at_risk(portofolio = {"SPOT Portfolio value": [test_asset_ccy1, test_asset_ccy2]}).calculate_value_at_risk()["SPOT Portfolio value VaR"], 3) ==  0