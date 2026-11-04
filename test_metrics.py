
import pandas as pd
import pytest
from src.metrics import (
    calculate_aov,
    calculate_order_ranges,
    calculate_order_value_distribution,
    calculate_order_value_std,
    calculate_order_value_variance,
    get_order_range_boundaries,
    calculate_total_revenue,
    calculate_total_revenue_units,
    calculate_total_units,
    count_orders,
    group_revenue,
    revenue_by_category,
    revenue_by_city,
    revenue_by_month,
    revenue_by_weekday,
    revenue_top_3_categories,
    revenue_top_3_cities,
)


# Test counting unique orders
def test_count_orders():
    df = pd.DataFrame({
        "order_id": [101, 102, 103, 103]
    })

    result = count_orders(df)

    assert result == 3


# Test calculating total revenue and total units
def test_calculate_total_revenue_units():
    df = pd.DataFrame({
        "revenue": [200, 300, 700, 900],
        "units": [4, 0, 7, 2]
    })

    total_revenue, total_units = calculate_total_revenue_units(df)

    assert total_revenue == 2100
    assert total_units == 13


# Test grouping revenue by city
def test_group_revenue_by_city():
    df = pd.DataFrame({
        "city": ["Stockholm", "Malmö", "Uppsala", "Malmö", "Uppsala"],
        "revenue": [100, 200, 300, 400, 100]
    })

    result = group_revenue(df, "city")

    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["city"].tolist() == ["Malmö", "Uppsala", "Stockholm"]


# Test grouping revenue by date
def test_group_revenue_by_date():
    df = pd.DataFrame({
        "date": ["2024-04-16", "2024-04-12", "2024-05-16",
                 "2024-04-12", "2024-05-16"],
        "revenue": [100, 200, 300, 400, 100]
    })

    result = group_revenue(df, "date")

    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["date"].tolist() == [
        "2024-04-12", "2024-05-16", "2024-04-16"
    ]


# Test grouping revenue by category
def test_group_revenue_by_category():
    df = pd.DataFrame({
        "category": ["Home", "Toys", "Sport", "Toys", "Sport"],
        "revenue": [100, 200, 300, 400, 100]
    })

    result = group_revenue(df, "category")

    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["category"].tolist() == ["Toys", "Sport", "Home"]


# Test calculating revenue by category
def test_revenue_by_category():
    df = pd.DataFrame({
        "category": ["Home", "Toys", "Sport", "Toys", "Sport", "Pets"],
        "revenue": [100, 200, 300, 400, 100, 800]
    })

    result = revenue_by_category(df)

    assert result["revenue"].tolist() == [800, 600, 400, 100]
    assert result["category"].tolist() == ["Pets", "Toys", "Sport", "Home"]


# Test calculating top 3 categories
def test_revenue_top_3_categories():
    df = pd.DataFrame({
        "category": ["Home", "Toys", "Sport", "Toys", "Sport", "Pets"],
        "revenue": [100, 200, 300, 400, 100, 800]
    })

    result = revenue_top_3_categories(df)

    assert result["revenue"].tolist() == [800, 600, 400]
    assert result["category"].tolist() == ["Pets", "Toys", "Sport"]


# Test calculating revenue by city
def test_revenue_by_city():
    df = pd.DataFrame({
        "city": ["Stockholm", "Malmö", "Uppsala", "Malmö", "Dalby", "Uppsala"],
        "revenue": [100, 200, 300, 400, 50, 100]
    })

    result = revenue_by_city(df)

    assert result["revenue"].tolist() == [600, 400, 100, 50]
    assert result["city"].tolist() == ["Malmö", "Uppsala", "Stockholm", "Dalby"]


# Test calculating top 3 cities
def test_revenue_top_3_cities():
    df = pd.DataFrame({
        "city": ["Stockholm", "Malmö", "Uppsala", "Malmö", "Dalby", "Uppsala"],
        "revenue": [100, 200, 300, 400, 50, 100]
    })

    result = revenue_top_3_cities(df)

    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["city"].tolist() == ["Malmö", "Uppsala", "Stockholm"]


# Test calculating revenue by month
def test_revenue_by_month():
    df = pd.DataFrame({
        "date": pd.to_datetime([
            "2025-10-25", "2025-01-26", "2024-10-25",
            "2024-01-12", "2024-01-10", "2024-01-26"
        ]),
        "revenue": [100, 200, 300, 400, 50, 100]
    })

    result = revenue_by_month(df)

    assert result["revenue"].tolist() == [
        550, 0, 0, 0, 0, 0, 0, 0, 0, 300, 0, 0,
        200, 0, 0, 0, 0, 0, 0, 0, 0, 100
    ]


