
import pandas as pd

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
    