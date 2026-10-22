
import pandas as pd
from src.metrics import count_orders


# test 
def test_count_ordes():
     #create a sample df with orders ids
    df =pd.DataFrame({"order_id":[101,102,103,103]})       
    result = count_orders(df)
    
    #check if the result is correct
    assert result ==3                                     
