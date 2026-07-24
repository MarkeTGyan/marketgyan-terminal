import streamlit as st
import yfinance as yf
from datetime import datetime
import json
import os
import hashlib
import pandas as pd
import urllib.request
import time

# --- CONFIG & HELPERS ---
st.set_page_config(page_title="MarkeTGyan PRO", page_icon="📈", layout="wide")
if not os.path.exists("userdata"): os.makedirs("userdata")

def hash_password(password): return hashlib.sha256(password.encode()).hexdigest()
def make_symbol(x): x = x.strip().upper(); return x if x.endswith(".NS") or x == "" else x + ".NS"
def clean_symbol(x): return x.replace(".NS", "")

def save_user_data(username):
    data = {"watchlist": st.session_state.watchlist, "portfolio": st.session_state.portfolio, 
            "positions": st.session_state.positions, "orders": st.session_state.orders, 
            "history": st.session_state.history, "margin": st.session_state.margin, 
            "name": st.session_state.full_name, "scan_results": st.session_state.scan_results}
    with open(f"userdata/{username}.json", "w") as f: json.dump(data, f)

def load_user_data(username):
    path = f"userdata/{username}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            st.session_state.update(data)

# --- INITIALIZE STATE ---
if "initialized" not in st.session_state:
    st.session_state.update({"logged_in": False, "username": "", "full_name": "", "watchlist": ["RELIANCE.NS"], 
                             "portfolio": {}, "positions": {}, "orders": [], "history": [], 
                             "margin": 100000, "scan_results": None, "initialized": True})

# --- CSS STYLES ---
st.markdown("""<style>
.main-title{text-align:center; font-size:40px; font-weight:900; background:linear-gradient(90deg,#00ffd5,#00bfff); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.userbar{background:#0f172a; padding:12px; border-radius:14px; margin-bottom:15px;}
.metric-box{background:#0d1526; padding:15px; border-radius:15px; text-align:center; border:1px solid #333;}
.green{color:#00ff88; font-weight:bold;} .red{color:#ff4d6d; font-weight:bold;}
</style>""", unsafe_allow_html=True)

# --- LOGIN / SIGNUP FLOW ---
if not st.session_state.logged_in:
    with st.sidebar:
        st.title("🔐 LOGIN")
        auth = st.radio("SELECT", ["LOGIN", "SIGNUP"])
        name = st.text_input("FULL NAME") if auth == "SIGNUP" else ""
        user = st.text_input("USERNAME").strip().lower()
        pwd = st.text_input("PASSWORD", type="password")
        if st.button("PROCEED"):
            users = json.load(open("users.json")) if os.path.exists("users.json") else {}
            if auth == "SIGNUP":
                users[user] = {"password": hash_password(pwd), "name": name.title()}
                json.dump(users, open("users.json", "w")); st.success("Created!")
            elif user in users and users[user]["password"] == hash_password(pwd):
                st.session_state.update({"logged_in": True, "username": user, "full_name": users[user]["name"]})
                load_user_data(user); st.rerun()
            else: st.error("Invalid Credentials!")
    st.warning("PLEASE LOGIN FROM SIDEBAR")
    st.stop()

# --- DASHBOARD (AFTER LOGIN) ---
st.markdown("<div class='main-title'>🚀 MarkeTGyan PRO Trading Terminal</div>", unsafe_allow_html=True)

u1, u2 = st.columns([6, 1])
u1.markdown(f"<div class='userbar'>👋 WELCOME <span style='color:#00ffd5'>{st.session_state.full_name}</span></div>", unsafe_allow_html=True)
if u2.button("LOGOUT"):
    save_user_data(st.session_state.username)
    st.session_state.logged_in = False; st.rerun()

# --- METRICS ---
m1, m2, m3, m4 = st.columns(4)
m1.markdown(f"<div class='metric-box'>Margin: ₹{st.session_state.margin:,.2f}</div>", unsafe_allow_html=True)
m2.markdown(f"<div class='metric-box'>Positions: {len(st.session_state.positions)}</div>", unsafe_allow_html=True)

# --- WATCHLIST ---
st.subheader("📊 Watchlist")
new_stock = st.text_input("Add Symbol (e.g. RELIANCE):")
if st.button("Add to Watchlist"):
    sym = make_symbol(new_stock)
    if sym not in st.session_state.watchlist: st.session_state.watchlist.append(sym); save_user_data(st.session_state.username); st.rerun()

for stock in st.session_state.watchlist:
    col1, col2 = st.columns(2)
    col1.write(f"**{clean_symbol(stock)}**")
    if col2.button("Remove", key=f"del_{stock}"): st.session_state.watchlist.remove(stock); save_user_data(st.session_state.username); st.rerun()
