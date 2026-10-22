
import pandas as pd


# calculate the average order value (AOV)
def calculate_aov(df: pd.DataFrame)  -> float:
    # use results from functions calculate_total_revenue(df) and count_orders
    total_revenue = calculate_total_revenue(df)
    total_orders = count_orders(df)
    
    # avoid division by zero
    if total_orders == 0:                              
        return 0.0

    # calculate AOV
    aov = total_revenue/total_orders 

    return aov

