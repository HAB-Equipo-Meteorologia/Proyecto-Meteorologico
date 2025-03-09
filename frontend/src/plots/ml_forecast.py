import plotly.graph_objects as go


def plot_forecast(result_df, predict_start):
    fig = go.Figure()

    # Historical data (including the prediction start date)
    historical = result_df[result_df['fecha'] <= predict_start]

    # Future data
    future = result_df[result_df['fecha'] > predict_start]

    marker_size = 4 if len(historical) < 50 else 0
    line_width = 3 if len(historical) < 50 else 2

    # Base historical line - always shown
    fig.add_trace(
        go.Scatter(
            x=historical['fecha'],
            y=historical['historical_tmed'],
            mode='lines+markers',
            line=dict(color='#1F77B4', width=line_width),
            marker=dict(size=marker_size, color='#1F77B4'),
            name='Historical Data',
            showlegend=True
        )
    )

    gru_future = future[~future['gru_tmed'].isna()]
    # Connect the last historical point with GRU predictions
    gru_x = [historical['fecha'].iloc[-1]] + list(gru_future['fecha'])
    gru_y = [historical['historical_tmed'].iloc[-1]] + list(gru_future['gru_tmed'])

    fig.add_trace(
        go.Scatter(
            x=gru_x,
            y=gru_y,
            mode='lines+markers',
            line=dict(color='#FF4B4B', width=line_width),
            marker=dict(size=marker_size, color='#FF4B4B'),
            name='GRU Prediction',
            showlegend=True
        )
    )

    prophet_future = future[~future['prop_tmed'].isna()]

    # Connect the last historical point with Prophet predictions
    prophet_x = [historical['fecha'].iloc[-1]] + list(prophet_future['fecha'])
    prophet_y = [historical['historical_tmed'].iloc[-1]] + list(prophet_future['prop_tmed'])

    fig.add_trace(
        go.Scatter(
            x=prophet_x,
            y=prophet_y,
            mode='lines+markers',
            line=dict(color='#2CA02C', width=line_width),  # Green color for Prophet
            marker=dict(size=marker_size, color='#2CA02C'),
            name='Prophet Prediction',
            showlegend=True
        )
    )

    # Add vertical line at prediction start
    fig.add_vline(x=predict_start, line_width=1, line_dash="dash", line_color="red")

    # Update layout
    fig.update_layout(
        title=f'Predicción de Temperatura Media (tmed)',
        xaxis_title='Date',
        yaxis_title='Temperatura Media (tmed) (°C)',
        template='plotly_white',
        height=500,
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode='x unified'
    )

    return fig