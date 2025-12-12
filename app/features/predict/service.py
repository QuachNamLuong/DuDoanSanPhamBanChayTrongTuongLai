import joblib
import pandas as pd
from .schemas import PredictRequest
from app.db import engine

# MODEL_PATH = "model/xgb_model.pkl"
# model = joblib.load(MODEL_PATH)

def predict_next_month():
    query = '''
    SELECT variant_id, price_at_event as unitprice, click_counting as view, event_time, event_type
    FROM `product_events`
    WHERE event_type = 'view'
    '''
    df_product_view_events = pd.read_sql(query, engine)
    df_product_view_events['event_time'] = pd.to_datetime(df_product_view_events['event_time'])
    df_product_view_events['year'] = df_product_view_events['event_time'].dt.year
    df_product_view_events['month'] = df_product_view_events['event_time'].dt.month
    df_product_view_events = df_product_view_events.groupby(['variant_id','year', 'month']).agg({
        'view': 'sum',
    })

    
    
