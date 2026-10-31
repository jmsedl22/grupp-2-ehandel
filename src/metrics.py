
import pandas as pd
import numpy as np


# Calculate the average order value (AOV)
def calculate_aov(df: pd.DataFrame)  -> float:
    # Calculate total revenue and number of unique orders
    total_revenue = calculate_total_revenue(df)
    total_orders = count_orders(df)
    
    # Avoid division by zero
    if total_orders == 0:                              
        return 0.0

    # Calculate AOV
    aov = total_revenue / total_orders 

    # Return the average revenue per order
    return float(aov)

# Count unique orders
def count_orders(df: pd.DataFrame) -> int:
    # Count district order IDs
    count_orders = df["order_id"].nunique()      
    
    # Return the number of  unique orders
    return int(count_orders)  


# Calculate total revenue 
def calculate_total_revenue(df: pd.DataFrame) -> float:
    # Sum revenues values
    total_revenue = sum(df["revenue"])

    # Return total revenue as a float
    return float(total_revenue)

# Calculate total number of units sold
def calculate_total_units(df: pd.DataFrame) -> int:
    # Check for missing values
    if df["units"].isna().any():
        raise ValueError("Units cannot contain missing value") 

    # Covert units to numeric values
    try: 
        units = pd.to_numeric(df["units"], errors="raise")

    except (ValueError, TypeError) as exc:
        raise ValueError("Units must contain numeric values") from exc

    # Check for non-finity and fractional values
    if not np.isfinite(units).all():
        raise ValueError("Units must cotain finite values")
    if not (units % 1 == 0).all():
        raise ValueError ("Units must cotain whole number")           

    total_units = int(units.sum())
    # Return the total number of units sold
    return int(total_units)


# Combine the results of the two previous functions
def calculate_total_revenue_units(df: pd.DataFrame) -> tuple[float, int]:
    
    # Return both results as a tuple
    return calculate_total_revenue(df), calculate_total_units(df)


# Group revenue by a selected column
def group_revenue(df: pd.DataFrame, group_by: str | pd.Grouper ) -> pd.DataFrame: 

    # Calculate total revenue for each group
    group = df.groupby(group_by, as_index= False)["revenue"].sum()   

    # Sort groups by total revenue in descending order   
    group = group.sort_values(by="revenue", ascending=False)                

    return group        


# Return total revenue grouping by city
def revenue_by_city(df: pd.DataFrame) -> pd.DataFrame:
    return group_revenue(df, "city")


# Return the three cities with highest revenue
def revenue_top_3_cities(df: pd.DataFrame)  -> pd.DataFrame:
    return group_revenue(df, "city").head(3)


# Return total revenue grouping by category
def revenue_by_category(df: pd.DataFrame)  -> pd.DataFrame:
    return group_revenue(df, "category")


# Return the three categories with highest revenue
def revenue_top_3_categories(df: pd.DataFrame)  -> pd.DataFrame:
    return group_revenue(df, "category").head(3)


# Group revenue by month
def revenue_by_month(df: pd.DataFrame)  -> pd.DataFrame:
    # Group revenue by month using the date column
    group_month = group_revenue(
        df, pd.Grouper(key="date", freq="MS"))
    
    # Sort month in chronological order
    group_month = group_month.sort_values(by="date")

    # Format dates as month and years
    group_month["date"] = group_month["date"].dt.strftime("%B %Y")

    return group_month


# Group revenue by weekday 
def revenue_by_weekday(df: pd.DataFrame)  -> pd.DataFrame:

    # Create a DataFrame grouped by weekday
    group_weekday = group_revenue(
        df.assign(weekday=df["date"].dt.dayofweek), "weekday")
    
    # Sort weekdays in chronological order
    group_weekday = group_weekday.sort_values(by="weekday")

    # Map weekday numbers to weekday names
    days = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    # Replace weekday numbers with weekday names
    group_weekday["weekday"] = group_weekday["weekday"].map(days)

    return group_weekday


# Calculate minumum, maximum and median order reveneu
def calculate_order_value_distribution(df: pd.DataFrame) -> dict[str, float]:
    # Calculate total revenue for each order
    orders_total_revenues = group_revenue(df, "order_id")

    # Find the minimum order revenue
    min_revenue = orders_total_revenues["revenue"].min()
    # Find the maximum order revenue
    max_revenue = orders_total_revenues["revenue"].max()
    # Calculate the median order revenue
    median_revenue = orders_total_revenues["revenue"].median()

    # return the calculate revenue statistics
    return {
        "min_revenue": float(min_revenue),
        "max_revenue" : float(max_revenue),
        "median_revenue" : float(median_revenue),
    }


