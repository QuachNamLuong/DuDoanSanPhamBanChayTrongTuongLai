from fastapi import APIRouter
import pandas as pd
import numpy as np
from app.db import engine
import joblib

pd.options.mode.copy_on_write = True 

router = APIRouter()

@router.get("/predict")
def predict(): # Thêm 'engine' vào tham số nếu cần
    # ======================
    # 1. LOAD PRODUCT VIEW & AGGREGATE TO QUARTERLY
    # ======================
    query_df_product_view_events = '''
    SELECT variant_id, click_counting as view, event_time
    FROM product_events
    WHERE event_type = 'view'
    '''
    df_view = pd.read_sql(query_df_product_view_events, engine)
    df_view['event_time'] = pd.to_datetime(df_view['event_time'])
    df_view['year'] = df_view['event_time'].dt.year
    df_view['quarter'] = df_view['event_time'].dt.quarter # <-- Đã sửa: trích xuất QUÝ

    # Groupby theo variant_id, year, VÀ quarter
    df_view = df_view.groupby(['variant_id', 'year', 'quarter'])['view'].sum().reset_index()

    # ======================
    # 2. LOAD ADD TO CART & AGGREGATE TO QUARTERLY
    # ======================
    query_df_product_add_to_cart_events = '''
    SELECT variant_id, click_counting as add_to_cart, event_time
    FROM product_events
    WHERE event_type = 'add_to_cart'
    '''
    df_cart = pd.read_sql(query_df_product_add_to_cart_events, engine)
    df_cart['event_time'] = pd.to_datetime(df_cart['event_time'])
    df_cart['year'] = df_cart['event_time'].dt.year
    df_cart['quarter'] = df_cart['event_time'].dt.quarter # <-- Đã sửa: trích xuất QUÝ

    # Groupby theo variant_id, year, VÀ quarter
    df_cart = df_cart.groupby(['variant_id', 'year', 'quarter'])['add_to_cart'].sum().reset_index()

    # ======================
    # 3. LOAD ORDERS & AGGREGATE TO QUARTERLY
    # ======================
    query = '''
    SELECT variant_id, quantity as orderquantity, price as unitprice, total_price as sales, created_at
    FROM orderitems
    JOIN orders ON orderitems.order_id = orders.order_id
    '''
    df_orders = pd.read_sql(query, engine)
    df_orders['created_at'] = pd.to_datetime(df_orders['created_at'])
    df_orders['year'] = df_orders['created_at'].dt.year
    df_orders['quarter'] = df_orders['created_at'].dt.quarter # <-- Đã sửa: trích xuất QUÝ

    # Groupby theo variant_id, year, VÀ quarter
    df_orders = df_orders.groupby(['variant_id', 'year', 'quarter']).agg({
        "orderquantity": "sum",
        "unitprice": "mean", # Giá trung bình trên mỗi quý
        "sales": "sum"       # Tổng doanh số trên mỗi quý
    }).reset_index()

    # ======================
    # MERGE DATA
    # ======================
    df = (
        df_orders
        # Merge dựa trên 'variant_id', 'year', VÀ 'quarter'
        .merge(df_view, on=['variant_id', 'year', 'quarter'], how='outer')
        .merge(df_cart, on=['variant_id', 'year', 'quarter'], how='outer')
        .fillna(0)
    )
    
    # Sắp xếp theo chuỗi thời gian (variant_id, year, quarter)
    df = df.sort_values(['variant_id', 'year', 'quarter'])

    # ======================
    # FEATURE ENGINEERING (Chuyển từ tháng sang quý)
    # ======================
    
    # Tính toán cột best_seller_of_quarter trước
    df['best_seller_of_quarter'] = ( # <-- Đã sửa tên biến
        df.groupby(['year', 'quarter'])['orderquantity']
          .transform(lambda x: (x == x.max()).astype(int))
    )

    # Biến mục tiêu và biến rò rỉ (Chuyển _next_month -> _next_quarter)
    df['orderquantity_next_quarter'] = df.groupby('variant_id')['orderquantity'].shift(-1)
    df['view_next_quarter'] = df.groupby('variant_id')['view'].shift(-1)
    df['add_to_cart_next_quarter'] = df.groupby('variant_id')['add_to_cart'].shift(-1)
    df['best_seller_next_quarter'] = df.groupby('variant_id')['best_seller_of_quarter'].shift(-1) # <-- Biến mới

    # Tránh chia cho 0 và thay thế NaN/Inf bằng 0 sau các phép chia
    # Sử dụng np.where để thay thế 0 trước khi chia
    
    # Tỷ lệ chuyển đổi
    df['add_to_cart_rate'] = np.where(df["view"] > 0, df["add_to_cart"] / df["view"], 0)
    df["cart_to_order_rate"] = np.where(df["add_to_cart"] > 0, df["orderquantity"] / df["add_to_cart"], 0)
    df["conversion_rate"] = np.where(df["view"] > 0, df["orderquantity"] / df["view"], 0)
    
    # AOV
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

    # ======================
    # CHỈ GIỮ DỮ LIỆU CỦA QUÝ GẦN NHẤT
    # ======================
    latest_year = df["year"].max()
    # Tìm quý lớn nhất trong năm lớn nhất
    latest_quarter = df[df["year"] == latest_year]["quarter"].max()

    df_latest = df[(df["year"] == latest_year) & (df["quarter"] == latest_quarter)]

    # ======================
    # MODEL PREDICT
    # ======================
    features = [
        # time
        "year",
        "quarter", # <-- Đã sửa: dùng 'quarter' thay 'month'
        
        # current quarter
        "orderquantity",
        "unitprice",
        "view",
        "sales",
        "add_to_cart",
        "best_seller_of_quarter", # <-- Đã sửa
        "add_to_cart_rate",
        "cart_to_order_rate",
        "conversion_rate",
        "aov",

        # growth features
        "order_growth",
        "view_growth",
        "add_to_cart_growth",

        # lag features
        "orderquantity_lag_1",
        "orderquantity_lag_2",
        "orderquantity_lag_3",
        "view_lag_1",
        "add_to_cart_lag_1",
        "aov_lag_1",


        # rolling windows
        "order_3q_avg",  # <-- Đã sửa
        "order_6q_avg",  # <-- Đã sửa
        "view_3q_avg",   # <-- Đã sửa
        "add_to_cart_3q_avg" # <-- Đã sửa
    ]

    # Kiểm tra sự tồn tại của mô hình
    try:
        model = joblib.load("app/api/model.pkl")
    except FileNotFoundError:
        return {"error": "Model file not found. Ensure 'model.pkl' exists at the specified path."}

    X = df_latest[features]
    pred = model.predict(X)

    # <-- Đã sửa tên cột dự đoán
    df_latest["predicted_order_next_quarter"] = pred

    # ======================
    # RETURN RESULT
    # ======================
    return df_latest[["variant_id", "predicted_order_next_quarter"]].to_dict(orient="records")

