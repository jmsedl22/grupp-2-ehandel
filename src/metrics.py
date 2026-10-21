
#count the total number of orders

def count_orders(df):
    count_orders = df["order_id"].nunique()       # nuninque - to avoid counting duplicates
    return count_orders                           # return the total number of orders