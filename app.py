# =========================================================
# 🚀 MarkeTGyan PRO Trading Terminal (FIXED & PERSISTENT)
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

# --- CSS और अन्य स्ट्रक्चर आपका पुराना वाला ही है (इसमें कोई बदलाव नहीं किया है) ---
# [ यहाँ आपका पुराना CSS कोड और Helpers फंक्शन वैसे के वैसे रहने दें ]

# =========================================================
# डेटा सेविंग और लोडिंग (सबसे महत्वपूर्ण सुधार)
# =========================================================
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
# सेशन इनिशियलाइजेशन (यहाँ सुधार किया है ताकि डेटा गायब न हो)
# =========================================================
if "logged_in" not in st.session_state:
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
# लॉगिन लॉजिक (यहाँ यूजर का डेटा लोड हो रहा है)
# =========================================================
# (जब आप LOGIN बटन दबाते हैं, तो यह कोड चलाएं)
# if username_input in users and password_correct:
#     st.session_state.logged_in = True
#     st.session_state.username = username_input
#     load_user_data(username_input)  <-- यह लाइन सबसे जरूरी है
#     st.rerun()

# =========================================================
# ट्रेड एग्जीक्यूशन (जहाँ भी आप BUY/SELL करते हैं)
# =========================================================
# (जब भी आप कोई ट्रेड करते हैं, तो अंत में यह जरूर लिखें)
# execute_buy(...)
# save_user_data(st.session_state.username) <-- यह लाइन डेटा सेव रखेगी
# st.rerun()
