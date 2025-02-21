from datetime import datetime
import pandas as pd
import numpy as np


def format_fecha(fecha_str: str):
    """
    Formatea una fecha en formato ISO 8601 a un formato más legible.
    :param fecha_str:
    :return:
    """
    meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    dt = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S")
    return f"{dt.day} {meses[dt.month - 1]} {dt.year}"


def convert_latitude(lat):
    # Extract degrees and minutes
    degrees = int(lat[:-5])  # First 4 digits are degrees
    minutes = int(lat[-5:-3])  # Last 2 digits are minutes

    # Convert to decimal degrees
    latitude_decimal = degrees + minutes / 60.0
    if lat[-1] == 'S':  # If South, make negative
        latitude_decimal = -latitude_decimal
    return latitude_decimal


def convert_longitude(lon):
    # Extract degrees and minutes
    degrees = int(lon[:-5])  # First 4 digits are degrees
    minutes = int(lon[-5:-3])  # Last 2 digits are minutes

    # Convert to decimal degrees
    longitude_decimal = degrees + minutes / 60.0
    if lon[-1] == 'W':  # If West, make it negative
        longitude_decimal = -longitude_decimal
    return longitude_decimal


def remove_outliers_tukey(
        df: pd.DataFrame,
        col: str,
        threshold: float = 1.5,
        lq: float = 0.25,
        uq: float = 0.75
) -> pd.DataFrame:
    """
    Remove outliers using Tukey's method (based on IQR).

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame
    col : str
        Column name to check for outliers
    threshold : float, default=1.5
        Multiplier for IQR to determine outlier boundaries
    lq : float, default=0.25
        Lower quantile (typically 0.25 for Q1)
    uq : float, default=0.75
        Upper quantile (typically 0.75 for Q3)

    Returns
    -------
    pandas.DataFrame
        DataFrame with outliers removed
    """
    # Calculate quartiles
    q1 = df[col].quantile(lq)
    q3 = df[col].quantile(uq)

    # Calculate IQR and bounds
    iqr = q3 - q1
    lower_bound = q1 - threshold * iqr
    upper_bound = q3 + threshold * iqr

    # Return filtered DataFrame
    return df[(df[col] >= lower_bound) & (df[col] <= upper_bound)].copy()


def remove_outliers_zscore(df: pd.DataFrame, col: str, threshold: int = 3):
    mean = df[col].mean()
    std = df[col].std()

    return df[abs(df[col] - mean) <= threshold * std]


def calculate_zscore(x, nan_policy='omit'):
    if nan_policy == 'omit':
        x = x[~x.isna()]

    mean = x.mean()
    std = x.std()

    z_scores = (x - mean) / std

    return z_scores


def remove_outliers_zscore_adaptive(
        X: pd.DataFrame,
        y: pd.Series,
        col: str,
        max_threshold: float = 4,
        min_threshold: float = 2,
        sensitivity: float = 0.2
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Removes outliers from a column using an adaptive Z-score threshold.

    The threshold adapts based on the proportion of outliers detected:
    - Starts with max_threshold
    - Adjusts downward based on outlier proportion and sensitivity
    - Won't go below min_threshold

    Parameters
    ----------
    X : pandas.DataFrame
        Input features
    y : pandas.Series
        Target variable
    col : str
        Column name to check for outliers
    max_threshold : float, default=4
        Maximum z-score threshold
    min_threshold : float, default=2
        Minimum z-score threshold
    sensitivity : float, default=0.2
        How quickly threshold adjusts to outlier proportion

    Returns
    -------
    tuple[pd.DataFrame, pd.Series]
        Filtered X and y with outliers removed

    Raises
    ------
    ValueError
        If thresholds are invalid or column doesn't exist
    """
    # Input validation
    if min_threshold >= max_threshold:
        raise ValueError("min_threshold must be less than max_threshold")
    if sensitivity <= 0:
        raise ValueError("sensitivity must be positive")
    if col not in X.columns:
        raise ValueError(f"Column '{col}' not found in DataFrame")
    if len(X) != len(y):
        raise ValueError("X and y must have same length")

    # Calculate z-scores
    z_scores = calculate_zscore(X[col])
    abs_z_scores = np.abs(z_scores)

    # Calculate initial outlier ratio using max threshold
    outlier_mask = abs_z_scores > max_threshold
    outlier_ratio = outlier_mask.mean()

    # Adjust threshold based on outlier ratio and sensitivity
    adjusted_threshold = max(
        min_threshold,
        max_threshold - (outlier_ratio / sensitivity)
    )

    # Apply final mask
    mask = abs_z_scores <= adjusted_threshold

    # Ensure X and y maintain index alignment
    X_filtered = X.loc[mask].copy()
    y_filtered = y.loc[mask].copy()

    return X_filtered, y_filtered


def remove_nans(
        df: pd.DataFrame,
        threshold: float = 0.1,
        fill_with: str = 'drop',
        value: any = None
) -> pd.DataFrame:
    """
    Clean NaN values in a DataFrame based on threshold and filling strategy.

    For each column, if the percentage of NaN values exceeds the threshold,
    applies the specified filling strategy. Otherwise, keeps the NaN values.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame to clean
    threshold : float, default 0.1
        Maximum allowed proportion of NaN values in a column (0 to 1)
    fill_with : str, default 'drop'
        Strategy to handle NaN values. Options:
        - 'drop': Remove rows with NaN values
        - 'mean': Fill with column mean (numeric only)
        - 'median': Fill with column median (numeric only)
        - 'mode': Fill with column mode
        - 'value': Fill with specified value parameter
    value : any, default None
        Value to use when fill_with='value'

    Returns
    -------
    pandas.DataFrame
        Cleaned DataFrame with NaN values handled according to parameters

    Raises
    ------
    ValueError
        If threshold is not between 0 and 1
        If fill_with is not one of the allowed options
        If fill_with='value' but no value is provided
    """
    # Validate inputs
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1")

    valid_methods = {'drop', 'mean', 'median', 'mode', 'value'}
    if fill_with not in valid_methods:
        raise ValueError(f"fill_with must be one of {valid_methods}")

    if fill_with == 'value' and value is None:
        raise ValueError("Must provide value when fill_with='value'")

    # Create a copy to avoid modifying original
    df_clean = df.copy()

    fill_methods = {
        'mean': lambda x: x.mean(),
        'median': lambda x: x.median(),
        'mode': lambda x: x.mode().iloc[0] if not x.mode().empty else None,
        'value': lambda x: value
    }

    for column in df_clean.columns:
        nan_proportion = df_clean[column].isna().mean()

        if nan_proportion > threshold:
            if fill_with == 'drop':
                df_clean = df_clean.dropna(subset=[column])
                continue

            # Handle numeric columns
            if pd.api.types.is_numeric_dtype(df_clean[column]):
                fill_value = fill_methods[fill_with](df_clean[column])
                df_clean[column] = df_clean[column].fillna(fill_value)
            # Handle non-numeric columns
            else:
                if fill_with == 'mode' or fill_with == 'value':
                    fill_value = fill_methods[fill_with](df_clean[column])
                    df_clean[column] = df_clean[column].fillna(fill_value)
                else:
                    df_clean = df_clean.dropna(subset=[column])

    return df_clean
