import streamlit as st
import yfinance as yf
from datetime import datetime
import json
import os
import hashlib
import pandas as pd
import urllib.request
import time

# =========================================================
# PAGE CONFIG - सबसे ऊपर
# =========================================================
st.set_page_config(page_title="MarkeTGyan PRO", page_icon="📈", layout="wide")

# =========================================================
# FOLDERS
# =========================================================
if not os.path.exists("userdata"):
    os.makedirs("userdata")

# =========================================================
# CSS STYLE
# =========================================================
st.markdown("""
<style>
html, body, [class*="css"]{ background:#05070d; color:white; font-family:'Segoe UI'; }
.stApp{ background: radial-gradient(circle at top left,#102040 0%,#05070d 40%), radial-gradient(circle at bottom right,#071522 0%,#05070d 40%); }
.main-title{ text-align:center; font-size:40px; font-weight:900; background:linear-gradient(90deg,#00ffd5,#00bfff,#00ff66); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.sub-title{ color:#9fb4d1; font-size:13px; text-align:center; margin-bottom: 20px;}
.metric-box{ background:linear-gradient(145deg,#111827,#0d1526); border-radius:15px; padding:10px; text-align:center; border:1px solid rgba(255,255,255,0.05); }
.metric-title{ color:#9fb4d1; font-size:10px; font-weight:700; }
.metric-value{ font-size:22px; font-weight:900; }
.pro-card{ background:linear-gradient(145deg,#0d1526,#111b31); border-radius:18px; padding:20px; border:1px solid rgba(255,255,255,0.05); margin-bottom:15px; }
.section-title{ color:#00ffd5; font-size:22px; font-weight:800; margin-bottom:15px; border-bottom: 2px solid rgba(0,255,213,0.2); padding-bottom:5px; }
.green{ color:#00ff88; font-weight:700; }
.red{ color:#ff4d6d; font-weight:700; }
.orange{ color:orange; font-weight:700; }
.stButton > button{ width:100%; border-radius:10px; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATA & HELPERS
# =========================================================
def hash_password(password): return hashlib.sha256(password.encode()).hexdigest()

def save_user_data(username):
    data = {
        "watchlist": st.session_state.watchlist,
        "portfolio": st.session_state.portfolio,
        "positions": st.session_state.positions,
        "orders": st.session_state.orders,
        "history": st.session_state.history,
        "margin": st.session_state.margin,
        "name": st.session_state.full_name,
        "scan_results": st.session_state.scan_results
    }
    with open(f"userdata/{username}.json", "w") as f:
        json.dump(data, f)

def load_user_data(username):
    path = f"userdata/{username}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            st.session_state.watchlist = data.get("watchlist", ["RELIANCE.NS", "TCS.NS"])
            st.session_state.portfolio = data.get("portfolio", {})
            st.session_state.positions = data.get("positions", {})
            st.session_state.orders = data.get("orders", [])
            st.session_state.history = data.get("history", [])
            st.session_state.margin = data.get("margin", 100000)
            st.session_state.full_name = data.get("name", username)
            st.session_state.scan_results = data.get("scan_results", None)

# =========================================================
# INITIALIZATION
# =========================================================
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.full_name = ""
    st.session_state.watchlist = ["RELIANCE.NS", "TCS.NS"]
    st.session_state.portfolio = {}
    st.session_state.positions = {}
    st.session_state.orders = []
    st.session_state.history = []
    st.session_state.margin = 100000
    st.session_state.scan_results = None

# =========================================================
# LOGIC FUNCTIONS
# =========================================================
def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="2d")
        if df.empty: return {"price": 100.0, "change": 0.0, "pct": 0.0}
        curr = round(float(df["Close"].iloc[-1]), 2)
        prev = round(float(df["Close"].iloc[-2]), 2)
        return {"price": curr, "change": round(curr - prev, 2), "pct": round(((curr - prev) / prev) * 100, 2)}
    except: return {"price": 100.0, "change": 0.0, "pct": 0.0}

# =========================================================
# SIDEBAR LOGIN
# =========================================================
with st.sidebar:
    st.title("🔐 LOGIN")
    mode = st.radio("SELECT", ["LOGIN", "SIGNUP"])
    user_input = st.text_input("EMAIL").strip().lower()
    pass_input = st.text_input("PASSWORD", type="password")
    
    if mode == "SIGNUP":
        name = st.text_input("FULL NAME")
        if st.button("CREATE ACCOUNT"):
            users = {}
            if os.path.exists("users.json"):
                with open("users.json", "r") as f: users = json.load(f)
            users[user_input] = {"password": hash_password(pass_input), "name": name}
            with open("users.json", "w") as f: json.dump(users, f)
            st.success("CREATED!")
    else:
        if st.button("LOGIN"):
            users = {}
            if os.path.exists("users.json"):
                with open("users.json", "r") as f: users = json.load(f)
            if user_input in users and users[user_input]["password"] == hash_password(pass_input):
                st.session_state.logged_in = True
                st.session_state.username = user_input
                load_user_data(user_input)
                st.rerun()
            else: st.error("INVALID")

# =========================================================
# MAIN APP
# =========================================================
if not st.session_state.logged_in:
    st.warning("PLEASE LOGIN TO ACCESS TERMINAL")
else:
    st.markdown("<div class='main-title'>🚀 MarkeTGyan PRO</div>", unsafe_allow_html=True)
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

    # DASHBOARD
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='metric-box'><div class='metric-title'>BALANCE</div><div class='metric-value'>₹ {round(st.session_state.margin, 2)}</div></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-box'><div class='metric-title'>POSITIONS</div><div class='metric-value'>{len(st.session_state.positions)}</div></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-box'><div class='metric-title'>ORDERS</div><div class='metric-value'>{len(st.session_state.orders)}</div></div>", unsafe_allow_html=True)

    # WATCHLIST
    st.markdown("---")
    st.subheader("📊 WATCHLIST")
    new_stock = st.text_input("ADD SYMBOL (e.g. INFY)")
    if st.button("ADD"):
        sym = (new_stock.strip().upper() + ".NS") if not new_stock.endswith(".NS") else new_stock.upper()
        if sym not in st.session_state.watchlist:
            st.session_state.watchlist.append(sym)
            save_user_data(st.session_state.username)
            st.rerun()

    for stock in st.session_state.watchlist:
        data = get_stock_data(stock)
        cols = st.columns([2, 1, 1, 1])
        cols[0].write(stock)
        cols[1].write(f"₹ {data['price']}")
        cols[2].write(f"{data['pct']}%")
        if cols[3].button("DEL", key=f"del_{stock}"):
            st.session_state.watchlist.remove(stock)
            save_user_data(st.session_state.username)
            st.rerun()

    # PORTFOLIO TAB
    st.markdown("---")
    st.subheader("💼 PORTFOLIO")
    if not st.session_state.portfolio:
        st.info("NO HOLDINGS")
    else:
        df_p = pd.DataFrame.from_dict(st.session_state.portfolio, orient='index')
        st.table(df_p)
