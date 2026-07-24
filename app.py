import streamlit as st
import yfinance as yf
from datetime import datetime
import json
import os
import hashlib
import pandas as pd
import urllib.request
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="MarkeTGyan PRO", page_icon="📈", layout="wide")

# --- DIRECTORY SETUP ---
if not os.path.exists("userdata"):
    os.makedirs("userdata")

# --- DATA PERSISTENCE ENGINE ---
def save_user_data(username):
    data = {
        "watchlist": st.session_state.get("watchlist", []),
        "portfolio": st.session_state.get("portfolio", {}),
        "positions": st.session_state.get("positions", {}),
        "orders": st.session_state.get("orders", []),
        "history": st.session_state.get("history", []),
        "margin": st.session_state.get("margin", 100000),
        "name": st.session_state.get("full_name", username),
        "scan_results": st.session_state.get("scan_results", None)
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

# --- INITIALIZATION ---
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

# --- SIDEBAR LOGIN ---
with st.sidebar:
    st.title("🔐 LOGIN")
    mode = st.radio("SELECT", ["LOGIN", "SIGNUP"])
    user = st.text_input("EMAIL").strip().lower()
    pw = st.text_input("PASSWORD", type="password")
    
    if mode == "SIGNUP":
        name = st.text_input("FULL NAME")
        if st.button("CREATE ACCOUNT"):
            users = {}
            if os.path.exists("users.json"):
                with open("users.json", "r") as f: users = json.load(f)
            users[user] = {"password": hashlib.sha256(pw.encode()).hexdigest(), "name": name}
            with open("users.json", "w") as f: json.dump(users, f)
            st.success("ACCOUNT CREATED")
    else:
        if st.button("LOGIN"):
            users = {}
            if os.path.exists("users.json"):
                with open("users.json", "r") as f: users = json.load(f)
            if user in users and users[user]["password"] == hashlib.sha256(pw.encode()).hexdigest():
                st.session_state.logged_in = True
                st.session_state.username = user
                load_user_data(user) # डेटा यहाँ लोड होगा
                st.rerun()
            else:
                st.error("INVALID CREDENTIALS")

# --- MAIN APP ---
if not st.session_state.logged_in:
    st.warning("PLEASE LOGIN TO ACCESS TERMINAL")
else:
    st.title("🚀 MarkeTGyan PRO Trading Terminal")
    if st.button("LOGOUT"):
        save_user_data(st.session_state.username) # लॉगआउट पर डेटा सेव
        st.session_state.logged_in = False
        st.rerun()
    
    # यहाँ आपका बाकी UI कोड काम करेगा...
    st.write(f"WELCOME {st.session_state.full_name}")
    st.metric("BALANCE", f"₹ {st.session_state.margin}")
