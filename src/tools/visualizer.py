"""
MarketSentry Quantitative Data Visualization Suite.
Generates dark-mode, high-density charts using Plotly.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import pandas as pd


def generate_anomaly_chart(ticker: str) -> go.Figure:
    """
    Creates an institutional dual-axis price action and volume chart
    with standard deviation (±2σ) volatility bands.
    """
    stock = yf.Ticker(ticker.strip().upper())
    df = stock.history(period="1mo", interval="1d")

    if df.empty or len(df) < 5:
        return go.Figure()

    df['SMA20'] = df['Close'].rolling(window=20, min_periods=5).mean()
    df['STD20'] = df['Close'].rolling(window=20, min_periods=5).std().fillna(0)
    df['Upper_Band'] = df['SMA20'] + (2 * df['STD20'])
    df['Lower_Band'] = df['SMA20'] - (2 * df['STD20'])

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3]
    )

    # Volatility Envelope
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['Upper_Band'],
            line=dict(color='rgba(148, 163, 184, 0.2)', width=1, dash='dot'),
            name='+2σ Boundary', showlegend=False
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['Lower_Band'],
            line=dict(color='rgba(148, 163, 184, 0.2)', width=1, dash='dot'),
            fill='tonexty', fillcolor='rgba(148, 163, 184, 0.04)',
            name='-2σ Boundary', showlegend=False
        ),
        row=1, col=1
    )

    # Price Line
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df['Close'],
            line=dict(color='#38bdf8', width=2),
            name='Closing Price'
        ),
        row=1, col=1
    )

    # Volume Bars
    colors = ['#22c55e' if c >= o else '#ef4444' for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(
        go.Bar(
            x=df.index, y=df['Volume'],
            marker_color=colors, opacity=0.6,
            name='Volume'
        ),
        row=2, col=1
    )

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#12161f',
        plot_bgcolor='#12161f',
        margin=dict(l=10, r=10, t=20, b=10),
        height=340,
        showlegend=False,
        hovermode='x unified',
        font=dict(family='Inter', size=11, color='#94a3b8'),
        xaxis2=dict(showgrid=False, linecolor='#1f2633'),
        yaxis=dict(gridcolor='#1a202c', zeroline=False),
        yaxis2=dict(showgrid=False, zeroline=False)
    )

    return fig


def generate_dialectic_comparison_chart(bull_points: list, bear_points: list) -> go.Figure:
    """
    Renders horizontal paired conviction bars comparing Bull confidence vs Bear risk scores.
    """
    bull_labels = [p.point[:24] + "..." if len(p.point) > 24 else p.point for p in bull_points]
    bull_scores = [round(p.confidence_score * 100, 1) for p in bull_points]

    bear_labels = [p.point[:24] + "..." if len(p.point) > 24 else p.point for p in bear_points]
    bear_scores = [round(p.confidence_score * 100, 1) for p in bear_points]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=bull_labels,
        x=bull_scores,
        orientation='h',
        name='Bull Upside',
        marker=dict(color='#22c55e', opacity=0.85)
    ))

    fig.add_trace(go.Bar(
        y=bear_labels,
        x=bear_scores,
        orientation='h',
        name='Bear Risk',
        marker=dict(color='#ef4444', opacity=0.85)
    ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#12161f',
        plot_bgcolor='#12161f',
        barmode='group',
        margin=dict(l=10, r=10, t=10, b=10),
        height=260,
        font=dict(family='Inter', size=11, color='#94a3b8'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        xaxis=dict(title='Confidence Metric (%)', gridcolor='#1a202c', range=[0, 100]),
        yaxis=dict(autorange='reversed')
    )

    return fig