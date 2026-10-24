
import pandas as pd


# Count the total number of orders
def count_orders(df: pd.DataFrame) -> int:
    # nuninque - to avoid counting duplicates
    count_orders = df["order_id"].nunique()      
    
    # return the total number of orders
    return count_orders  


# Calculate total revenue 
def calculate_total_revenue(df:pd.DataFrame) -> float:
    # Sum all values in the column "revenue"
    total_revenue = sum(df["revenue"])

    # Returas total revenue as a float
    return float(total_revenue)


# Calculate total number of units sold
def calculate_total_units(df:pd.DataFrame) -> int:
    # Sum all values in the column "units"   
    total_units = sum(df["units"])       

    # Returas calculeted total units
    return (total_units)


# Combine the results of the two previous functions
def calculate_total_revenue_units(df:pd.DataFrame) -> tuple[float, int]:
    
    # Returas both results as tuple
    return calculate_total_revenue(df), calculate_total_units(df)


# Group revenue by a selected column
def group_revenue(df: pd.DataFrame, group_by: str) -> pd.DataFrame: 

    # calculate total revenue for each group
    group = df.groupby(group_by, as_index= False)["revenue"].sum()   

    # sort groups by total revenue (highest to lower)   
    group = group.sort_values(by="revenue", ascending=False)                

    return group        


# 
def calculate_order_value_distribution(df: pd.DataFrame) -> dict[str:float] :
    orders_total_revenues = group_revenue(df, "order_id")
    min_revenue = orders_total_revenues["revenue"].min()
    max_revenue = orders_total_revenues["revenue"].max()
    median_revenue = orders_total_revenues["revenue"].median()


    return {
        "min_revenue": min_revenue,
        "max_revenue" : max_revenue,
        "median_revenue" : median_revenue
    }
