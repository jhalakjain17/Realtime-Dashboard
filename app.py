import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objs as go

st.set_page_config(layout="wide", page_title="Stock Dashboard")

# ---------------- Sidebar ----------------
st.sidebar.title("📊 Stock Dashboard")

ticker = st.sidebar.text_input("Enter Stock Ticker", "TSLA").upper()

mode = st.sidebar.radio("Select Data Type", ["Daily (EOD)", "Intraday (Live)"])

if mode == "Daily (EOD)":
    period = st.sidebar.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=0)
    interval = "1d"
else:
    interval = st.sidebar.selectbox("Select Interval", ["1m", "5m", "15m", "30m", "1h"], index=2)
    period = "1d"

# ---------------- Fetch Data ----------------
data = yf.download(ticker, period=period, interval=interval)

if data.empty:
    st.error("⚠️ No data found! Try another stock ticker or interval.")
    st.stop()

# ---------------- Technical Indicators ----------------
# SMA & EMA (20-period)
data['SMA20'] = data['Close'].rolling(window=20).mean()
data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()

# RSI (14-period)
delta = data['Close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss
data['RSI'] = 100 - (100 / (1 + rs))

# ---------------- Price Chart ----------------
st.subheader(f"{ticker} Price Chart ({mode})")

fig = go.Figure()

# Candlesticks
fig.add_trace(go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name="Candlesticks"
))

# SMA & EMA
fig.add_trace(go.Scatter(x=data.index, y=data['SMA20'], line=dict(color="blue", width=1.5), name="SMA 20"))
fig.add_trace(go.Scatter(x=data.index, y=data['EMA20'], line=dict(color="orange", width=1.5), name="EMA 20"))

fig.update_layout(
    xaxis_title="Date/Time",
    yaxis_title="Price",
    template="plotly_dark",
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- RSI Chart ----------------
st.subheader("RSI Indicator (14-period)")

fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], line=dict(color="cyan", width=1.5), name="RSI"))
fig_rsi.add_hline(y=70, line=dict(color="red", dash="dash"))
fig_rsi.add_hline(y=30, line=dict(color="green", dash="dash"))

fig_rsi.update_layout(
    xaxis_title="Date/Time",
    yaxis_title="RSI",
    template="plotly_dark"
)

st.plotly_chart(fig_rsi, use_container_width=True)

# ---------------- Latest Metrics ----------------
st.subheader("Latest Market Data")

try:
    if not data.empty and len(data) > 1:
        last_price = float(data['Close'].iloc[-1])
        prev_price = float(data['Close'].iloc[-2])
        st.metric("Last Price", f"${last_price:.2f}", f"{last_price - prev_price:.2f}")
    elif len(data) == 1:
        last_price = float(data['Close'].iloc[-1])
        st.metric("Last Price", f"${last_price:.2f}", "N/A (Only 1 datapoint)")
    else:
        st.warning("⚠️ No market data available for this ticker/interval right now.")
except Exception as e:
    st.error(f"⚠️ Error while fetching metrics: {e}")
