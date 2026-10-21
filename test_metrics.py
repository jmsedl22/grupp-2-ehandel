
import pandas as pd
from src.metrics import count_orders

# test
def test_count_ordes():
    df =pd.DataFrame({"order_id":[101,102,103,103]})       #create a sample df with orders ids
    result = count_orders(df)

    assert result ==4                                      #check if the result is correct
