import pandas as pd
from src.metrics import calculate_total_revenue
from src.metrics import calculate_total_units
from src.metrics import calculate_total_revenue_units


#Test of function - combine the results of the two previous functions
def test_calculate_total_revenue_units():
    # create a sample df
    df = pd.DataFrame(                                             
    {"revenue":[200, 
                300, 
                700,
                900], 
     "units":[4,
              0,
              7,
              2]}   
    )

    # call the function and unpack the returned tuple
    total_revenue, total_units = calculate_total_revenue_units(df)

    # check if the results are correct
    assert total_units == 13                                       
    assert total_revenue == 2100