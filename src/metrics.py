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
    df_required[group_by] = df_required[group_by].astype(object)

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


def city_summary(df: DataFrame) -> DataFrame:
    """Return city, revenue and share_pct, with shares of total revenue."""
    return _group_revenue_summary(df, "city")


def top_categories_summary(df: DataFrame, n: int = 3) -> DataFrame:
    """Return the top n categories with revenue shares."""
    if (not isinstance(n, (int, np.integer)) or n <= 0):
        raise ValueError("n must be a positive integer")

    categories = category_summary(df)
    return categories.head(int(n))


def data_overview(df: DataFrame) -> dict[str, object]:
    """Return data-quality counts, date bounds, and dates without observations.

    Missing values and numeric infinities are allowed. Discrepancy checks
    include only rows with present, finite price, units, and revenue values.
    Missing-value and duplicate counts use the original input.

    Invalid dates are excluded from date bounds and calendar coverage.
    Dates without observations do not establish that sales were zero.
    Empty input with required columns returns zero counts and no date range.
    """
    required_cols = {"date", "order_id", "price", "units", "revenue"}
    missing_cols = required_cols - set(df.columns)

    if missing_cols:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing_cols))}")

    missing_values_by_column = {
        column: int(count)
        for column, count in df.isna().sum().items()
    }
    missing_values_total = sum(missing_values_by_column.values())
    duplicate_row_count = int(df.duplicated().sum())

    numeric = df[["price", "units", "revenue"]].copy()

    for column in numeric.columns:
        try:
            numeric[column] = pd.to_numeric(numeric[column], errors="raise")
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"{column} must contain numeric values"
            ) from exc

    negative_numeric_row_count = int(
        numeric.lt(0).any(axis=1).sum()
    )

    numeric_values = numeric.to_numpy(dtype=float, na_value=np.nan)
    valid_rows = np.isfinite(numeric_values).all(axis=1)
    valid_values = numeric_values[valid_rows]

    matches = np.isclose(
        valid_values[:, 0] * valid_values[:, 1],
        valid_values[:, 2],
        atol=0.01,
        rtol=0,
    )
    price_units_discrepancy_count = int((~matches).sum())

    dates = pd.to_datetime(df["date"], errors="coerce")
    valid_dates = dates.dropna()

    if valid_dates.empty:
        date_min = pd.NaT
        date_max = pd.NaT
        dates_without_observations = pd.DatetimeIndex([])
    else:
        date_min = valid_dates.min()
        date_max = valid_dates.max()

        observed_dates = pd.DatetimeIndex(
            valid_dates.dt.normalize().unique()
        )
        calendar_dates = pd.date_range(
            start=observed_dates.min(),
            end=observed_dates.max(),
            freq="D",
        )
        dates_without_observations = calendar_dates.difference(
            observed_dates
        ).sort_values()

    return {
        "row_count": len(df),
        "order_count": int(df["order_id"].nunique()),
        "missing_values_by_column": missing_values_by_column,
        "missing_values_total": missing_values_total,
        "duplicate_row_count": duplicate_row_count,
        "negative_numeric_row_count": negative_numeric_row_count,
        "price_units_discrepancy_count": price_units_discrepancy_count,
        "date_min": date_min,
        "date_max": date_max,
        "dates_without_observations": dates_without_observations,
    }


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


def order_histogram(
    df: DataFrame,
    bins: int = 25,
) -> dict[str, list[float] | list[int]]:
    """Return histogram bin_edges and counts for combined orders.

    Each bin includes its left boundary and excludes its right boundary,
    (except the final bin). NumPy determines the range, expanding it
    automatically for constant order revenues.
    """
    if (not isinstance(bins, (int, np.integer)) or bins <= 0):
        raise ValueError("bins must be a positive integer")

    orders = order_totals(df)

    if orders.empty:
        return {"bin_edges": [], "counts": []}

    counts, edges = np.histogram(
        orders["revenue"].to_numpy(),
        bins=int(bins),
    )

    return {
        "bin_edges": [float(edge) for edge in edges],
        "counts": [int(count) for count in counts],
    }


