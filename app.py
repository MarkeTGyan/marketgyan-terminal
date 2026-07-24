import streamlit as st
import yfinance as yf
from datetime import datetime
import json
import os
import hashlib
import pandas as pd
import time

# --- 1. CONFIG ---
st.set_page_config(page_title="MarkeTGyan PRO", layout="wide")

if not os.path.exists("userdata"): os.makedirs("userdata")

# --- 2. DATA MANAGEMENT (आपका मूल डेटा सेविंग फंक्शन) ---
def save_user_data(username):
    data = {
        "watchlist": st.session_state.watchlist,
        "portfolio": st.session_state.portfolio,
        "positions": st.session_state.positions,
        "margin": st.session_state.margin,
        "full_name": st.session_state.full_name
    }
    with open(f"userdata/{username}.json", "w") as f:
        json.dump(data, f)

def load_user_data(username):
    path = f"userdata/{username}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            st.session_state.watchlist = data.get("watchlist", [])
            st.session_state.portfolio = data.get("portfolio", {})
            st.session_state.positions = data.get("positions", {})
            st.session_state.margin = data.get("margin", 100000)
            st.session_state.full_name = data.get("full_name", "")

# --- 3. SESSION SETUP ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.watchlist = []
    st.session_state.portfolio = {}
    st.session_state.positions = {}
    st.session_state.margin = 100000
    st.session_state.full_name = ""

# --- 4. LOGIN LOGIC ---
# यहाँ आपका वो हिस्सा है जो आप पहले यूज़ कर रहे थे
with st.sidebar:
    user = st.text_input("Username")
    if st.button("Login"):
        st.session_state.logged_in = True
        st.session_state.username = user
        load_user_data(user) # <--- डेटा यहाँ से लोड होगा
        st.rerun()

# --- 5. MAIN TERMINAL (आपका असली कोड यहाँ रखें) ---
if st.session_state.logged_in:
    st.title("MarkeTGyan PRO Trading Terminal")
    
    # जब भी कोई ट्रेड हो, इस फंक्शन को कॉल करें:
    # save_user_data(st.session_state.username)
    
    st.write(f"Welcome, {st.session_state.full_name}")
    # आपका बाकी कोड यहाँ वैसे का वैसा ही रहेगा...
else:
    st.write("Please Login")
