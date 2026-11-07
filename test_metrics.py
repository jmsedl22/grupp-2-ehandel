import numpy as np
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
    monthly_summary,
    revenue_by_weekday,
    revenue_top_3_categories,
    revenue_top_3_cities,
    calculate_descriptive_statistics,
    calculate_order_z_scores,
    detect_outliers,
    calculate_units_revenue_correlation,
)


def test_count_orders():
    df = pd.DataFrame({"order_id": [101, 102, 103, 103]})
    result = count_orders(df)

    assert result == 3
    assert type(result) is int


def test_calculate_total_revenue_units():
    df = pd.DataFrame({
        "revenue": [200, 300, 700, 900],
        "units": [4, 0, 7, 2]
    })

    total_revenue, total_units = calculate_total_revenue_units(df)

    assert total_revenue == 2100
    assert total_units == 13
    assert type(total_revenue) is float
    assert type(total_units) is int
    assert isinstance(calculate_total_revenue_units(df), tuple)


def test_group_revenue_by_city():
    df = pd.DataFrame({
        "city": ["Stockholm", "Malmö", "Uppsala", "Malmö", "Uppsala"],
        "revenue": [100, 200, 300, 400, 100]
    })

    result = group_revenue(df, "city")

    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["city"].tolist() == ["Malmö", "Uppsala", "Stockholm"]
    assert isinstance(result, pd.DataFrame)


def test_group_revenue_by_date():
    df = pd.DataFrame({
        "date": [
            "2024-04-16", "2024-04-12", "2024-05-16",
            "2024-04-12", "2024-05-16"
        ],
        "revenue": [100, 200, 300, 400, 100]
    })

    result = group_revenue(df, "date")

    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["date"].tolist() == [
        "2024-04-12", "2024-05-16", "2024-04-16"
    ]
    assert isinstance(result, pd.DataFrame)


def test_group_revenue_by_category():
    df = pd.DataFrame({
        "category": ["Home", "Toys", "Sport", "Toys", "Sport"],
        "revenue": [100, 200, 300, 400, 100]
    })

    result = group_revenue(df, "category")

    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["category"].tolist() == ["Toys", "Sport", "Home"]
    assert isinstance(result, pd.DataFrame)


def test_revenue_by_category():
    df = pd.DataFrame({
        "category": ["Home", "Toys", "Sport", "Toys", "Sport", "Pets"],
        "revenue": [100, 200, 300, 400, 100, 800]
    })

    result = revenue_by_category(df)

    assert result["revenue"].tolist() == [800, 600, 400, 100]
    assert result["category"].tolist() == ["Pets", "Toys", "Sport", "Home"]
    assert isinstance(result, pd.DataFrame)


def test_revenue_top_3_categories():
    df = pd.DataFrame({
        "category": ["Home", "Toys", "Sport", "Toys", "Sport", "Pets"],
        "revenue": [100, 200, 300, 400, 100, 800]
    })

    result = revenue_top_3_categories(df)

    assert result["revenue"].tolist() == [800, 600, 400]
    assert result["category"].tolist() == ["Pets", "Toys", "Sport"]
    assert isinstance(result, pd.DataFrame)


def test_revenue_by_city():
    df = pd.DataFrame({
        "city": ["Stockholm", "Malmö", "Uppsala", "Malmö", "Dalby", "Uppsala"],
        "revenue": [100, 200, 300, 400, 50, 100]
    })

    result = revenue_by_city(df)

    assert result["revenue"].tolist() == [600, 400, 100, 50]
    assert result["city"].tolist() == ["Malmö", "Uppsala", "Stockholm", "Dalby"]
    assert isinstance(result, pd.DataFrame)


def test_revenue_top_3_cities():
    df = pd.DataFrame({
        "city": ["Stockholm", "Malmö", "Uppsala", "Malmö", "Dalby", "Uppsala"],
        "revenue": [100, 200, 300, 400, 50, 100]
    })

    result = revenue_top_3_cities(df)

    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["city"].tolist() == ["Malmö", "Uppsala", "Stockholm"]
    assert isinstance(result, pd.DataFrame)


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

    assert result["date"].tolist() == [
        "January 2024", "February 2024", "March 2024",
        "April 2024", "May 2024", "June 2024",
        "July 2024", "August 2024", "September 2024",
        "October 2024", "November 2024", "December 2024",
        "January 2025", "February 2025", "March 2025",
        "April 2025", "May 2025", "June 2025",
        "July 2025", "August 2025", "September 2025",
        "October 2025"
    ]
    assert isinstance(result, pd.DataFrame)


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
    assert isinstance(result, pd.DataFrame)


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
    assert isinstance(result, dict)
    assert type(result["min_revenue"]) is float
    assert type(result["max_revenue"]) is float
    assert type(result["median_revenue"]) is float


