# =========================================================
# 🚀 MarkeTGyan PRO Trading Terminal (USER-SPECIFIC FIX)
# =========================================================

import streamlit as st
import yfinance as yf
from datetime import datetime
import json
import os
import hashlib
import pandas as pd
import time

# [CSS STYLE - APKA PURANA WALA]
# (Isse change mat kijiye, waisa hi rehne dein)
st.markdown("""<style>
/* ... (Aapka CSS yahan rahega) ... */
</style>""", unsafe_allow_html=True)

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user_data(username):
    # Sirf login hone par hi save karega
    if username:
        data = {
            "watchlist": st.session_state.watchlist,
            "portfolio": st.session_state.portfolio,
            "positions": st.session_state.positions,
            "orders": st.session_state.orders,
            "history": st.session_state.history,
            "margin": st.session_state.margin,
            "scan_results": st.session_state.scan_results
        }
        with open(f"userdata/{username}.json", "w") as f:
            json.dump(data, f)

def load_user_data(username):
    path = f"userdata/{username}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            st.session_state.watchlist = data.get("watchlist", ["RELIANCE.NS"])
            st.session_state.portfolio = data.get("portfolio", {})
            st.session_state.positions = data.get("positions", {})
            st.session_state.orders = data.get("orders", [])
            st.session_state.history = data.get("history", [])
            st.session_state.margin = data.get("margin", 100000)
            st.session_state.scan_results = data.get("scan_results", None)

# =========================================================
# INITIALIZE STATE (GLOBAL)
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "username": "", "full_name": "",
        "watchlist": ["RELIANCE.NS"], "portfolio": {}, 
        "positions": {}, "orders": [], "history": [], 
        "margin": 100000, "scan_results": None
    })

# =========================================================
# SIDEBAR LOGIN SYSTEM
# =========================================================
with st.sidebar:
    st.title("🔐 LOGIN")
    auth_mode = st.radio("SELECT", ["LOGIN", "SIGNUP"])
    
    # Input fields
    if auth_mode == "SIGNUP": full_name = st.text_input("FULL NAME")
    username = st.text_input("EMAIL / USERNAME").strip().lower()
    password = st.text_input("PASSWORD", type="password")

    if st.button("PROCEED"):
        users = {}
        if os.path.exists("users.json"):
            with open("users.json", "r") as f: users = json.load(f)
            
        if auth_mode == "SIGNUP":
            users[username] = {"password": hash_password(password), "name": full_name.title()}
            with open("users.json", "w") as f: json.dump(users, f)
            st.success("ACCOUNT CREATED! NOW LOGIN.")
        else:
            if username in users and users[username]["password"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.full_name = users[username]["name"]
                # YAHAN SE DATA LOAD HOGA
                load_user_data(username)
                st.rerun()
            else:
                st.error("INVALID CREDENTIALS")

if not st.session_state.logged_in:
    st.warning("PLEASE LOGIN FROM SIDEBAR")
    st.stop()

# =========================================================
# LOGOUT BUTTON
# =========================================================
if st.sidebar.button("LOGOUT"):
    save_user_data(st.session_state.username) # Save before logout
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# =========================================================
# YAHAN SE AAPKA BAKI KA POORA CODE VAISE HI CHALEGA
# =========================================================
# ... (Baaki poora logic yahan paste karein) ...
