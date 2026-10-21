import pandas as pd
from src.metrics import calculate_total_revenue_units

#Test total revenue and units calculation

def test_calculate_total_revenue_units():


    df = pd.DataFrame(                                             # create a sample df
    {"revenue":[200, 300, 700, 900], 
     "units":[4,0,7,2]}   
    )

    total_revenue, total_units = calculate_total_revenue_units(df)

    assert total_units == 13                                       # chech if the results are correct
    assert total_revenue == 2100