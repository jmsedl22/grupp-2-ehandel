import numpy as np
import pandas as pd
from pandas import DataFrame


def calculate_aov(df: DataFrame) -> float:
    """
    Calculates the average order value.
    """
    orders = order_totals(df)
    number_of_orders = len(orders)

    if number_of_orders <= 0:
        return 0.0

    total_revenue = calculate_total_revenue(orders)
    aov = total_revenue / number_of_orders

    return float(aov)


# Count unique orders
def count_orders(df: DataFrame) -> int:
    # Count district order IDs
    count_orders = df["order_id"].nunique()

    # Return the number of  unique orders
    return int(count_orders)


# Calculate total revenue
def calculate_total_revenue(df: DataFrame) -> float:
    # Sum revenues values
    total_revenue = sum(df["revenue"])

    # Return total revenue as a float
    return float(total_revenue)

# Calculate total number of units sold
def calculate_total_units(df: DataFrame) -> int:
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
def calculate_total_revenue_units(df: DataFrame) -> tuple[float, int]:

    # Return both results as a tuple
    return calculate_total_revenue(df), calculate_total_units(df)


# Group revenue by a selected column
def group_revenue(df: DataFrame, group_by: str | pd.Grouper ) -> DataFrame:

    # Calculate total revenue for each group
    group = df.groupby(group_by, as_index= False)[["revenue"]].sum()

    # Sort groups by total revenue in descending order
    group = group.sort_values(by="revenue", ascending=False)

    return group


def _group_revenue_summary(df: DataFrame, group_by: str) -> DataFrame:
    """
    Return grouped revenue and percentage shares of total input revenue. Empty
    input returns the same three columns. Zero total gives NaN shares. Raise
    ValueError for missing required columns or invalid revenue.
    """
    required_cols = {group_by, 'revenue'}
    missing_cols = required_cols - set(df.columns)

    if missing_cols:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing_cols))}")

    df_required = df[[group_by, "revenue"]].copy()

    try:
        revenue = pd.to_numeric(df_required["revenue"], errors="raise")
    except (ValueError, TypeError) as exc:
        raise ValueError("Revenue must contain numeric values") from exc

    if revenue.isna().to_numpy().any():
        raise ValueError("Revenue cannot contain missing values")

    if not np.isfinite(revenue.to_numpy(dtype=float)).all():
        raise ValueError("Revenue must contain finite values")

    df_required["revenue"] = revenue
    total_revenue = revenue.sum()

    groups = df_required.groupby(
        group_by,
        as_index=False,
        dropna=False,
        observed=True,
    )[["revenue"]].sum()

    if total_revenue == 0:
        groups["share_pct"] = float("nan")
    else:
        groups["share_pct"] = groups["revenue"] / total_revenue * 100

    groups = groups.sort_values(
        by=["revenue", group_by],
        ascending=[False, True],
        na_position="last",
    )

    return groups[[group_by, "revenue", "share_pct"]]


def category_summary(df: DataFrame) -> DataFrame:
    """Return category revenue totals and percentage shares of all revenue."""
    return _group_revenue_summary(df, "category")


def order_totals(df: DataFrame) -> DataFrame:
    """
    Return order_id and summed, unrounded revenue, sorted by revenue descending.
    Raise ValueError for missing required columns, missing order IDs,
    or non-numeric, missing, or infinite revenue. Negative revenue is allowed.
    """
    required_cols = {"order_id", "revenue"}
    missing_cols = required_cols - set(df.columns)

    if missing_cols:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing_cols))}")

    df_required = df[["order_id", "revenue"]].copy()

    if df_required[["order_id"]].isna().to_numpy().any():
        raise ValueError("Order IDs cannot contain missing values")

    try:
        revenue = pd.to_numeric(df_required["revenue"], errors="raise")
    except (ValueError, TypeError) as exc:
        raise ValueError("Revenue must contain numeric values") from exc

    if revenue.isna().to_numpy().any():
        raise ValueError("Revenue cannot contain missing values")

    if not np.isfinite(revenue.to_numpy(dtype=float)).all():
        raise ValueError("Revenue must contain finite values")

    df_required["revenue"] = revenue

    if df_required.empty:
        return df_required

    orders = group_revenue(df_required, 'order_id')
    return orders[['order_id', 'revenue']]


