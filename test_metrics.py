
import pandas as pd
from src.metrics import count_orders


# test 
def test_count_ordes():
     #create a sample df with orders ids
    df =pd.DataFrame({"order_id":[101,102,103,103]})       
    result = count_orders(df)
    
    #check if the result is correct
    assert result ==3                                     

from src.metrics import calculate_total_revenue
from src.metrics import calculate_total_units
from src.metrics import calculate_total_revenue_units


#Test of function - combine the results of the two previous functions
def test_calculate_total_revenue_units():
    # create a sample df
    df = pd.DataFrame(                                             
    {"revenue":[200, 
                300, 
                700,
                900], 
     "units":[4,
              0,
              7,
              2]}   
    )

    # call the function and unpack the returned tuple
    total_revenue, total_units = calculate_total_revenue_units(df)

    # check if the results are correct
    assert total_units == 13                                       
    assert total_revenue == 2100


# Test of funktion - group revenue
from src.metrics import group_revenue


def test_group_revenue_by_city():
    # create sample sales data
    df = pd.DataFrame({
        "city":["Stockholm", 
                "Malmö", 
                "Uppsala", 
                "Malmö", 
                "Uppsala"],
        "revenue":[100, 
                   200, 
                   300, 
                   400, 
                   100]
    })

    # group revenue by city
    result = group_revenue(df, "city")

    # check total revenue and sorting order
    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["city"].tolist() == ["Malmö", "Uppsala", "Stockholm"]


def test_group_revenue_by_date():
    # create sample sales date
    df = pd.DataFrame({
        "date":["2024-04-16", 
                "2024-04-12", 
                "2024-05-16", 
                "2024-04-12", 
                "2024-05-16"],
        "revenue":[100, 
                   200, 
                   300, 
                   400, 
                   100]
    })

    # group revenue by date
    result = group_revenue(df, "date")

    # check total revenue and sorting order
    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["date"].tolist() == ["2024-04-12", "2024-05-16","2024-04-16"]


#group revenue by category
def test_group_revenue_by_category():
    # create sample sales data
    df = pd.DataFrame({
        "category":["Home", "Toys", "Sport", "Toys", "Sport"],
        "revenue":[100, 200, 300, 400, 100]
    })

    # group revenue by category
    result = group_revenue(df, "category")

    # check total revenue and sorting order
    assert result["revenue"].tolist() == [600, 400, 100]
    assert result["category"].tolist() == ["Toys", "Sport", "Home"]

from src.metrics import revenue_by_category
#group revenue by category
def test_revenue_by_category():
    # create sample sales data
    df = pd.DataFrame({
        "category":["Home", "Toys", "Sport", "Toys", "Sport", "Pets"],
        "revenue":[100, 200, 300, 400, 100, 800]
    })

    # group revenue by category
    result = revenue_by_category(df)

    # check total revenue and sorting order
    assert result["revenue"].tolist() == [800, 600, 400, 100]
    assert result["category"].tolist() == ["Pets", "Toys", "Sport", "Home"]


from src.metrics import revenue_top_3_categories
#group revenue by category
def test_revenue_top_3_categories():
    # create sample sales data
    df = pd.DataFrame({
        "category":["Home", "Toys", "Sport", "Toys", "Sport", "Pets"],
        "revenue":[100, 200, 300, 400, 100, 800]
    })

    # group revenue by category
    result = revenue_top_3_categories(df)

    # check total revenue and sorting order
    assert result["revenue"].tolist() == [800, 600, 400]
    assert result["category"].tolist() == ["Pets", "Toys", "Sport"]
    
    
from src.metrics import revenue_by_city
def test_revenue_by_city():
    # create sample sales data
        df = pd.DataFrame({
            "city":["Stockholm", 
                    "Malmö", 
                    "Uppsala", 
                    "Malmö",
                    "Dalby", 
                    "Uppsala"],
            "revenue":[100, 
                       200, 
                       300, 
                       400,
                       50, 
                       100]
        })
    
        # group revenue by city
        result = revenue_by_city(df)
    
        # check total revenue and sorting order
        assert result["revenue"].tolist() == [600, 400, 100, 50]
        assert result["city"].tolist() == ["Malmö", "Uppsala", "Stockholm", "Dalby"]

from src.metrics import revenue_top_3_cities
def test_revenue_top_3_cities():
    # create sample sales data
        df = pd.DataFrame({
            "city":["Stockholm", 
                    "Malmö", 
                    "Uppsala", 
                    "Malmö",
                    "Dalby", 
                    "Uppsala"],
            "revenue":[100, 
                       200, 
                       300, 
                       400,
                       50, 
                       100]
        })
    
        # group revenue by city
        result = revenue_top_3_cities(df)
    
        # check total revenue and sorting order
        assert result["revenue"].tolist() == [600, 400, 100]
        assert result["city"].tolist() == ["Malmö", "Uppsala", "Stockholm"]


from src.metrics import revenue_by_month


def test_revenue_by_month():
     # create sample sales date
         df = pd.DataFrame({
             "date":pd.to_datetime(["2026-10-25", 
                     "2026-01-26", 
                     "2024-10-25", 
                     "2024-01-12", 
                     "2024-01-10",
                     "2024-01-26"]),
             "revenue":[100, 
                        200, 
                        300, 
                        400,
                        50, 
                        100]
         })
     
         # group revenue by date
         result = revenue_by_month(df)
     
         # check total revenue and sorting order
         assert result["revenue"].tolist() == [550, 300, 200, 100]
         assert result["date"].tolist() == ["January 2024", "October 2024","January 2026", "October 2026"]
     
from src.metrics import revenue_by_weekday


def test_revenue_by_weekday():
     # create sample sales date
         df = pd.DataFrame({
             "date":pd.to_datetime([
                     "2026-10-25", 
                     "2026-01-26", 
                     "2024-10-25", 
                     "2024-01-12", 
                     "2024-01-10",
                     "2024-01-26"]),
             "revenue":[100, 
                        200, 
                        300, 
                        400,
                        50, 
                        100]
         })
     
         # group revenue by weekday
         result = revenue_by_weekday(df)
     
         # check total revenue and sorting order
         assert result["revenue"].tolist() == [200, 50, 800, 100]
         assert result["weekday"].tolist() == ["Monday", "Wenedsday","Friday", "Sunday"]
     