# Calculate revenue ranges for order distribution
def calculate_order_ranges(df: pd.DataFrame) -> pd.DataFrame:
    from_to = _calculate_order_boundaries(df)

    # Calculate total revenue for each order
    orders = group_revenue(df, "order_id")

    # Handle orders with identical revenue values
    if len(from_to) == 1:
        return pd.DataFrame(
            {
                "number of orders": [len(orders)],
                "percentages": [100.0],
            },
            index=["group1"],
        )

    labels = [f"{from_to[i]: .2f} - {from_to[i+1]:.2f}"
              for i in range (len(from_to) - 1)
    ]
    # Divide orders into revenue groups based on the defined boudaries
    orders["revenue_group"] = pd.cut(
        orders["revenue"],
        bins=from_to,
        labels=labels,
        include_lowest=True,
    )

    counts = orders["revenue_group"].value_counts().sort_index()
    # Calculate the percantage of orders in each group
    count_procent = counts / len(orders)*100

    # Create a Data Frame with order counts and percentages
    result = pd.DataFrame(
        {
            "number of orders": counts,
            "percentages" :count_procent
        }
    )

    return result

# Calculate standard deviation of order values
def calculate_order_value_std(df: pd.DataFrame) -> float:
    # Calculate total revenue for each order
    order = group_revenue(df, "order_id")

    # Calculate standart deviation
    std = order["revenue"].std()

    return float(std)


def get_order_range_boundaries(df:pd.DataFrame) -> list[float]:
    # return revenue range boundaries for plotting
    return _calculate_order_boundaries(df)


# Calculate variance of order values
def calculate_order_value_variance(df: pd.DataFrame) -> float:
    # Calculate total revenue for each order
    orders = group_revenue(df, "order_id") 
    variance = orders["revenue"].var()

    return float(variance)


# Calculate and returns order revenue boundaries
def _calculate_order_boundaries(df: pd.DataFrame) -> list[float]:
    # Get order revenue statistics
    stats = calculate_order_value_distribution(df)

    # Extract minimum, maximum and median revenue
    min_revenue = stats["min_revenue"]
    max_revenue = stats["max_revenue"]
    median_revenue = stats["median_revenue"]

    if min_revenue == max_revenue:
        return [float(min_revenue)]
    
    # Find the smaller distance between the median and the revenues limits
    distance = min(
        median_revenue - min_revenue,
        max_revenue - median_revenue
    )
    # Calculate a margin of 20 percent around the median
    margin = distance * 0.2

    # Calculate the lower and upper boundaries around the median
    middle_lower = median_revenue - margin
    middle_upper = median_revenue + margin
    # Calculate the midpoints of the lower and upper revenue ranges
    lower_split = (min_revenue + middle_lower) / 2
    upper_split = (middle_upper + max_revenue) / 2

    # Define boundaries for the revenue ranges
    boundaries = [
        min_revenue,
        lower_split,
        middle_lower,
        middle_upper,
        upper_split,
        max_revenue,
    ]

    return sorted({float(value) for value in boundaries})


# Calculate mode, quartiles and IRQ of order values
def calulate_descriptive_statistics(df:pd.DataFrame) -> dict: 
    orders = group_revenue(df, "order_id")
    values = orders["revenue"]
    
    if values.empty:
        return {}
    
    mode = values.mode().tolist()
    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1
    
    return {
        "mode": mode,
        "q1": q1,
        "q3": q3,
        "iqr": iqr
    }


# Detect outliners in order values using the IQR methot
def detect_outliers(df: pd.DataFrame) -> pd.DataFrame:
    
    orders = group_revenue(df, "order_id")
    stats = calulate_descriptive_statistics(df)
        
    if not stats:
        return orders

    # Get quartiles and IQR from the stasistics dictionary    
    q1 = stats["q1"]
    q3 = stats["q3"]
    iqr = stats["iqr"]

    # Calculate lower and upper outlier boundalies
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Select orders outside the boundaries   
    outliers = orders[
        (orders["revenue"] < lower_bound) | (orders["revenue"] > upper_bound)
    ]

    return outliers

def calculate_order_z_scores(df: pd.DataFrame) -> pd.DataFrame:
    orders = group_revenue(df, "order_id")

    # Get order revenue values
    values = orders["revenue"]

    if values.empty:
        orders["z_score"] = pd.Serie(dtypy=float)
        return orders
        
    
    mean = calculate_aov(df)
    std = calculate_order_value_std(df)

    # Handle zero standard deviation
    if pd.isna(std) or std == 0:
        orders["z_score"] = 0.0
        return orders

    # Calculate z-score for each order
    orders["z_score"] = (values - mean) / std

    return orders


# Calculate the linear between units sold and revenue
def calculate_units_revenue_correlation(df: pd.DatFrame) -> float:
    correlation = df["units"].corr(df["revenue"])

    return float(correlation)