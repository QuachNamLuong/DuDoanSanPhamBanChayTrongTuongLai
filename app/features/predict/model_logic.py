# app/features/predict/model_logic.py
import numpy as np

def build_features(df_orders, df_view, df_cart):
    df = (
        df_orders
        .merge(df_view, on=["variant_id", "year", "quarter"], how="outer")
        .merge(df_cart, on=["variant_id", "year", "quarter"], how="outer")
        .fillna(0)
        .sort_values(["variant_id", "year", "quarter"])
    )

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

    return df.fillna(0)
