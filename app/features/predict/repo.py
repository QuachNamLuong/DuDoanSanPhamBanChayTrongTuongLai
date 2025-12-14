# app/features/predict/repository.py
import pandas as pd
from app.db import engine

def load_views_quarter():
    query = """
        SELECT variant_id, click_counting AS view, event_time
        FROM product_events
        WHERE event_type = 'view'
    """
    df = pd.read_sql(query, engine)
    df["event_time"] = pd.to_datetime(df["event_time"])
    df["year"] = df["event_time"].dt.year
    df["quarter"] = df["event_time"].dt.quarter
    return df.groupby(["variant_id", "year", "quarter"])["view"].sum().reset_index()


def load_add_to_cart_quarter():
    query = """
        SELECT variant_id, click_counting AS add_to_cart, event_time
        FROM product_events
        WHERE event_type = 'add_to_cart'
    """
    df = pd.read_sql(query, engine)
    df["event_time"] = pd.to_datetime(df["event_time"])
    df["year"] = df["event_time"].dt.year
    df["quarter"] = df["event_time"].dt.quarter
    return df.groupby(["variant_id", "year", "quarter"])["add_to_cart"].sum().reset_index()


def load_orders_quarter():
    query = """
        SELECT variant_id, quantity AS orderquantity, price AS unitprice,
               total_price AS sales, created_at
        FROM orderitems
        JOIN orders ON orderitems.order_id = orders.order_id
    """
    df = pd.read_sql(query, engine)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["year"] = df["created_at"].dt.year
    df["quarter"] = df["created_at"].dt.quarter

    return df.groupby(["variant_id", "year", "quarter"]).agg({
        "orderquantity": "sum",
        "unitprice": "mean",
        "sales": "sum"
    }).reset_index()
