import joblib
import numpy as np
import pandas as pd
from app.db import engine

async def get_historical_data():
    query_df_product_view_events = '''
    SELECT variant_id, click_counting as view, event_time
    FROM product_events
    WHERE event_type = 'view'
    '''
    df_view = pd.read_sql(query_df_product_view_events, engine)
    df_view['event_time'] = pd.to_datetime(df_view['event_time'])
    df_view['year'] = df_view['event_time'].dt.year
    df_view['quarter'] = df_view['event_time'].dt.quarter
    df_view = df_view.groupby(['variant_id', 'year', 'quarter'])['view'].sum().reset_index()

    query_df_product_add_to_cart_events = '''
    SELECT variant_id, click_counting as add_to_cart, event_time
    FROM product_events
    WHERE event_type = 'add_to_cart'
    '''
    df_cart = pd.read_sql(query_df_product_add_to_cart_events, engine)
    df_cart['event_time'] = pd.to_datetime(df_cart['event_time'])
    df_cart['year'] = df_cart['event_time'].dt.year
    df_cart['quarter'] = df_cart['event_time'].dt.quarter 

    df_cart = df_cart.groupby(['variant_id', 'year', 'quarter'])['add_to_cart'].sum().reset_index()

    query = '''
    SELECT variant_id, quantity as orderquantity, price as unitprice, total_price as sales, created_at
    FROM orderitems
    JOIN orders ON orderitems.order_id = orders.order_id
    '''
    df_orders = pd.read_sql(query, engine)
    df_orders['created_at'] = pd.to_datetime(df_orders['created_at'])
    df_orders['year'] = df_orders['created_at'].dt.year
    df_orders['quarter'] = df_orders['created_at'].dt.quarter 

    # Groupby theo variant_id, year, VÀ quarter
    df_orders = df_orders.groupby(['variant_id', 'year', 'quarter']).agg({
        "orderquantity": "sum",
        "unitprice": "mean",
        "sales": "sum"       
    }).reset_index()
    df = (
        df_orders
        .merge(df_view, on=['variant_id', 'year', 'quarter'], how='outer')
        .merge(df_cart, on=['variant_id', 'year', 'quarter'], how='outer')
        .fillna(0)
    )
    
    df = df.sort_values(['variant_id', 'year', 'quarter'])

    df['best_seller_of_quarter'] = ( # <-- Đã sửa tên biến
        df.groupby(['year', 'quarter'])['orderquantity']
          .transform(lambda x: (x == x.max()).astype(int))
    )

    df['orderquantity_next_quarter'] = df.groupby('variant_id')['orderquantity'].shift(-1)
    df['view_next_quarter'] = df.groupby('variant_id')['view'].shift(-1)
    df['add_to_cart_next_quarter'] = df.groupby('variant_id')['add_to_cart'].shift(-1)
    df['best_seller_next_quarter'] = df.groupby('variant_id')['best_seller_of_quarter'].shift(-1) # <-- Biến mới

    df['add_to_cart_rate'] = np.where(df["view"] > 0, df["add_to_cart"] / df["view"], 0)
    df["cart_to_order_rate"] = np.where(df["add_to_cart"] > 0, df["orderquantity"] / df["add_to_cart"], 0)
    df["conversion_rate"] = np.where(df["view"] > 0, df["orderquantity"] / df["view"], 0)
    
    df["aov"] = np.where(df["orderquantity"] > 0, df["sales"] / df["orderquantity"], 0)

    # Tỷ lệ tăng trưởng (Growth rates)
    df["order_growth"] = np.where(df["orderquantity"] > 0, df["orderquantity_next_quarter"] / df["orderquantity"], 0)
    df["view_growth"] = np.where(df["view"] > 0, df["view_next_quarter"] / df["view"], 0)
    df["add_to_cart_growth"] = np.where(df["add_to_cart"] > 0, df["add_to_cart_next_quarter"] / df["add_to_cart"], 0)


    # Biến trễ (Lag features) - Cấp độ Quý
    df["orderquantity_lag_1"] = df.groupby("variant_id")["orderquantity"].shift(1)
    df["orderquantity_lag_2"] = df.groupby("variant_id")["orderquantity"].shift(2)
    df["orderquantity_lag_3"] = df.groupby("variant_id")["orderquantity"].shift(3)

    df["view_lag_1"] = df.groupby("variant_id")["view"].shift(1)
    df["add_to_cart_lag_1"] = df.groupby("variant_id")["add_to_cart"].shift(1)
    df["aov_lag_1"] = df.groupby("variant_id")["aov"].shift(1)

    # Trung bình trượt (Rolling windows) - Chuyển _m_avg -> _q_avg
    df["order_3q_avg"] = df.groupby("variant_id")["orderquantity"].rolling(3).mean().reset_index(level=0, drop=True)
    df["order_6q_avg"] = df.groupby("variant_id")["orderquantity"].rolling(6).mean().reset_index(level=0, drop=True)
    df["view_3q_avg"] = df.groupby("variant_id")["view"].rolling(3).mean().reset_index(level=0, drop=True)
    df["add_to_cart_3q_avg"] = df.groupby("variant_id")["add_to_cart"].rolling(3).mean().reset_index(level=0, drop=True)

    # Fill remaining NaN after lag/rolling (chủ yếu là NaN từ shift/rolling ở các quý đầu)
    df = df.fillna(0)
    df2 = pd.read_csv("app/data/base_dataset.csv")
    df += df2
    df = pd.concat([df2, df], ignore_index=True)
    df.to_csv("app/data/base_dataset.csv")
    return df


MODEL_PATH = "app/data/model.pkl"

async def save_trained_model(model):
    joblib.dump(model, MODEL_PATH)