def order_summary(df: DataFrame) -> dict[str, float]:
    """
    Return statistics for combined order revenues using linear quantile interpolation. Invalid input raises ValueError. Empty input with required columns still returns all seven keys.
    """
    aov = calculate_aov(df)
    distribution = calculate_order_value_distribution(df)
    stats = calculate_descriptive_statistics(df)

    return {
        "aov": aov,
        "median_revenue": distribution["median_revenue"],
        "min_revenue": distribution["min_revenue"],
        "max_revenue": distribution["max_revenue"],
        "q1": stats.get("q1", float("nan")),
        "q3": stats.get("q3", float("nan")),
        "iqr": stats.get("iqr", float("nan")),
    }


# Return total revenue grouping by city
def revenue_by_city(df: DataFrame) -> DataFrame:
    return group_revenue(df, "city")


# Return the three cities with highest revenue
def revenue_top_3_cities(df: DataFrame)  -> DataFrame:
    return group_revenue(df, "city").head(3)


# Return total revenue grouping by category
def revenue_by_category(df: DataFrame)  -> DataFrame:
    return group_revenue(df, "category")


# Return the three categories with highest revenue
def revenue_top_3_categories(df: DataFrame)  -> DataFrame:
    return group_revenue(df, "category").head(3)


# Group revenue by month
def revenue_by_month(df: DataFrame)  -> DataFrame:
    # Group revenue by month using the date column
    group_month = group_revenue(
        df, pd.Grouper(key="date", freq="MS"))

    # Sort month in chronological order
    group_month = group_month.sort_values(by="date")

    # Format dates as month and years
    group_month["date"] = group_month["date"].dt.strftime("%B %Y")

    return group_month


# Group revenue by weekday
def revenue_by_weekday(df: DataFrame)  -> DataFrame:

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
def calculate_order_value_distribution(df: DataFrame) -> dict[str, float]:
    # Calculate total revenue for each order
    orders_total_revenues = order_totals(df)

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
def calculate_order_ranges(df: DataFrame) -> DataFrame:
    from_to = _calculate_order_boundaries(df)

    # Calculate total revenue for each order
    orders = order_totals(df)

    # Handle orders with identical revenue values
    if len(from_to) == 1:
        return DataFrame(
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
    result = DataFrame(
        {
            "number of orders": counts,
            "percentages" :count_procent
        }
    )

    return result

# Calculate standard deviation of order values
def calculate_order_value_std(df: DataFrame) -> float:
    # Calculate total revenue for each order
    order = order_totals(df)

    # Calculate standart deviation
    std = order["revenue"].std()

    return float(std)


def get_order_range_boundaries(df:DataFrame) -> list[float]:
    # return revenue range boundaries for plotting
    return _calculate_order_boundaries(df)


# Calculate variance of order values
def calculate_order_value_variance(df: DataFrame) -> float:
    # Calculate total revenue for each order
    orders = order_totals(df)
    variance = orders["revenue"].var()

    return float(variance)


# Calculate and returns order revenue boundaries
def _calculate_order_boundaries(df: DataFrame) -> list[float]:
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
def calculate_descriptive_statistics(df:DataFrame) -> dict:
    orders = order_totals(df)
    values = orders["revenue"]

    if values.empty:
        return {}

    mode = values.mode().tolist()
    q1 = values.quantile(0.25, interpolation="linear")
    q3 = values.quantile(0.75, interpolation="linear")
    iqr = q3 - q1

    return {
        "mode":[float(value) for value in mode],
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
    }


# Detect outliners in order values using the IQR methot
def detect_outliers(df: DataFrame) -> DataFrame:

    orders = order_totals(df)
    stats = calculate_descriptive_statistics(df)

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

def calculate_order_z_scores(df: DataFrame) -> DataFrame:
    orders = order_totals(df)

    # Get order revenue values
    values = orders["revenue"]

    if values.empty:
        orders["z_score"] = pd.Series(dtype=float)
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
def calculate_units_revenue_correlation(df: DataFrame) -> float:
    correlation = df["units"].corr(df["revenue"])

    return float(correlation)
