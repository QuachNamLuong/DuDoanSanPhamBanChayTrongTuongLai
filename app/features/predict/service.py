# app/features/predict/service.py
from .repo import (
    load_views_quarter, load_add_to_cart_quarter, load_orders_quarter
)
from .model_logic import build_features
import joblib

FEATURES = [
    # Cấp độ thời gian
    "year",
    "quarter", # Thêm cột 'quarter' nếu bạn muốn nắm bắt tính mùa vụ

    # Giá trị của Quý hiện tại (t)
    "orderquantity",  # Đã sửa
    "unitprice",
    "view",
    "sales",          # Đã sửa (nên là SALES nếu có)
    "add_to_cart",
    "add_to_cart_rate",
    "cart_to_order_rate",
    "conversion_rate",
    "aov",

    # Biến tăng trưởng (Growth features)
    # Các biến này cũng là biến hiện tại (t) được tính từ t+1 / t
    "order_growth",
    "view_growth",
    "add_to_cart_growth",

    # Biến trễ (Lag features) - Quý trước đó (t-1, t-2, t-3)
    "orderquantity_lag_1", # Đây là tên bạn đã sử dụng cho ORDERQUANTITY trễ
    "orderquantity_lag_2",
    "orderquantity_lag_3",
    "view_lag_1",
    "add_to_cart_lag_1",
    "aov_lag_1",


    # Trung bình trượt (Rolling windows) - Đã sửa tên biến cho phù hợp với quý (q)
    "order_3q_avg",
    "order_6q_avg",
    "view_3q_avg",
    "add_to_cart_3q_avg"
]

def predict_next_quarter():
    df_view = load_views_quarter()
    df_cart = load_add_to_cart_quarter()
    df_orders = load_orders_quarter()

    df = build_features(df_orders, df_view, df_cart)

    latest_year = df["year"].max()
    latest_quarter = df[df["year"] == latest_year]["quarter"].max()

    df_latest = df[(df["year"] == latest_year) & (df["quarter"] == latest_quarter)]

    model = joblib.load("app/data/model.pkl")

    df_latest["predicted_order_next_quarter"] = model.predict(df_latest[FEATURES])

    return df_latest[["variant_id", "predicted_order_next_quarter"]].to_dict(orient="records")
