
import pandas as pd


# Count the total number of orders
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
