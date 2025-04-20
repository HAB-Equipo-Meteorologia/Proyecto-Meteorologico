import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd


def plot_forecast(result_df, predict_start, start_date, end_date):
    fig = go.Figure()

    result_df = result_df[result_df['fecha'] >= start_date]
    result_df = result_df[result_df['fecha'] <= end_date]

    historical = result_df[result_df['fecha'] <= predict_start]
    future = result_df[result_df['fecha'] > predict_start]

    line_width = 2

    fig.add_trace(
        go.Scatter(
            x=historical['fecha'],
            y=historical['historical_tmed'],
            mode='lines',
            line=dict(color='#1F77B4', width=line_width),
            name='Historical Data',
            showlegend=True
        )
    )

    gru_future = future[~future['gru_tmed'].isna()]
    gru_x = [historical['fecha'].iloc[-1]] + list(gru_future['fecha'])
    gru_y = [historical['historical_tmed'].iloc[-1]] + list(gru_future['gru_tmed'])

    lstm_future = future[~future['lstm_tmed'].isna()]
    lstm_x = [historical['fecha'].iloc[-1]] + list(lstm_future['fecha'])
    lstm_y = [historical['historical_tmed'].iloc[-1]] + list(lstm_future['lstm_tmed'])

    simple_rnn_future = future[~future['simple_rnn_tmed'].isna()]
    simple_rnn_x = [historical['fecha'].iloc[-1]] + list(simple_rnn_future['fecha'])
    simple_rnn_y = [historical['historical_tmed'].iloc[-1]] + list(simple_rnn_future['simple_rnn_tmed'])

    fig.add_trace(
        go.Scatter(
            x=gru_x,
            y=gru_y,
            mode='lines',
            line=dict(color='#FF4B4B', width=line_width),
            name='GRU Prediction',
            showlegend=True
        )
    )

    fig.add_trace(
        go.Scatter(
            x=lstm_x,
            y=lstm_y,
            mode='lines',
            line=dict(color='#FFA15A', width=line_width),
            name='LSTM Prediction',
            showlegend=True
        )
    )

    fig.add_trace(
        go.Scatter(
            x=simple_rnn_x,
            y=simple_rnn_y,
            mode='lines',
            line=dict(color='#FFD700', width=line_width),
            name='SimpleRNN Prediction',
            showlegend=True
        )
    )

    prophet_future = future[~future['prop_tmed'].isna()]

    prophet_x = [historical['fecha'].iloc[-1]] + list(prophet_future['fecha'])
    prophet_y = [historical['historical_tmed'].iloc[-1]] + list(prophet_future['prop_tmed'])

    fig.add_trace(
        go.Scatter(
            x=prophet_x,
            y=prophet_y,
            mode='lines',
            line=dict(color='#2CA02C', width=line_width),
            name='Prophet Prediction',
            showlegend=True
        )
    )

    fig.add_vline(x=predict_start, line_width=1, line_dash="dash", line_color="red")

    fig.update_layout(
        title=f'Predicción de Temperatura Media (tmed)',
        xaxis_title='Fecha',
        yaxis_title='Temperatura Media (tmed) (°C)',
        template='plotly_white',
        height=500,
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.4,
            xanchor="center",
            x=0.5
        )
    )

    return fig