# from fastapi import APIRouter
# import pandas as pd
# from app.db import engine
# import joblib

# pd.options.mode.copy_on_write = True 

# router = APIRouter()

# @router.get("/health", tags=["Health"])
# def health_check():
#     return {"status": "ok", "message": "API is running"}


# @router.get("/predict")
# def predict():
#     # ======================
#     # 1. LOAD PRODUCT VIEW
#     # ======================
#     query_df_product_view_events = '''
#     SELECT variant_id, price_at_event as unitprice, click_counting as view, event_time
#     FROM product_events
#     WHERE event_type = 'view'
#     '''
#     df_view = pd.read_sql(query_df_product_view_events, engine)
#     df_view['event_time'] = pd.to_datetime(df_view['event_time'])
#     df_view['year'] = df_view['event_time'].dt.year
#     df_view['month'] = df_view['event_time'].dt.month

#     df_view = df_view.groupby(['variant_id', 'year', 'month'])['view'].sum().reset_index()

#     # ======================
#     # 2. LOAD ADD TO CART
#     # ======================
#     query_df_product_add_to_cart_events = '''
#     SELECT variant_id, price_at_event as unitprice, click_counting as add_to_cart, event_time
#     FROM product_events
#     WHERE event_type = 'add_to_cart'
#     '''
#     df_cart = pd.read_sql(query_df_product_add_to_cart_events, engine)
#     df_cart['event_time'] = pd.to_datetime(df_cart['event_time'])
#     df_cart['year'] = df_cart['event_time'].dt.year
#     df_cart['month'] = df_cart['event_time'].dt.month

#     df_cart = df_cart.groupby(['variant_id', 'year', 'month'])['add_to_cart'].sum().reset_index()

#     # ======================
#     # 3. LOAD ORDERS
#     # ======================
#     query = '''
#     SELECT variant_id, quantity as orderquantity, price as unitprice, total_price as sales, created_at
#     FROM orderitems
#     JOIN orders ON orderitems.order_id = orders.order_id
#     '''
#     df_orders = pd.read_sql(query, engine)
#     df_orders['created_at'] = pd.to_datetime(df_orders['created_at'])
#     df_orders['year'] = df_orders['created_at'].dt.year
#     df_orders['month'] = df_orders['created_at'].dt.month