# Test calculating revenue by weekday
def test_revenue_by_weekday():
    df = pd.DataFrame({
        "date": pd.to_datetime([
            "2026-10-25", "2026-01-26", "2024-10-25",
            "2024-01-12", "2024-01-10", "2024-01-26"
        ]),
        "revenue": [100, 200, 300, 400, 50, 100]
    })

    result = revenue_by_weekday(df)

    assert result["revenue"].tolist() == [200, 50, 800, 100]
    assert result["weekday"].tolist() == [
        "Monday", "Wednesday", "Friday", "Sunday"
    ]


# Test calculating order value distribution
def test_order_value_distribution():
    df = pd.DataFrame({
        "order_id": [101, 102, 103, 103, 103],
        "revenue": [100, 200, 300, 400, 100]
    })

    result = calculate_order_value_distribution(df)

    assert result == {
        "min_revenue": 100,
        "max_revenue": 800,
        "median_revenue": 200
    }


# Test calculating average order value
def test_calculate_aov():
    df = pd.DataFrame({
        "order_id": [101, 102, 103, 103, 103],
        "revenue": [100, 200, 300, 400, 100]
    })

    result = calculate_aov(df)

    assert result == pytest.approx(1100 / 3)


# Test AOV when there are no orders
def test_calculate_aov_zero():
    df = pd.DataFrame({
        "order_id": [],
        "revenue": []
    })

    result = calculate_aov(df)

    assert result == 0.0


# Test calculating order ranges
def test_calculate_order_ranges():
    df = pd.DataFrame({
        "order_id": [101, 102, 103, 104, 105],
        "revenue": [100, 200, 100, 200, 800]
    })

    result = calculate_order_ranges(df)

    assert result["number of orders"].sum() == 5
    assert len(result) == 5
    assert round(result["percentages"].sum(), 2) == 100


# Test order ranges with identical values
def test_calculate_order_ranges_identical_values():
    df = pd.DataFrame({
        "order_id": [101, 102, 103],
        "revenue": [100, 100, 100]
    })

    result = calculate_order_ranges(df)

    assert result.loc["group1", "number of orders"] == 3
    assert result.loc["group1", "percentages"] == 100.0


# Test calculating total revenue
def test_calculate_total_revenue():
    df = pd.DataFrame({
        "revenue": [100, 200, 300]
    })

    result = calculate_total_revenue(df)

    assert result == 600.0


# Test calculating total units
def test_calculate_total_units():
    df = pd.DataFrame({
        "units": [4, 0, 7, 2]
    })

    result = calculate_total_units(df)

    assert result == 13


# Test calculating standard deviation of order values
def test_calculate_order_value_std():
    df = pd.DataFrame({
        "order_id": [101, 102, 103],
        "revenue": [100, 200, 300]
    })

    result = calculate_order_value_std(df)

    assert result == pytest.approx(100.0)
    assert isinstance(result, float)


# Test calculating variance of order values
def test_calculate_order_value_variance():
    df = pd.DataFrame({
        "order_id": [101, 102, 103],
        "revenue": [100, 200, 300]
    })

    result = calculate_order_value_variance(df)

    assert result == pytest.approx(10000.0)
    assert isinstance(result, float)
def test_calculate_order_value_std_identical_values():
    df = pd.DataFrame({
        "order_id": [101, 102, 103],
        "revenue": [100, 100, 100]
    })

    result = calculate_order_value_std(df)

    assert result == 0.0
    assert isinstance(result, float)


def test_calculate_order_value_variance_identical_values():
    df = pd.DataFrame({
        "order_id": [101, 102, 103],
        "revenue": [100, 100, 100]
    })



    result = calculate_order_value_variance(df)

    assert result == 0.0
    assert isinstance(result, float)


def test_get_order_range_boundaries():
    df = pd.DataFrame({
        "order_id": [101, 102, 103, 104, 105],
        "revenue": [100, 200, 300, 400, 800]
    })

    result = get_order_range_boundaries(df)

    assert result == [100.0, 180.0, 260.0, 340.0, 570.0, 800.0]
    assert isinstance(result, list)
    assert all(isinstance(value, float) for value in result)


def test_calculate_order_value_std_empty_dataframe():
    df = pd.DataFrame({
        "order_id": [],
        "revenue": []
    })
    

    result = calculate_order_value_std(df)

    assert pd.isna(result)
    assert isinstance(result, float)


# Test variance with an empty DataFrame
def test_calculate_order_value_variance_empty_dataframe():
    df = pd.DataFrame({
        "order_id": [],
        "revenue": []
    })

    result = calculate_order_value_variance(df)

    assert pd.isna(result)
    assert isinstance(result, float)