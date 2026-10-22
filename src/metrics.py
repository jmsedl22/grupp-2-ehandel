
import pandas as pd


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


# combine the results of the two previous functions
def calculate_total_revenue_units(df:pd.DataFrame) -> tuple[float, int]:
    
    # Returas both results as tuple
    return calculate_total_revenue(df), calculate_total_units(df)


