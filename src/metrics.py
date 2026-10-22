
import pandas as pd


# group revenue by a selected column
def group_revenue(df: pd.DataFrame, group_by: str) -> pd.DataFrame: 

    # calculate total revenue for each group
    group = df.groupby(group_by, as_index= False)["revenue"].sum()   

    # sort groups by total revenue (highest to lower)   
    group = group.sort_values(by="revenue", ascending=False)                

    return group        
