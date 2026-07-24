import streamlit as st
import json
import os
import hashlib

# 1. Page Config
st.set_page_config(page_title="MarkeTGyan PRO", layout="wide")

# 2. Folder Setup
if not os.path.exists("userdata"): os.makedirs("userdata")

# 3. Persistence Functions
def save_user_data(username):
    data = {
        "watchlist": st.session_state.watchlist,
        "portfolio": st.session_state.portfolio,
        "positions": st.session_state.positions,
        "margin": st.session_state.margin,
        "name": st.session_state.full_name
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
            st.session_state.margin = data.get("margin", 100000)
            st.session_state.full_name = data.get("name", username)

# 4. Session Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.full_name = ""
    st.session_state.watchlist = ["RELIANCE.NS"]
    st.session_state.portfolio = {}
    st.session_state.positions = {}
    st.session_state.margin = 100000

# 5. UI: Sidebar Login
with st.sidebar:
    st.title("🔐 LOGIN")
    user = st.text_input("USERNAME").strip().lower()
    pw = st.text_input("PASSWORD", type="password")
    if st.button("LOGIN"):
        # Login logic (Hash check here)
        st.session_state.logged_in = True
        st.session_state.username = user
        load_user_data(user)
        st.rerun()

# 6. Main Dashboard
if st.session_state.logged_in:
    st.title("🚀 MarkeTGyan PRO")
    st.write(f"WELCOME, {st.session_state.full_name}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("MARGIN", f"₹ {st.session_state.margin}")
        if st.button("SAVE DATA"):
            save_user_data(st.session_state.username)
            st.success("DATA SAVED!")
            
    with col2:
        st.subheader("PORTFOLIO")
        st.write(st.session_state.portfolio)
else:
    st.warning("PLEASE LOGIN")
