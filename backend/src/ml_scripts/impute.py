import pandas as pd
import os
import sys
sys.path.append('../../..')
from common.config import script_dir


_lookup_dir = os.path.join(script_dir, '../data/locations/estacion_distance_lookup.csv')
_lookup = pd.read_csv(_lookup_dir)


def impute_knn(df, k=3):  

    # Create a copy to avoid modifying the original
    df_imputed = df.copy()

    for col in ['tmed', 'tmax', 'tmin', 'prec', 'hr_media', 'hr_max']:
        
        # Iterate through each day
        for fecha in df_imputed['fecha'].unique():
            current_row = df_imputed[df_imputed['fecha'] == fecha]
    
            # Filter NaN and non NaN rows
            nan_rows = current_row[current_row[col].isna()]
            non_nan_rows = current_row[current_row[col].notna()]
    
            for index, row in nan_rows.iterrows():
                
                # Use the nearest k stations to take the average
                nearest_idemas = _lookup[row['idema']]
                nearest_values = non_nan_rows[non_nan_rows['idema'].isin(nearest_idemas)][col][:k]
    
                if not nearest_values.empty:
                    imputed_value = nearest_values.mean()
                    df_imputed.loc[index, col] = imputed_value

    df_imputed = df_imputed.drop(columns=['idema'])

    return df_imputed.round(4)
