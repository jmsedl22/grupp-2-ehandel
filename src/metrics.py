
import pandas as pd


# count the total number of orders
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


# combine the results of the two previous functions
def calculate_total_revenue_units(df:pd.DataFrame) -> tuple[float, int]:
    
    # Returas both results as tuple
    return calculate_total_revenue(df), calculate_total_units(df)


# group revenue by a selected column
def group_revenue(df: pd.DataFrame, group_by: str) -> pd.DataFrame: 

    # calculate total revenue for each group
    group = df.groupby(group_by, as_index= False)["revenue"].sum()   

    # sort groups by total revenue (highest to lower)   
    group = group.sort_values(by="revenue", ascending=False)                

    return group        


# return selctiv result av group_revenue
def revenue_by_city(df: pd.DataFrame) -> pd.DataFrame:
    return group_revenue(df, "city")

def revenue_top_3_cities(df: pd.DataFrame)  -> pd.DataFrame:
    return group_revenue(df, "city").head(3)

def revenue_by_category(df: pd.DataFrame)  -> pd.DataFrame:
    return group_revenue(df, "category")

def revenue_top_3_categories(df: pd.DataFrame)  -> pd.DataFrame:
    return group_revenue(df, "category").head(3)

def revenue_by_month(df:pd.DataFrame)  -> pd.DataFrame:
    group_month = group_revenue(
        df, pd.Grouper(key="date", freq="MS"))
    
    group_month = group_month[group_month["revenue"] != 0]

    # chenges soted ordning
    group_month = group_month.sort_values(by = "date")
    # chenges namns on date column
    group_month["date"] = group_month["date"].dt.strftime("%B %Y")

    return group_month


def revenue_by_weekday(df:pd.DataFrame)  -> pd.DataFrame:

    # create ny df
    group_weekday = group_revenue(
        df.assign(weekday=df["date"].dt.dayofweek), "weekday")
    
    # chenges soted ordning
    group_weekday = group_weekday.sort_values(by = "weekday")

    # change namns i column
    days = {0: "Monday",
            1: "Tuesday",
            2: "Wenedsday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday"
                }

    # chenges namns on date column
    group_weekday["weekday"] = group_weekday["weekday"].map(days)

    return group_weekday

