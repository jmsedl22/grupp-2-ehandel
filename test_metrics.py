
import pandas as pd

from src.metrics import calculate_aov


 # test AOV calculation 
def test_calculate_aov():
    #create sample order data
    df = pd.DataFrame({
        "order_id":[101,
                    102,
                    103,
                    103],
        "revenue":[200,
                   300,
                   400,
                   100]}
    )
    result = calculate_aov(df)
    # chech if the results are correct
    assert result == 1000/3                                        


# test AOV when zero orders
def test_calculate_aov_zero():
    #create sample order data
    df = pd.DataFrame({
        "order_id":[],
        "revenue":[]}
    )
    result = calculate_aov(df)
    # chech if the results are correct
    assert result == 0,0          
                                     