#     df_orders = df_orders.groupby(['variant_id', 'year', 'month']).agg({
#         "orderquantity": "sum",
#         "unitprice": "mean",
#         "sales": "mean"
#     }).reset_index()

#     # ======================
#     # MERGE DATA
#     # ======================
#     df = (
#         df_orders
#         .merge(df_view, on=['variant_id', 'year', 'month'], how='outer')
#         .merge(df_cart, on=['variant_id', 'year', 'month'], how='outer')
#         .fillna(0)
#         .sort_values(['variant_id', 'year', 'month'])
#     )

#     # ======================
#     # FEATURE ENGINEERING
#     # ======================
#     df['best_seller_of_month'] = (
#         df.groupby(['year', 'month'])['orderquantity']
#           .transform(lambda x: (x == x.max()).astype(int))
#     )

#     df['orderquantity_next_month'] = df.groupby('variant_id')['orderquantity'].shift(-1)
#     df['view_next_month'] = df.groupby('variant_id')['view'].shift(-1)
#     df['add_to_cart_next_month'] = df.groupby('variant_id')['add_to_cart'].shift(-1)

#     # Avoid divide-by-zero
#     df['add_to_cart_rate'] = df["add_to_cart"] / df["view"].replace(0, 1)
#     df["cart_to_order_rate"] = df["orderquantity"] / df["add_to_cart"].replace(0, 1)
#     df["conversion_rate"] = df["orderquantity"] / df["view"].replace(0, 1)
#     df["aov"] = df["sales"] / df["orderquantity"].replace(0, 1)

#     df["order_growth"] = df["orderquantity_next_month"] / df["orderquantity"].replace(0, 1)
#     df["view_growth"] = df["view_next_month"] / df["view"].replace(0, 1)
#     df["add_to_cart_growth"] = df["add_to_cart_next_month"] / df["add_to_cart"].replace(0, 1)

#     df["orderquantity_lag_1"] = df.groupby("variant_id")["orderquantity"].shift(1)
#     df["orderquantity_lag_2"] = df.groupby("variant_id")["orderquantity"].shift(2)
#     df["orderquantity_lag_3"] = df.groupby("variant_id")["orderquantity"].shift(3)

#     df["view_lag_1"] = df.groupby("variant_id")["view"].shift(1)
#     df["add_to_cart_lag_1"] = df.groupby("variant_id")["add_to_cart"].shift(1)
#     df["aov_lag_1"] = df.groupby("variant_id")["aov"].shift(1)

#     df["order_3m_avg"] = df.groupby("variant_id")["orderquantity"].rolling(3).mean().reset_index(level=0, drop=True)
#     df["order_6m_avg"] = df.groupby("variant_id")["orderquantity"].rolling(6).mean().reset_index(level=0, drop=True)
#     df["view_3m_avg"] = df.groupby("variant_id")["view"].rolling(3).mean().reset_index(level=0, drop=True)
#     df["add_to_cart_3m_avg"] = df.groupby("variant_id")["add_to_cart"].rolling(3).mean().reset_index(level=0, drop=True)

#     # Fill remaining NaN after lag/rolling
#     df = df.fillna(0)

#     # ======================
#     # CHỈ GIỮ DỮ LIỆU THÁNG GẦN NHẤT
#     # ======================
#     latest_year = df["year"].max()
#     latest_month = df[df["year"] == latest_year]["month"].max()

#     df_latest = df[(df["year"] == latest_year) & (df["month"] == latest_month)]

#     # ======================
#     # MODEL PREDICT
#     # ======================
#     features = [
#         "year","month","orderquantity","unitprice","view","sales","add_to_cart",
#         "best_seller_of_month","add_to_cart_rate","cart_to_order_rate","conversion_rate","aov",
#         "order_growth","view_growth","add_to_cart_growth",
#         "orderquantity_lag_1","orderquantity_lag_2","orderquantity_lag_3",
#         "view_lag_1","add_to_cart_lag_1","aov_lag_1",
#         "order_3m_avg","order_6m_avg","view_3m_avg","add_to_cart_3m_avg"
#     ]

#     model = joblib.load("app/api/model.pkl")

#     X = df_latest[features]
#     pred = model.predict(X)

#     df_latest["predicted_order_next_month"] = pred

#     # ======================
#     # RETURN RESULT
#     # ======================
#     return df_latest[["variant_id", "predicted_order_next_month"]].to_dict(orient="records")
