
import pandas as pd


# count the total number of orders
def count_orders(df: pd.DataFrame) -> int:
    # nuninque - to avoid counting duplicates
    count_orders = df["order_id"].nunique()      
    
    # return the total number of orders
    return count_orders                           