def test_calculate_aov():
    df = pd.DataFrame({
        "order_id": [101, 102, 103, 103, 103],
        "revenue": [100, 200, 300, 400, 100]
    })

    result = calculate_aov(df)

    assert result == pytest.approx(1100 / 3)
    assert isinstance(result, float)


def test_calculate_aov_zero():
    df = pd.DataFrame({
        "order_id": [],
        "revenue": []
    })

    result = calculate_aov(df)

    assert result == 0.0
    assert type(result) is float


def test_calculate_order_ranges():
    df = pd.DataFrame({
        "order_id": [101, 102, 103, 104, 105],
        "revenue": [100, 200, 100, 200, 800]
    })

    result = calculate_order_ranges(df)

    assert result["number of orders"].sum() == 5
    assert len(result) == 5
    assert round(result["percentages"].sum(), 2) == 100
    assert isinstance(result, pd.DataFrame)


def test_calculate_order_ranges_identical_values():
    df = pd.DataFrame({
        "order_id": [101, 102, 103],
        "revenue": [100, 100, 100]
    })

    result = calculate_order_ranges(df)

    assert result.loc["group1", "number of orders"] == 3
    assert result.loc["group1", "percentages"] == 100.0


def test_calculate_total_revenue():
    df = pd.DataFrame({"revenue": [100, 200, 300]})

    result = calculate_total_revenue(df)

    assert result == 600.0
    assert type(result) is float


def test_calculate_total_units():
    df = pd.DataFrame({"units": [4, 0, 7, 2]})

    result = calculate_total_units(df)

    assert result == 13
    assert type(result) is int


def test_calculate_total_units_missing_values():
    for value in [None, float("nan")]:
        df = pd.DataFrame({"units": [4, value, 2]})

        with pytest.raises(ValueError):
            calculate_total_units(df)


def test_calculate_total_units_invalid_values():
    for value in [float("inf"), float("-inf"), 2.5]:
        df = pd.DataFrame({"units": [4, value, 2]})

        with pytest.raises(ValueError):
            calculate_total_units(df)


def test_calculate_order_value_std():
    df = pd.DataFrame({
        "order_id": [101, 102, 103],
        "revenue": [100, 200, 300]
    })

    result = calculate_order_value_std(df)

    assert result == pytest.approx(100.0)
    assert isinstance(result, float)


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


def test_calculate_order_value_variance_empty_dataframe():
    df = pd.DataFrame({
        "order_id": [],
        "revenue": []
    })

    result = calculate_order_value_variance(df)

    assert pd.isna(result)
    assert isinstance(result, float)


def test_calculate_descriptive_statistics():
    df = pd.DataFrame({
        "order_id": [101, 102, 103, 104, 105],
        "revenue": [100, 200, 100, 200, 800]
    })

    result = calculate_descriptive_statistics(df)

    assert result["mode"] == [100, 200]
    assert result["q1"] == 100
    assert result["q3"] == 200
    assert result["iqr"] == 100


def test_calculate_order_z_scores():
    df = pd.DataFrame({
        "order_id": [101, 102, 103, 104, 105],
        "revenue": [100, 200, 100, 200, 800]
    })

    result = calculate_order_z_scores(df).sort_values("order_id")

    assert result["z_score"].round(3).tolist() == [
        -0.610, -0.271, -0.610, -0.271, 1.763
    ]
    assert isinstance(result, pd.DataFrame)


def test_detect_outliers():
    df = pd.DataFrame({
        "order_id": [101, 102, 103, 104, 105, 106, 107],
        "revenue": [10, 400, 500, 400, 500, 450, 1200]
    })

    result = detect_outliers(df)

    assert len(result) == 2
    assert sorted(result["order_id"].tolist()) == [101, 107]
    assert isinstance(result, pd.DataFrame)