def order_summary(df: DataFrame) -> dict[str, float]:
    """
    Return statistics for combined order revenues using linear quantile
    interpolation. Invalid input raises ValueError. Empty input with required
    columns still returns all seven keys.
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


def monthly_summary(df: DataFrame) -> DataFrame:
    """Return chronological monthly revenue, order counts, and daily coverage.

    An order ID appearing in multiple months counts once in each month.
    Observing every calendar date does not guarantee every transaction
    was captured. Revenue per day is reported only for fully observed months.

    Unobserved months within the range have zero counts and NaN financial
    metrics. Empty input with required columns returns a typed empty table.
    Invalid input raises ValueError. Dates are timezone-naive.
    """

    required_cols = {"date", "order_id", "revenue"}
    missing_cols = required_cols - set(df.columns)

    if missing_cols:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing_cols))}"
        )

    df_required = df[["date", "order_id", "revenue"]].copy()

    if df_required["order_id"].isna().any():
        raise ValueError("Order IDs cannot contain missing values")

    try:
        revenue = pd.to_numeric(df_required["revenue"], errors="raise")
    except (ValueError, TypeError) as exc:
        raise ValueError("Revenue must contain numeric values") from exc

    if revenue.isna().any():
        raise ValueError("Revenue cannot contain missing values")

    if not np.isfinite(revenue.to_numpy(dtype=float)).all():
        raise ValueError("Revenue must contain finite values")

    df_required["revenue"] = revenue

    try:
        dates = pd.to_datetime(df_required["date"], errors="raise")
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError("Dates must contain valid datetime values") from exc

    if dates.isna().any():
        raise ValueError("Dates cannot contain missing values")

    df_required["date"] = dates

    column_dtypes = {
        "month": "datetime64[ns]",
        "revenue": "float64",
        "order_count": "int64",
        "calendar_days": "int64",
        "observed_days": "int64",
        "coverage_status": "string",
        "revenue_per_day": "float64",
        "aov": "float64",
    }

    if df_required.empty:
        return DataFrame({
            column: pd.Series(dtype=dtype)
            for column, dtype in column_dtypes.items()
        })

    df_required["observed_date"] = df_required["date"].dt.normalize()
    df_required["month"] = (
        df_required["date"].dt.to_period("M").dt.to_timestamp()
    )

    monthly = df_required.groupby("month").agg(
        revenue=("revenue", "sum"),
        order_count=("order_id", "nunique"),
        observed_days=("observed_date", "nunique"),
    )

    months = pd.date_range(
        start=monthly.index.min(),
        end=monthly.index.max(),
        freq="MS",
        name="month",
    )
    monthly = monthly.reindex(months)

    for column in ["order_count", "observed_days"]:
        monthly[column] = monthly[column].fillna(0).astype("int64")

    monthly["calendar_days"] = months.days_in_month

    has_observations = monthly["observed_days"] > 0
    all_days_observed = (
        monthly["observed_days"] == monthly["calendar_days"]
    )

    monthly["coverage_status"] = pd.Series(
        "no_observations",
        index=monthly.index,
        dtype="string",
    )
    monthly.loc[has_observations, "coverage_status"] = "partial"
    monthly.loc[all_days_observed, "coverage_status"] = "all_days_observed"

    monthly["revenue_per_day"] = (
        monthly["revenue"] / monthly["calendar_days"]
    ).where(all_days_observed)

    positive_order_count = monthly["order_count"].where(
        monthly["order_count"] > 0
    )
    monthly["aov"] = monthly["revenue"] / positive_order_count

    return monthly.reset_index()[list(column_dtypes)]


def monthly_category_summary(df: DataFrame) -> DataFrame:
    """Return month, category and revenue in chronological order.

    Observed categories share one monthly range, from the earliest
    to the latest month across the entire input. Missing category labels
    remain a separate group. NaN revenue means no observations for that
    month/category combination.

    Empty input with required columns returns a typed empty table.
    Invalid input raises ValueError. Dates are expected to be timezone-naive.
    """
    required_cols = {"date", "category", "revenue"}
    missing_cols = required_cols - set(df.columns)

    if missing_cols:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing_cols))}")

    df_required = df[["date", "category", "revenue"]].copy()
    df_required["category"] = df_required["category"].astype(object)

    try:
        revenue = pd.to_numeric(df_required["revenue"], errors="raise")
    except (ValueError, TypeError) as exc:
        raise ValueError("Revenue must contain numeric values") from exc

    if revenue.isna().any():
        raise ValueError("Revenue cannot contain missing values")

    if not np.isfinite(revenue.to_numpy(dtype=float)).all():
        raise ValueError("Revenue must contain finite values")

    df_required["revenue"] = revenue

    try:
        dates = pd.to_datetime(df_required["date"], errors="raise")
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError("Dates must contain valid datetime values") from exc

    if dates.isna().any():
        raise ValueError("Dates cannot contain missing values")

    df_required["date"] = dates

    if df_required.empty:
        return DataFrame({
            "month": pd.Series(dtype="datetime64[ns]"),
            "category": pd.Series(dtype=object),
            "revenue": pd.Series(dtype="float64"),
        })

    df_required["month"] = (
        df_required["date"].dt.to_period("M").dt.to_timestamp()
    )

    grouped = df_required.groupby(
        ["month", "category"],
        dropna=False,
        observed=True,
    )[["revenue"]].sum()

    months = pd.date_range(
        start=df_required["month"].min(),
        end=df_required["month"].max(),
        freq="MS",
    )
    categories = grouped.index.get_level_values("category").unique()

    complete_index = pd.MultiIndex.from_product(
        [months, categories],
        names=["month", "category"],
    )

    result = grouped.reindex(complete_index).reset_index()
    result = result.sort_values(
        by=["month", "category"],
        ascending=[True, True],
        na_position="last",
        ignore_index=True,
    )

    return result[["month", "category", "revenue"]]


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
