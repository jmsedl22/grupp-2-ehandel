
import pandas as pd

from src.metrics import (
    calculate_aov,
    calculate_order_ranges,
    calculate_order_value_distribution,
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
    calulate_descriptive_statistics,
    calculate_order_z_scores,
    detect_outliers,
    calculate_units_revenue_correlation,
)


# Test counting unique orders 
def test_count_ordes():
    # Create sample data with duplicate order IDs
    df = pd.DataFrame({"order_id":[101,102,103,103]})

    result = count_orders(df)
    
    # Verify that duplicate order IDs are counted only once
    assert result == 3                                     


# Test calculate total revenue and total units
def test_calculate_total_revenue_units():
    # Create sample sales data with revenue and units
    df = pd.DataFrame({
        "revenue":[200, 300, 700, 900], 
        "units":[4, 0, 7, 2]
    })

    # Calculate total revenue and units
    total_revenue, total_units = calculate_total_revenue_units(df)

    # Verify the expected total revenue and units
    assert total_revenue == 2100
    assert total_units == 13                                       
    

# Test grouping total revenue by city
def test_group_revenue_by_city():
    # Create sample sales data
    df = pd.DataFrame({
        "city":["Stockholm", "Malmö", "Uppsala", "Malmö",  "Uppsala"],
        "revenue":[100, 200, 300, 400, 100]
    })

    # Calculate total revenue for each city
    result = group_revenue(df,"city")

    # Verify total revenue for each city and descending order
    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["city"].tolist() == ["Malmö", "Uppsala", "Stockholm"]


def test_group_revenue_by_date():
    # Create sample sales date with dates and revenue
    df = pd.DataFrame({
        "date":["2024-04-16", "2024-04-12", "2024-05-16", "2024-04-12", "2024-05-16"],
        "revenue":[100, 200, 300, 400, 100]
    })

    # Calculate total revenue for each date
    result = group_revenue(df,"date")

    # Verify total revenue for each date and descebding order
    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["date"].tolist() == ["2024-04-12", "2024-05-16","2024-04-16"]


# Test grouping revenue by category
def test_group_revenue_by_category():
    # Create sample sales data with catagories and revenue
    df = pd.DataFrame({
        "category":["Home", "Toys", "Sport", "Toys", "Sport"],
        "revenue":[100, 200, 300, 400, 100]
    })

    # Calculate total revenue for each category
    result = group_revenue(df,"category")

    # Verify total revenue for each category and descending order
    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["category"].tolist() == ["Toys", "Sport", "Home"]


# Test calculating revenue by category
def test_revenue_by_category():
    # Create sample sales data with categories and revenue
    df = pd.DataFrame({
        "category":["Home", "Toys", "Sport", "Toys", "Sport", "Pets"],
        "revenue":[100, 200, 300, 400, 100, 800]
    })

    # Calculate total revenue for each category
    result = revenue_by_category(df)

    # Verify total revenue for each category and descending order
    assert result["revenue"].tolist() == [800, 600, 400, 100]
    assert result["category"].tolist() == ["Pets", "Toys", "Sport", "Home"]



# Test calculating revenue for the top 3 categories 
def test_revenue_top_3_categories():
    # Create sample sales data with categories and revenue
    df = pd.DataFrame({
        "category":["Home", "Toys", "Sport", "Toys", "Sport", "Pets"],
        "revenue":[100, 200, 300, 400, 100, 800]
    })

    # Calculate revenue for top 3 categories
    result = revenue_top_3_categories(df)

    # Verify the 3 top categories by revenue in descending order
    assert result["revenue"].tolist() == [800, 600, 400]
    assert result["category"].tolist() == ["Pets", "Toys", "Sport"]
    