def daily_stats_comparison(model_name, daily_stats):
    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        subplot_titles=('Prediccíones Diarias', 'Errores Residuales'),
                        row_heights=[0.7, 0.3],
                        vertical_spacing=0.1)

    fig.add_trace(
        go.Scatter(
            x=daily_stats['fecha'],
            y=daily_stats['actual_mean'],
            mode='lines',
            name='Temperatura Real',
            line=dict(color='blue'),
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=daily_stats['fecha'].tolist() + daily_stats['fecha'].tolist()[::-1],
            y=daily_stats['actual_max'].tolist() + daily_stats['actual_min'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(0, 0, 255, 0.1)',
            line=dict(color='rgba(0, 0, 255, 0)'),
            name='Rango Real (±std)',
            showlegend=True
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=daily_stats['fecha'],
            y=daily_stats['predicted_mean'],
            mode='lines',
            name='Temperatura Predicha',
            line=dict(color='red'),
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=daily_stats['fecha'].tolist() + daily_stats['fecha'].tolist()[::-1],
            y=daily_stats['predicted_max'].tolist() + daily_stats['predicted_min'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(255, 0, 0, 0.1)',
            line=dict(color='rgba(255, 0, 0, 0)'),
            name='Rango Predicho (±std)',
            showlegend=True
        ),
        row=1, col=1
    )

    error = daily_stats['predicted_mean'] - daily_stats['actual_mean']
    fig.add_trace(
        go.Bar(
            x=daily_stats['fecha'],
            y=error,
            name='Error Residual',
            marker=dict(color='red')
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=[daily_stats['fecha'].min(), daily_stats['fecha'].max()],
            y=[0, 0],
            mode='lines',
            line=dict(color='black', dash='dash'),
            showlegend=False
        ),
        row=2, col=1
    )

    mae = np.mean(np.abs(error))
    rmse = np.sqrt(np.mean(error ** 2))

    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.01, y=0.25,
        text=f"MAE: {mae:.2f}°<br>RMSE: {rmse:.2f}°",
        showarrow=False,
        font=dict(size=12),
        align="left",
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="black",
        borderwidth=1,
        borderpad=4
    )

    fig.update_layout(
        title=f'Ánalisis Diario de Predicciones ({model_name})',
        height=700,
        width=1300,
        template='plotly_white',
        legend=dict(
            orientation="h",
            x=1.0,
            y=1.0,
            xanchor='right',
            yanchor='top'
        ),
        xaxis=dict(title='Fecha'),
        xaxis2=dict(title='Fecha'),
        yaxis=dict(title='Temperatura (°C)'),
        yaxis2=dict(title='Error (°C)')
    )

    return fig


def difference_histogram(model_name, difference):
    fig = go.Figure(data=[go.Histogram(
        x=difference,
        nbinsx=50,
        marker=dict(color='skyblue', line=dict(color='black', width=1))
    )])

    fig.update_layout(
        title=f'Histogram of Prediction Differences ({model_name})',
        xaxis_title='Difference (Predicted - Actual)',
        yaxis_title='Frequency',
        template='plotly_white',
        height=500,
        width=1300
    )

    return fig


def training_history(model_name, metrics):
    fig = make_subplots(rows=4, cols=1, subplot_titles=(
    "Error Cuadrático Medio (MSE)", "Error Absoluto Medio (MAE)", "Raíz del Error Cuadrático Medio (RMSE)", "R2 Score"))
    row = 1
    for i, (metric, values) in enumerate([
        ('mse', metrics['loss']),
        ('val_mse', metrics['val_loss']),
        ('mae', metrics['mean_absolute_error']),
        ('val_mae', metrics['val_mean_absolute_error']),
        ('rmse', metrics['root_mean_squared_error']),
        ('val_rmse', metrics['val_root_mean_squared_error']),
        ('r2', metrics['r2_score']),
        ('val_r2', metrics['val_r2_score'])
    ]):
        is_val = 'val' in metric
        fig.add_trace(
            go.Scatter(x=list(range(10)), y=values, name=metric,
                       line=dict(dash='dash' if is_val else None, color='firebrick' if is_val else 'royalblue')),
            row=row, col=1
        )
        if is_val:
            row += 1

    fig.update_layout(
        width=1000,
        height=1200,
        title_text=f"Historial de Entrenamiento ({model_name})",
        legend=dict(
            orientation="h",
            x=1.0,
            y=1.1,
            xanchor='right',
            yanchor='top',
        ),
        template='plotly_white'
    )

    fig.update_xaxes(title_text="Época", row=2, col=1)
    fig.update_yaxes(title_text="Valor", row=2, col=1)

    return fig


def training_history_scaled(model_name, scaled_metrics, metrics):
    fig = go.Figure()

    metric_pairs = [
        ('loss', 'val_loss', 'MSE'),
        ('mean_absolute_error', 'val_mean_absolute_error', 'MAE'),
        ('root_mean_squared_error', 'val_root_mean_squared_error', 'RMSE'),
        ('r2_score', 'val_r2_score', 'R2')
    ]

    colors = {
        'loss': 'blue', 'val_loss': 'lightblue',
        'mean_absolute_error': 'green', 'val_mean_absolute_error': 'lightgreen',
        'root_mean_squared_error': 'red', 'val_root_mean_squared_error': 'pink',
        'r2_score': 'purple', 'val_r2_score': 'violet'
    }

    for train_metric, val_metric, label in metric_pairs:
        fig.add_trace(
            go.Scatter(
                x=list(range(len(scaled_metrics))),
                y=scaled_metrics[train_metric],
                name=f"{label} (Train)",
                line=dict(color=colors[train_metric]),
                hovertemplate=f"{label} (Train): %{{y:.4f}}<br>Original: %{{customdata:.4f}}<extra></extra>",
                customdata=metrics[train_metric]
            )
        )

        fig.add_trace(
            go.Scatter(
                x=list(range(len(scaled_metrics))),
                y=scaled_metrics[val_metric],
                name=f"{label} (Val)",
                line=dict(color=colors[val_metric], dash='dash'),
                hovertemplate=f"{label} (Val): %{{y:.4f}}<br>Original: %{{customdata:.4f}}<extra></extra>",
                customdata=metrics[val_metric]
            )
        )

    fig.update_layout(
        title=f"Historial de Entrenamiento Escalado ({model_name})",
        xaxis_title="Época",
        yaxis_title="Valor Escalado",
        height=600,
        width=1000,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified"
    )

    return fig


def prophet_forecast(forecast_avg):
    fig = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=(
        "Average Forecast with Confidence Interval", "Average Trend Component", "Average Seasonal Components"),
        vertical_spacing=0.1,
        row_heights=[0.5, 0.25, 0.25]
    )

    fig.add_trace(
        go.Scatter(
            x=forecast_avg['ds'],
            y=forecast_avg['yhat'],
            mode='lines',
            name='Average Forecast',
            line=dict(color='blue')
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=pd.concat([forecast_avg['ds'], forecast_avg['ds'].iloc[::-1]]),
            y=pd.concat([forecast_avg['yhat_upper'], forecast_avg['yhat_lower'].iloc[::-1]]),
            fill='toself',
            fillcolor='rgba(0, 176, 246, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% Confidence Interval'
        ),
        row=1, col=1
    )

    actual_points = forecast_avg[forecast_avg['y'].notnull()]

    fig.add_trace(
        go.Scatter(
            x=actual_points['ds'],
            y=actual_points['y'],
            mode='markers',
            name='Actual Values',
            marker=dict(color='black', size=4)
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=forecast_avg['ds'],
            y=forecast_avg['trend'],
            mode='lines',
            name='Average Trend',
            line=dict(color='darkblue')
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=pd.concat([forecast_avg['ds'], forecast_avg['ds'].iloc[::-1]]),
            y=pd.concat([forecast_avg['trend_upper'], forecast_avg['trend_lower'].iloc[::-1]]),
            fill='toself',
            fillcolor='rgba(0, 0, 139, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Trend Confidence Interval',
            showlegend=False
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=forecast_avg['ds'],
            y=forecast_avg['weekly'],
            mode='lines',
            name='Weekly Pattern',
            line=dict(color='green')
        ),
        row=3, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=pd.concat([forecast_avg['ds'], forecast_avg['ds'].iloc[::-1]]),
            y=pd.concat([forecast_avg['weekly_upper'], forecast_avg['weekly_lower'].iloc[::-1]]),
            fill='toself',
            fillcolor='rgba(0, 128, 0, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Weekly Confidence Interval',
            showlegend=False
        ),
        row=3, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=forecast_avg['ds'],
            y=forecast_avg['yearly'],
            mode='lines',
            name='Yearly Pattern',
            line=dict(color='red')
        ),
        row=3, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=pd.concat([forecast_avg['ds'], forecast_avg['ds'].iloc[::-1]]),
            y=pd.concat([forecast_avg['yearly_upper'], forecast_avg['yearly_lower'].iloc[::-1]]),
            fill='toself',
            fillcolor='rgba(255, 0, 0, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Yearly Confidence Interval',
            showlegend=False
        ),
        row=3, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=forecast_avg['ds'],
            y=forecast_avg['additive_terms'],
            mode='lines',
            name='All Seasonal Components',
            line=dict(color='purple')
        ),
        row=3, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=pd.concat([forecast_avg['ds'], forecast_avg['ds'].iloc[::-1]]),
            y=pd.concat([forecast_avg['additive_terms_upper'], forecast_avg['additive_terms_lower'].iloc[::-1]]),
            fill='toself',
            fillcolor='rgba(128, 0, 128, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Seasonal Confidence Interval',
            showlegend=False
        ),
        row=3, col=1
    )

    fig.update_layout(
        title="Prophet Forecast (Daily Average)",
        xaxis_title="Date",
        yaxis_title="Value",
        height=900,
        width=1000,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        template="plotly_white",
    )

    fig.update_yaxes(title_text="Value", row=1, col=1)
    fig.update_yaxes(title_text="Trend", row=2, col=1)
    fig.update_yaxes(title_text="Seasonal Effects", row=3, col=1)

    return fig
