import numpy as np

def create_sequences(X, y, dates, n_days=7):
    X_seq, y_seq, dates_seq = [], [], []

    for i in range(n_days, len(X)):
        X_seq.append(X.iloc[i - n_days:i].values)
        y_seq.append(y.iloc[i])
        dates_seq.append(dates[i])

    X_seq = np.array(X_seq)
    y_seq = np.array(y_seq)

    return X_seq, y_seq, dates_seq