# Test calculating total revenue by city    
def test_revenue_by_city():
    # Create sample sales data with cities and revenue
        df = pd.DataFrame({
            "city":["Stockholm", "Malmö", "Uppsala", "Malmö", "Dalby", "Uppsala"],
            "revenue":[100, 200, 300, 400, 50, 100]
        })
    
        # Calculate total revenue for each city
        result = revenue_by_city(df)
    
        # Verify total revenue for each city and descending order
        assert result["revenue"].tolist() == [600, 400, 100, 50]
        assert result["city"].tolist() == ["Malmö", "Uppsala", "Stockholm", "Dalby"]


# Test calculating revenue for the top 3 cities
def test_revenue_top_3_cities():
    # Create sample sales data with cities and revenue
        df = pd.DataFrame({
            "city":["Stockholm", "Malmö", "Uppsala", "Malmö", "Dalby", "Uppsala"],
            "revenue":[100, 200, 300, 400, 50, 100]
        })
    
        # Calculate revenue for the top 3 cities
        result = revenue_top_3_cities(df)
    
        # Verify the top 3 cities be revenue in descending order
        assert result["revenue"].tolist() == [600, 400, 100]
        assert result["city"].tolist() == ["Malmö", "Uppsala", "Stockholm"]


# Test calculating total revenue by month
def test_revenue_by_month():
     # Create sample sales date with dates and revenue
         df = pd.DataFrame({
             "date":pd.to_datetime(["2025-10-25", "2025-01-26", "2024-10-25", "2024-01-12", "2024-01-10", "2024-01-26"]),
             "revenue":[100, 200, 300, 400, 50, 100]
         })
     
         # Calculate total revenue for each month
         result = revenue_by_month(df)
     
         # Verify total revenue for each month and sorting order
         assert result["revenue"].tolist() == [550, 0, 0, 0, 0, 0, 0, 0, 0, 300, 0, 0,  200, 0, 0, 0, 0, 0, 0, 0, 0, 100]
         assert result["date"].tolist() == [ "January 2024", "February 2024", "March 2024", "April 2024", "May 2024", "June 2024", "July 2024", "August 2024", "September 2024", "October 2024", "November 2024", "December 2024",
                                            "January 2025", "February 2025", "March 2025", "April 2025", "May 2025", "June 2025", "July 2025", "August 2025", "September 2025", "October 2025",
                                            ]
     

# Test calculeting revenue by weekdays
def test_revenue_by_weekday():
     # Create sample sales date with revenue and dates
         df = pd.DataFrame({
             "date":pd.to_datetime(["2026-10-25", "2026-01-26", "2024-10-25", "2024-01-12", "2024-01-10", "2024-01-26"]),
             "revenue":[100, 200, 300, 400, 50, 100]
         })
     
         # Calculate total revenue for each weekday
         result = revenue_by_weekday(df)
     
         # Verify total revenue for each weekday and weekday order
         assert result["revenue"].tolist() == [200, 50, 800, 100]
         assert result["weekday"].tolist() == ["Monday", "Wednesday","Friday", "Sunday"]
     

# Test calculating the distributionof order values
def test_order_value_distribution():
    # Create sample order data with IDs, dates and revenue
    df = pd.DataFrame({
        "order_id":[101, 102, 103, 103, 103],
            "date":["2024-04-16", "2024-04-12", "2024-05-16", "2024-04-12", "2024-05-16"],
            "revenue":[100, 200, 300, 400, 100]
        })

    # Calculate the minimum, maximum and medisn order revenue
    result = calculate_order_value_distribution(df)
    
    # Verify the minimum, maximum and median order revenue
    assert result == {
        "min_revenue": 100,
        "max_revenue" : 800,
        "median_revenue" : 200
    }


# Test calculating average order value (AOV)
def test_calculate_aov():
    # Create sample order data with IDs, dates and revenues
    df = pd.DataFrame({
        "order_id":[101, 102, 103, 103, 103],
            "date":["2024-04-16", "2024-04-12", "2024-05-16", "2024-05-16", "2024-05-16"],
            "revenue":[100, 200, 300, 400, 100]
        })

    # Calculate the average order value
    result = calculate_aov(df)

    # Verify the expected average order value
    assert result == 1100/3                                        


