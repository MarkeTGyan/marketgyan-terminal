# =========================================================
# 🚀 MarkeTGyan PRO Trading Terminal (FULL INTEGRATED)
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

# [PASTE AAPKA PURANA CSS YAHAN PAR]
st.markdown("""<style>
/* Aapka purana CSS yahan copy karein */
</style>""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def hash_password(password): return hashlib.sha256(password.encode()).hexdigest()
def make_symbol(x): x = x.strip().upper(); return x if x.endswith(".NS") or x == "" else x + ".NS"
def clean_symbol(x): return x.replace(".NS", "")

def save_user_data(username):
    data = {"watchlist": st.session_state.watchlist, "portfolio": st.session_state.portfolio, "positions": st.session_state.positions, "orders": st.session_state.orders, "history": st.session_state.history, "margin": st.session_state.margin, "name": st.session_state.full_name, "scan_results": st.session_state.scan_results}
    with open(f"userdata/{username}.json", "w") as f: json.dump(data, f)

def load_user_data(username):
    path = f"userdata/{username}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            for key in data: st.session_state[key] = data[key]

# --- INITIALIZE STATE ---
if "initialized" not in st.session_state:
    st.session_state.update({"logged_in": False, "username": "", "full_name": "", "watchlist": ["RELIANCE.NS"], "portfolio": {}, "positions": {}, "orders": [], "history": [], "margin": 100000, "scan_results": None, "initialized": True})

# --- LOGIN FLOW ---
if not st.session_state.logged_in:
    with st.sidebar:
        st.title("🔐 LOGIN")
        auth = st.radio("SELECT", ["LOGIN", "SIGNUP"])
        name = st.text_input("FULL NAME") if auth == "SIGNUP" else ""
        user = st.text_input("EMAIL").strip().lower()
        pwd = st.text_input("PASSWORD", type="password")
        if st.button("PROCEED"):
            users = json.load(open("users.json")) if os.path.exists("users.json") else {}
            if auth == "SIGNUP":
                users[user] = {"password": hash_password(pwd), "name": name.title()}
                json.dump(users, open("users.json", "w")); st.success("Created!")
            elif user in users and users[user]["password"] == hash_password(pwd):
                st.session_state.update({"logged_in": True, "username": user, "full_name": users[user]["name"]})
                load_user_data(user); st.rerun()
            else: st.error("Wrong!")
    st.stop()

# =========================================================
# YAHAN SE AAPKA MAIN DASHBOARD CODE SHURU HOTA HAI
# =========================================================
st.markdown("<div class='main-title'>🚀 MarkeTGyan PRO Trading Terminal</div>", unsafe_allow_html=True)

# User Bar
u1, u2 = st.columns([6, 1])
u1.markdown(f"<div class='userbar'>👋 WELCOME <span style='color:#00ffd5'>{st.session_state.full_name}</span></div>", unsafe_allow_html=True)
if u2.button("LOGOUT"):
    save_user_data(st.session_state.username)
    st.session_state.logged_in = False; st.rerun()

# --- ABA AAPKA BAAKI KA PURANA CODE YAHAN SE NICHE PASTE KAR DEIN ---
# Jaise: Summary Metrics, Watchlist, Tables, Scanner...
# Kyunki wo sab 'logged_in' check ke baad aayenge, toh wo login ke baad hi dikhenge.
