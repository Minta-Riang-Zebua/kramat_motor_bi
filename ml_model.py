import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

FEATURES = ['Harga', 'Stok', 'bulan', 'tahun', 'lag_1', 'lag_2', 'lag_3']

def add_lags(df):
    d = df.sort_values(['id_produk', 'periode_date']).copy()
    d['lag_1'] = d.groupby('id_produk')['Terjual'].shift(1)
    d['lag_2'] = d.groupby('id_produk')['Terjual'].shift(2)
    d['lag_3'] = d.groupby('id_produk')['Terjual'].shift(3)
    return d

def prepare_data(df):
    d = df.copy()
    d['periode_date'] = pd.to_datetime(d['periode_date'])
    d['bulan'] = d['periode_date'].dt.month
    d['tahun'] = d['periode_date'].dt.year
    d = add_lags(d)
    return d.dropna(subset=['lag_1', 'lag_2', 'lag_3'])

def train_evaluate(df):
    processed = prepare_data(df)
    train = processed[processed['periode_date'] < '2026-01-01']
    test = processed[processed['periode_date'] >= '2026-01-01']
    
    if train.empty or test.empty:
        train = processed.iloc[:int(len(processed)*0.8)]
        test = processed.iloc[int(len(processed)*0.8):]

    X_train, y_train = train[FEATURES], train['Terjual']
    X_test, y_test = test[FEATURES], test['Terjual']

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    test_eval = test.copy()
    test_eval['prediksi'] = preds

    metrics = {
        'MAE': mean_absolute_error(y_test, preds),
        'RMSE': float(np.sqrt(mean_squared_error(y_test, preds))),
        'R2': r2_score(y_test, preds)
    }
    return model, processed, train, test_eval, metrics

def fit_full(df):
    processed = prepare_data(df)
    X, y = processed[FEATURES], processed['Terjual']
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model, processed

def next_month_forecast(df, model=None):
    if model is None:
        model, _ = fit_full(df)
    
    latest_date = pd.to_datetime(df['periode_date'].max())
    target_date = latest_date + pd.DateOffset(months=1)
    
    latest_records = df.sort_values('periode_date').groupby('id_produk').last().reset_index()
    
    forecasts = []
    for _, row in latest_records.iterrows():
        pid = row['id_produk']
        prod_history = df[df['id_produk'] == pid].sort_values('periode_date', ascending=False)
        
        lag_1 = prod_history.iloc[0]['Terjual'] if len(prod_history) >= 1 else 0
        lag_2 = prod_history.iloc[1]['Terjual'] if len(prod_history) >= 2 else lag_1
        lag_3 = prod_history.iloc[2]['Terjual'] if len(prod_history) >= 3 else lag_2
        
        feat_row = {
            'Harga': row['Harga'],
            'Stok': row['Stok'],
            'bulan': target_date.month,
            'tahun': target_date.year,
            'lag_1': lag_1,
            'lag_2': lag_2,
            'lag_3': lag_3
        }
        
        pred = model.predict(pd.DataFrame([feat_row]))[0]
        
        forecasts.append({
            'id_produk': pid,
            'Produk': row['Produk'],
            'Kategori': row['Kategori'],
            'Harga': row['Harga'],
            'Stok': row['Stok'],
            'lag_1': lag_1,
            'lag_2': lag_2,
            'lag_3': lag_3,
            'hasil_prediksi': max(0, round(pred))
        })
        
    return pd.DataFrame(forecasts), target_date
