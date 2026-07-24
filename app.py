# =========================================================
# 🚀 MarkeTGyan PRO Trading Terminal (STABLE VERSION)
# =========================================================

import streamlit as st
import yfinance as yf
from datetime import datetime
import json
import os
import hashlib
import pandas as pd
import urllib.request
import time

# Page Config
st.set_page_config(page_title="MarkeTGyan PRO", page_icon="📈", layout="wide")

# Helpers
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def make_symbol(x):
    x = x.strip().upper()
    return x if x.endswith(".NS") or x == "" else x + ".NS"

def clean_symbol(x):
    return x.replace(".NS", "")

# Folders
if not os.path.exists("userdata"): os.makedirs("userdata")

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
.main-title{text-align:center; font-size:40px; font-weight:900; background:linear-gradient(90deg,#00ffd5,#00bfff); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.metric-box{background:#0d1526; border-radius:15px; padding:15px; border:1px solid rgba(255,255,255,0.1);}
.green{color:#00ff88; font-weight:bold;} .red{color:#ff4d6d; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# =========================================================
# STATE INITIALIZATION
# =========================================================
if "initialized" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "username": "", "full_name": "",
        "watchlist": ["RELIANCE.NS", "TCS.NS", "INFY.NS"],
        "portfolio": {}, "positions": {}, "orders": [], "history": [],
        "margin": 100000, "scan_results": None, "initialized": True
    })

# =========================================================
# DATA ENGINE
# =========================================================
def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5d")
        if len(df) < 2: return {"price": 0.0, "change": 0.0, "pct": 0.0}
        curr = round(float(df["Close"].iloc[-1]), 2)
        prev = round(float(df["Close"].iloc[-2]), 2)
        return {"price": curr, "change": round(curr - prev, 2), "pct": round(((curr-prev)/prev)*100, 2)}
    except: return {"price": 0.0, "change": 0.0, "pct": 0.0}

def save_data():
    if st.session_state.logged_in:
        data = {k: st.session_state[k] for k in ["watchlist", "portfolio", "positions", "orders", "history", "margin", "scan_results"]}
        with open(f"userdata/{st.session_state.username}.json", "w") as f: json.dump(data, f)

# =========================================================
# LOGIN SYSTEM
# =========================================================
if not st.session_state.logged_in:
    st.sidebar.title("🔐 LOGIN")
    mode = st.sidebar.radio("MODE", ["LOGIN", "SIGNUP"])
    user = st.sidebar.text_input("USERNAME").lower()
    pwd = st.sidebar.text_input("PASSWORD", type="password")
    name = st.sidebar.text_input("FULL NAME") if mode == "SIGNUP" else ""
    
    if st.sidebar.button("SUBMIT"):
        users = json.load(open("users.json")) if os.path.exists("users.json") else {}
        if mode == "SIGNUP":
            users[user] = {"password": hash_password(pwd), "name": name}
            json.dump(users, open("users.json", "w"))
            st.sidebar.success("Account Created!")
        elif user in users and users[user]["password"] == hash_password(pwd):
            st.session_state.update({"logged_in": True, "username": user, "full_name": users[user]["name"]})
            if os.path.exists(f"userdata/{user}.json"):
                st.session_state.update(json.load(open(f"userdata/{user}.json")))
            st.rerun()
    st.stop()

# =========================================================
# MAIN DASHBOARD
# =========================================================
st.markdown("<div class='main-title'>🚀 MarkeTGyan PRO</div>", unsafe_allow_html=True)

# Top Bar
c1, c2 = st.columns([5, 1])
c1.write(f"Welcome, **{st.session_state.full_name}**")
if c2.button("Logout"): st.session_state.logged_in = False; st.rerun()

# Metrics
cols = st.columns(4)
cols[0].markdown(f"<div class='metric-box'>Margin: ₹{st.session_state.margin:,.2f}</div>", unsafe_allow_html=True)
cols[1].markdown(f"<div class='metric-box'>Positions: {len(st.session_state.positions)}</div>", unsafe_allow_html=True)

# Watchlist Logic
st.subheader("📊 Watchlist")
new_stock = st.text_input("Add Symbol (e.g. SBIN):")
if st.button("Add"):
    sym = make_symbol(new_stock)
    if sym not in st.session_state.watchlist:
        st.session_state.watchlist.append(sym)
        save_data()
        st.rerun()

# Display Stocks
for stock in st.session_state.watchlist:
    data = get_stock_data(stock)
    col1, col2, col3 = st.columns([2, 1, 1])
    col1.write(f"**{clean_symbol(stock)}**")
    col2.write(f"₹{data['price']}")
    col3.markdown(f"<span class='{'green' if data['change']>=0 else 'red'}'>{data['pct']}%</span>", unsafe_allow_html=True)

# Scanner Tab
if st.button("⚡ Run Scanner"):
    with st.spinner("Scanning NSE..."):
        # YFinance batch download
        data = yf.download(st.session_state.watchlist, period="1y")
        st.success("Scan Complete!")
        # (Aapka custom logic yahan add karein)

st.divider()