def test_calculate_units_revenue_correlation():
    df = pd.DataFrame({
        "units": [5, 10, 4, 2, 5],
        "revenue": [100, 200, 400, 500, 300]
    })

    result = calculate_units_revenue_correlation(df)

    df_zero = pd.DataFrame({
        "units": [3, 1, 2],
        "revenue": [100, 100, 200]
    })
    result_zero = calculate_units_revenue_correlation(df_zero)

    df_const = pd.DataFrame({
        "units": [10, 10, 10, 10],
        "revenue": [100, 200, 400, 500]
    })
    result_const = calculate_units_revenue_correlation(df_const)

    df_empty = pd.DataFrame(columns=["units", "revenue"])
    result_empty = calculate_units_revenue_correlation(df_empty)

    assert round(result, 3) == -0.643
    assert round(result_zero, 3) == 0.0
    assert pd.isna(result_const)
    assert pd.isna(result_empty)
    assert isinstance(result, (float, np.floating))
    assert isinstance(result_zero, (float, np.floating))
    assert isinstance(result_const, (float, np.floating))
    assert isinstance(result_empty, (float, np.floating))


def test_monthly_summary_full_leap_month():
    df = pd.DataFrame({
        "date": pd.date_range("2024-02-01", "2024-02-29"),
        "order_id": range(29),
        "revenue": [10.0] * 29,
    })

    result = monthly_summary(df)
    row = result.iloc[0]

    assert list(result.columns) == [
        "month",
        "revenue",
        "order_count",
        "calendar_days",
        "observed_days",
        "coverage_status",
        "revenue_per_day",
        "aov",
    ]
    assert row["month"] == pd.Timestamp("2024-02-01")
    assert row["revenue"] == pytest.approx(290.0)
    assert row["order_count"] == 29
    assert row["calendar_days"] == 29
    assert row["observed_days"] == 29
    assert row["coverage_status"] == "all_days_observed"
    assert row["revenue_per_day"] == pytest.approx(10.0)
    assert row["aov"] == pytest.approx(10.0)


def test_monthly_summary_partial_and_missing_months():
    df = pd.DataFrame({
        "date": pd.to_datetime([
            "2024-03-01 09:00:00",
            "2024-01-31 15:00:00",
            "2024-01-31 09:00:00",
        ]),
        "order_id": ["A", "A", "A"],
        "revenue": ["0", "49.75", "100.25"],
    })
    original = df.copy(deep=True)

    result = monthly_summary(df)

    assert result["month"].tolist() == [
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-02-01"),
        pd.Timestamp("2024-03-01"),
    ]
    assert result["calendar_days"].tolist() == [31, 29, 31]
    assert result["order_count"].tolist() == [1, 0, 1]
    assert result["observed_days"].tolist() == [1, 0, 1]
    assert result["coverage_status"].tolist() == [
        "partial", "no_observations", "partial",
    ]
    assert result["revenue_per_day"].isna().all()

    january, february, march = [result.iloc[i] for i in range(3)]

    assert january["revenue"] == pytest.approx(150.0)
    assert january["aov"] == pytest.approx(150.0)

    assert pd.isna(february["revenue"])
    assert pd.isna(february["aov"])

    # An observed zero is different from an unobserved month.
    assert march["revenue"] == 0.0
    assert march["aov"] == 0.0

    pd.testing.assert_frame_equal(df, original)


def test_monthly_summary_empty_input():
    df = pd.DataFrame(columns=["date", "order_id", "revenue"])

    result = monthly_summary(df)

    assert result.empty
    assert list(result.columns) == [
        "month",
        "revenue",
        "order_count",
        "calendar_days",
        "observed_days",
        "coverage_status",
        "revenue_per_day",
        "aov",
    ]
    assert pd.api.types.is_datetime64_any_dtype(result["month"])
    assert pd.api.types.is_string_dtype(result["coverage_status"])

    for column in ["order_count", "calendar_days", "observed_days"]:
        assert pd.api.types.is_integer_dtype(result[column])

    for column in ["revenue", "revenue_per_day", "aov"]:
        assert pd.api.types.is_float_dtype(result[column])


@pytest.mark.parametrize("column", ["date", "order_id", "revenue"])
def test_monthly_summary_rejects_missing_columns_even_when_empty(column):
    df = pd.DataFrame(columns=["date", "order_id", "revenue"])
    df = df.drop(columns=[column])

    with pytest.raises(ValueError):
        monthly_summary(df)


@pytest.mark.parametrize(
    "column, value",
    [
        ("order_id", None),
        ("revenue", "not numeric"),
        ("revenue", None),
        ("revenue", np.nan),
        ("revenue", np.inf),
        ("revenue", -np.inf),
        ("date", "not a date"),
        ("date", None),
        ("date", pd.NaT),
    ],
)
def test_monthly_summary_rejects_invalid_values(column, value):
    data = {
        "date": ["2024-01-01"],
        "order_id": ["A"],
        "revenue": [10.0],
    }
    data[column] = [value]

    with pytest.raises(ValueError):
        monthly_summary(pd.DataFrame(data))
