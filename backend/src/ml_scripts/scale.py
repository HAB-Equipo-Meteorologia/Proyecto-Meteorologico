import pandas as pd


def scale_df(df: pd.DataFrame, scaler_X, scaler_y) -> pd.DataFrame:

    df_unscaled = df.copy()
    
    target = 'tmed'
    ignore_cols = ['fecha_sin', 'fecha_cos']
    
    X_scale_cols = list(df_unscaled.drop(columns=ignore_cols + [target]).columns)
    y_scale_cols = [target]

    X_scaled = scaler_X.transform(df_unscaled[X_scale_cols].values)
    y_scaled = scaler_y.transform(df_unscaled[y_scale_cols].values)
    
    df_scaled = pd.DataFrame(X_scaled, columns=df_unscaled[X_scale_cols].columns)
    df_scaled[target] = y_scaled

    df_scaled[ignore_cols] = df_unscaled[ignore_cols].values
    df_scaled = df_scaled[df_unscaled.columns]

    numeric_cols = ['fecha_sin', 'fecha_cos']
    df_scaled[numeric_cols] = df_scaled[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df_scaled.index = df_unscaled.index

    return df_scaled.round(4)
