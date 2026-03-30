import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator
import time

# Dashboard title
st.title("Real-Time Stock Market Dashboard")

# User inputs
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL").upper()
interval = st.selectbox("Refresh Interval (seconds)", [10, 30, 60], index=1)


# Historical chart with indicators
st.subheader("Historical Price Chart")
period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "max"], index=0)

# Fetch historical data for the selected period
hist_data = yf.download(ticker, period=period, auto_adjust=True)


# Check if data is valid and contains 'Close' column
if not hist_data.empty and 'Close' in hist_data.columns:
    # Ensure 'Close' is a 1D pandas Series
    close_prices = hist_data['Close'].squeeze()

    # Add technical indicators
    sma20 = SMAIndicator(close_prices, window=20).sma_indicator()
    ema20 = EMAIndicator(close_prices, window=20).ema_indicator()
    rsi14 = RSIIndicator(close_prices, window=14).rsi()

    # Assign indicators back to DataFrame
    hist_data['SMA20'] = sma20
    hist_data['EMA20'] = ema20
    hist_data['RSI14'] = rsi14

    # Candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=hist_data.index,
                                        open=hist_data['Open'],
                                        high=hist_data['High'],
                                        low=hist_data['Low'],
                                        close=hist_data['Close'],
                                        name='Candlesticks')])
    print(hist_data.columns)

    # Add lines for indicators
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['SMA20'], mode='lines', name='SMA 20', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=hist_data.index, y=hist_data['EMA20'], mode='lines', name='EMA 20', line=dict(color='orange')))
    fig.update_layout(title=f"{ticker} Price Chart", xaxis_title="Date", yaxis_title="Price", xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

    # RSI chart
    st.subheader("RSI Indicator")
    rsi_fig = go.Figure(go.Scatter(x=hist_data.index, y=hist_data['RSI14'], mode='lines', name='RSI 14'))
    rsi_fig.update_layout(title="RSI 14", xaxis_title="Date", yaxis_title="RSI")
    st.plotly_chart(rsi_fig)
else:
    st.error("No valid data available for the selected ticker or period.")

    
# Real-time refresh
if st.button("Start Real-Time Monitoring"):
    try:
        while True:
           st.rerun()
           time.sleep(interval)
    except KeyboardInterrupt:
           st.write("Real-time monitoring stopped.")
