import logging
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from app.features.schedule_training.model import model
import numpy as np

logger = logging.getLogger(__name__)

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

def train_model(data):
    X = data[FEATURES]
    y = data["orderquantity_next_quarter"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=True, random_state=42
    )

    model.fit(
        X_train, 
        y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        verbose=True
    )

    # Prediction
    pred = model.predict(X_test)

    # Evaluation metrics
    mae = mean_absolute_error(y_test, pred)
    mse = mean_squared_error(y_test, pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, pred)
    medae = median_absolute_error(y_test, pred)

    # MAPE (Mean Absolute Percentage Error)
    mape = np.mean(np.abs((y_test - pred) / y_test)) * 100

    # SMAPE (Symmetric MAPE)
    smape = np.mean(2 * np.abs(y_test - pred) / (np.abs(y_test) + np.abs(pred))) * 100

    # Print results
    print("MAE:", mae)
    print("MSE:", mse)
    print("RMSE:", rmse)
    print("R² Score:", r2)
    print("Median AE:", medae)
    print("MAPE (%):", mape)
    print("SMAPE (%):", smape)
    logger.info("Model evaluation results:")
    logger.info("MAE: %.6f", mae)
    logger.info("MSE: %.6f", mse)
    logger.info("RMSE: %.6f", rmse)
    logger.info("R² Score: %.6f", r2)
    logger.info("Median AE: %.6f", medae)
    logger.info("MAPE (%%): %.2f", mape)
    logger.info("SMAPE (%%): %.2f", smape)

    return model