# Test calculating AOV when there are no orders
def test_calculate_aov_zero():
    # Create an empty DataFrame with order IDs and revenue
    df = pd.DataFrame({
        "order_id":[],
        "revenue":[]
    })

    # Calculate AOV when there are no orders
    result = calculate_aov(df)

    # Verify that AOV is zero when there are no orders
    assert result == 0.0          


# Test calculating the sidtribution of order values across ranges
def test_calculate_order_ranges():
    # Create sample order data with IDs and revenue
    df = pd.DataFrame({
            "order_id":[101, 102, 103, 104, 105],
            "revenue":[100, 200, 100, 200, 800]
    })

    # Calculate the distribution of orders across value ranges
    result = calculate_order_ranges(df)

    # Verify order counts, number of ranges and total percentage
    assert result["number of orders"].sum() == 5
    assert len(result) == 5
    assert round(result["percentages"].sum(),2)==100


# Test calculating total revenue
def test_calculate_total_revenue():
    # Create sample sales with revenue
    df = pd.DataFrame({
          "revenue": [100, 200, 300]
     })

    # Calculate total revenue
    result = calculate_total_revenue(df)

    # Verify the expected total revenue
    assert result == 600.0


# Test calculating total units sold
def test_calculate_total_units():
    # Create sample sales data with units
    df = pd.DataFrame({
          "units": [4, 0, 7, 2]
    })

    # Calculate total units sold
    result = calculate_total_units(df)

    # Verify the expected total number of units
    assert result == 13

def test_calulate_descriptive_statistics():
    # Create sample order data with IDs and revenue
    df = pd.DataFrame({
        "order_id":[101, 102, 103, 104, 105],
        "revenue":[100, 200, 100, 200, 800]
    })
     
    # Calculate the 
    result = calulate_descriptive_statistics(df)
     
    # Verify order counts, number of ranges and total percentage
    assert result["mode"] == [100, 200]
    assert result["q1"] == 100
    assert result["q3"] == 200
    assert result["iqr"] == 100


def test_calculate_order_z_scores():
# Create sample order data with IDs and revenue
    df = pd.DataFrame({
        "order_id":[101, 102, 103, 104, 105],
        "revenue":[100, 200, 100, 200, 800]
    })

    # Calculate z-scores for test orders
    result = calculate_order_z_scores(df)
    result = result.sort_values("order_id")

    # Verify z -scores for orders
    assert result["z_score"].round(3).tolist() == [-0.610, -0.271, -0.610, -0.271, 1.763]

def test_detect_outliers():
    # Create sample order data with IDs and revenue
    df = pd.DataFrame({
        "order_id":[101, 102, 103, 104, 105, 106, 107],
        "revenue":[10, 400, 500, 400, 500, 450, 1200]
    })

    # Detect outliers in test orders
    result = detect_outliers(df)

    # Verify that exactly two outliers was found and their order_ids
    assert len(result) == 2
    assert sorted(result["order_id"].tolist()) == [101, 107]


def test_calculate_units_revenue_correlation():
# Create sample order data with IDs and revenue
    df = pd.DataFrame({
        "units":[5, 10, 4, 2, 5],
        "revenue":[100, 200, 400, 500, 300]
    })
    result = calculate_units_revenue_correlation(df)
    
    df_zero = pd.DataFrame({
        "units":[3, 1, 2],
        "revenue":[100, 100, 200]
    })
    result_zero = calculate_units_revenue_correlation(df_zero)

    # testing correlation when all units values are equal
    # Create sample order data with IDs and revenue
    df_const = pd.DataFrame({
        "units":[10, 10, 10, 10],
        "revenue":[100, 200, 400, 500]
    })
    result_const = calculate_units_revenue_correlation(df_const)

    # testing correlation with an empty DataFrame
    df_empty = pd. DataFrame(columns=["units", "revenue"])

    result_empty = calculate_units_revenue_correlation(df_empty)
    assert round(result, 3) == -0.643
    assert round(result_zero, 3) == 0.0
    assert pd.isna(result_const)
    assert pd.isna(result_empty)