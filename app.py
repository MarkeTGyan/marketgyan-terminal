# =========================================================
# 🚀 MarkeTGyan PRO Trading Terminal
# ULTRA RE-OPTIMIZED VERSION (SYNTAX ERROR FIXED)
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

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MarkeTGyan PRO",
    page_icon="📈",
    layout="wide"
)

# =========================================================
# FOLDERS & DIRECTORIES
# =========================================================
if not os.path.exists("userdata"):
    os.makedirs("userdata")

# =========================================================
# CSS STYLE
# =========================================================
st.markdown("""
<style>
html, body, [class*="css"]{
    background:#05070d;
    color:white;
    font-family:'Segoe UI';
}
.stApp{
    background:
    radial-gradient(circle at top left,#102040 0%,#05070d 40%),
    radial-gradient(circle at bottom right,#071522 0%,#05070d 40%);
}
.main-title{
    text-align:center;
    font-size:40px;
    font-weight:900;
    background:linear-gradient(90deg,#00ffd5,#00bfff,#00ff66);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.sub-title{
    color:#9fb4d1;
    font-size:13px;
}
.userbar{
    background:#0f172a;
    padding:12px;
    border-radius:14px;
    border:1px solid rgba(255,255,255,0.05);
    margin-bottom:15px;
}
.metric-box{
    background:linear-gradient(145deg,#111827,#0d1526);
    border-radius:15px;
    padding:10px;
    text-align:center;
    min-height:75px;
    border:1px solid rgba(255,255,255,0.05);
}
.metric-title{
    color:#9fb4d1;
    font-size:10px;
    font-weight:700;
}
.metric-value{
    font-size:22px;
    font-weight:900;
}
.pro-card{
    background:linear-gradient(145deg,#0d1526,#111b31);
    border-radius:18px;
    padding:20px;
    border:1px solid rgba(255,255,255,0.05);
    margin-bottom:15px;
}
.section-title{
    color:#00ffd5;
    font-size:22px;
    font-weight:800;
    margin-bottom:15px;
    border-bottom: 2px solid rgba(0,255,213,0.2);
    padding-bottom:5px;
}
.table-header-custom {
    color: #9fb4d1;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    padding-bottom: 8px;
    margin-bottom: 12px;
}
.watch-row{
    padding-top:10px;
    padding-bottom:10px;
    border-bottom:1px solid rgba(255,255,255,0.06);
}
.trade-popup{
    background:linear-gradient(145deg,#0f172a,#111827);
    padding:20px;
    min-width:420px;
    border-radius:18px;
    border:1px solid rgba(255,255,255,0.06);
}
.trade-stock{
    color:#00ffd5;
    font-size:24px;
    font-weight:900;
}
.trade-price{
    color:white;
    font-size:22px;
    font-weight:900;
}
.trade-label{
    color:#9fb4d1;
    font-size:11px;
}
.mode-box{
    background:#0d1526;
    padding:10px;
    border-radius:12px;
    text-align:center;
    border:1px solid rgba(255,255,255,0.05);
}
.green{ color:#00ff88; font-weight:700; }
.red{ color:#ff4d6d; font-weight:700; }
.orange{ color:orange; font-weight:700; }

.stButton > button{
    width:100%;
    border:none;
    border-radius:10px;
    height:36px;
    font-weight:bold;
}
.buy-btn button{
    background:linear-gradient(135deg,#00c853,#00e676)!important;
    color:white!important;
}
.sell-btn button{
    background:linear-gradient(135deg,#ff1744,#ff5252)!important;
    color:white!important;
}
.scan-btn button{
    background: linear-gradient(90deg, #00ffd5 0%, #00bfff 100%) !important;
    color: #05070d !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 15px rgba(0, 255, 213, 0.3);
}
.stTextInput input, .stNumberInput input{
    background:#111827!important;
    color:white!important;
    border-radius:10px!important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def make_symbol(x):
    x = x.strip().upper()
    if not x.endswith(".NS") and x != "":
        x += ".NS"
    return x

def clean_symbol(x):
    return x.replace(".NS", "")

# =========================================================
# DATA PERSISTENCE
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
        "scan_results": st.session_state.get("scan_results", None)
    }
    with open(f"userdata/{username}.json", "w") as f:
        json.dump(data, f)

def load_user_data(username):
    path = f"userdata/{username}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
        st.session_state.watchlist = data.get("watchlist", ["RELIANCE.NS", "TCS.NS", "INFY.NS", "WIPRO.NS"])
        st.session_state.portfolio = data.get("portfolio", {})
        st.session_state.positions = data.get("positions", {})
        st.session_state.orders = data.get("orders", [])
        st.session_state.history = data.get("history", [])
        st.session_state.margin = data.get("margin", 100000)
        st.session_state.full_name = data.get("name", username)
        st.session_state.scan_results = data.get("scan_results", None)

# =========================================================
# INITIALIZE STATE
# =========================================================
defaults = {
    "logged_in": False,
    "username": "",
    "full_name": "",
    "watchlist": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "WIPRO.NS"],
    "portfolio": {},
    "positions": {},
    "orders": [],
    "history": [],
    "margin": 100000,
    "scan_results": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# FETCH LIVE STOCK PRICE (CORRECT PRICE CHANGE LOGIC)
# =========================================================
def get_stock_data(symbol):
    try:
        ticker_obj = yf.Ticker(symbol)
        df = ticker_obj.history(period="5d", interval="1d")
        
        if df.empty or len(df) < 2:
            return {"price": 150.0, "change": 0.0, "pct": 0.0}
            
        current_price = round(float(df["Close"].iloc[-1]), 2)
        previous_close = round(float(df["Close"].iloc[-2]), 2)
        
        price_change = round(current_price - previous_close, 2)
        change_pct = round((price_change / previous_close) * 100, 2) if previous_close != 0 else 0.0
        
        return {"price": current_price, "change": price_change, "pct": change_pct}
    except:
        return {"price": 150.0, "change": 0.0, "pct": 0.0}

# =========================================================
# NSE TICKERS EXTRACTOR
# =========================================================
@st.cache_data(ttl=86400)
def get_all_nse_tickers():
    priority_list = [
        "PASUPTAC.NS", "PARAS.NS", "CLCIND.NS", "VENUSREM.NS", "MODISONLTD.NS", 
        "ACUTAAS.NS", "ASTRAMICRO.NS", "CUPID.NS", "SHILPAMED.NS", "INDOBORAX.NS", 
        "POLYCAB.NS", "VIJAYA.NS", "DATAPATTNS.NS", "LAURUSLABS.NS", "BBOX.NS"
    ]
    try:
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            df = pd.read_csv(response)
        tickers = [str(sym).strip() + ".NS" for sym in df['SYMBOL'].unique() if pd.notna(sym) and sym != 'SYMBOL']
        for p in priority_list:
            if p not in tickers: tickers.insert(0, p)
        return tickers
    except Exception:
        return priority_list + ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "WIPRO.NS", "DABUR.NS"]

# =========================================================
# DYNAMIC 50-CHUNK SCANNER WITH 1500 DAY BREAKOUT LOGIC
# =========================================================
def scan_all_nse_50_chunks():
    all_tickers = get_all_nse_tickers()
    scanned_list = []
    
    chunk_size = 50  
    total_tickers = len(all_tickers)
    total_chunks = (total_tickers + chunk_size - 1) // chunk_size
    
    status_box = st.empty()
    progress_bar = st.progress(0)
    results_placeholder = st.empty()
    
    for chunk_idx in range(total_chunks):
        start_i = chunk_idx * chunk_size
        end_i = min(start_i + chunk_size, total_tickers)
        chunk = all_tickers[start_i:end_i]
        
        status_box.markdown(f"""
        <div style='background: rgba(0, 255, 213, 0.1); border: 1px solid #00ffd5; padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
            <h4 style='margin:0; color:#00ffd5;'>⏳ CHUNK RUN STATUS</h4>
            <p style='margin:5px 0 0 0; font-size:15px;'>Processing <b>Chunk {chunk_idx + 1}</b> of <b>{total_chunks}</b> (Stocks {start_i} to {end_i} of {total_tickers})</p>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar.progress(int(((chunk_idx + 1) / total_chunks) * 100))
        
        try:
            # Downloading data for ~1500 trading days
            data_df = yf.download(chunk, period="6y", progress=False, group_by='ticker', show_errors=False)
            
            for ticker in chunk:
                try:
                    if isinstance(data_df.columns, pd.MultiIndex):
                        if ticker in data_df.columns.levels[0]:
                            sub_df = data_df[ticker].dropna(subset=['High', 'Close'])
                        else: continue
                    else:
                        sub_df = data_df.dropna(subset=['High', 'Close'])
                    
                    if len(sub_df) < 1001: continue
                    
                    high_vals = sub_df['High'].squeeze()
                    close_vals = sub_df['Close'].squeeze()
                    
                    # Today's parameters
                    daily_high = float(high_vals.iloc[-1])
                    current_price = round(float(close_vals.iloc[-1]), 2)
                    prev_price = round(float(close_vals.iloc[-2]), 2)
                    
                    # 1 Day Ago Max calculation up to past 1000 days
                    hist_highs = high_vals.iloc[:-1]
                    max_1000_high = float(hist_highs.iloc[-1000:].max())
                    
                    # Logic Condition Checklist
                    if daily_high >= max_1000_high:
                        price_change = round(current_price - prev_price, 2)
                        price_pct = round((price_change / prev_price) * 100, 2) if prev_price != 0 else 0.0
                        
                        match_item = {
                            "Stock Name": ticker.replace(".NS", ""),
                            "Current Price": current_price,
                            "Price Change": price_change,
                            "Change Percentage": price_pct
                        }
                        if match_item not in scanned_list:
                            scanned_list.append(match_item)
                except:
                    continue
        except:
            continue
            
        if scanned_list:
            with results_placeholder.container():
                st.markdown(f"🎯 **Live Stocks Found So Far ({len(scanned_list)}):**")
                st.dataframe(pd.DataFrame(scanned_list), use_container_width=True)

    status_box.empty()
    progress_bar.empty()
    results_placeholder.empty()
    return scanned_list

# =========================================================
# CORE TRANSACTION ENGINE (SUCCESS MESSAGES)
# =========================================================
def execute_buy(stock, qty, price, mode):
    value = qty * price
    if st.session_state.margin < value:
        st.error("INSUFFICIENT MARGIN")
        return

    st.session_state.margin -= value

    if stock not in st.session_state.positions:
        st.session_state.positions[stock] = {"qty": qty, "avg_price": price, "mode": mode}
    else:
        old_qty = st.session_state.positions[stock]["qty"]
        old_avg = st.session_state.positions[stock]["avg_price"]
        new_qty = old_qty + qty
        avg = ((old_qty * old_avg) + (qty * price)) / new_qty
        st.session_state.positions[stock]["qty"] = new_qty
        st.session_state.positions[stock]["avg_price"] = round(avg, 2)
        st.session_state.positions[stock]["mode"] = mode

    if mode == "LONGTERM":
        if stock not in st.session_state.portfolio:
            st.session_state.portfolio[stock] = {"qty": qty, "avg_price": price}
        else:
            old_qty = st.session_state.portfolio[stock]["qty"]
            old_avg = st.session_state.portfolio[stock]["avg_price"]
            new_qty = old_qty + qty
            avg = ((old_qty * old_avg) + (qty * price)) / new_qty
            st.session_state.portfolio[stock]["qty"] = new_qty
            st.session_state.portfolio[stock]["avg_price"] = round(avg, 2)

    st.session_state.orders.append({
        "time": datetime.now().strftime("%H:%M:%S"), "stock": stock, "type": "BUY",
        "qty": qty, "price": price, "mode": mode, "status": "EXECUTED", "date": datetime.now().strftime("%Y-%m-%d")
    })
    st.session_state.history.append(st.session_state.orders[-1].copy())
    save_user_data(st.session_state.username)
    
    st.success("🟢 BUY TRADE EXECUTED SUCCESSFULLY!")
    st.toast(f"Bought {qty} Qty of {clean_symbol(stock)}!", icon="✅")
    time.sleep(1)

def execute_sell(stock, qty, price):
    available_qty = 0
    if stock in st.session_state.positions:
        available_qty = st.session_state.positions[stock]["qty"]
    
    if qty > available_qty:
        st.error(f"Not enough quantity to sell. Available: {available_qty}")
        return

    value = qty * price
    st.session_state.margin += value

    remain_pos = st.session_state.positions[stock]["qty"] - qty
    if remain_pos <= 0:
        del st.session_state.positions[stock]
    else:
        st.session_state.positions[stock]["qty"] = remain_pos

    if stock in st.session_state.portfolio:
        remain_port = st.session_state.portfolio[stock]["qty"] - qty
        if remain_port <= 0:
            del st.session_state.portfolio[stock]
        else:
            st.session_state.portfolio[stock]["qty"] = remain_port

    st.session_state.orders.append({
        "time": datetime.now().strftime("%H:%M:%S"), "stock": stock, "type": "SELL",
        "qty": qty, "price": price, "mode": "EXIT", "status": "EXECUTED", "date": datetime.now().strftime("%Y-%m-%d")
    })
    st.session_state.history.append(st.session_state.orders[-1].copy())
    save_user_data(st.session_state.username)
    
    st.success("🔴 SELL TRADE EXECUTED SUCCESSFULLY!")
    st.toast(f"Sold {qty} Qty of {clean_symbol(stock)}!", icon="⚠️")
    time.sleep(1)

# =========================================================
# SIDEBAR LOGIN SYSTEM
# =========================================================
with st.sidebar:
    st.title("🔐 LOGIN")
    auth_mode = st.radio("SELECT", ["LOGIN", "SIGNUP"])
    
    if auth_mode == "SIGNUP":
        full_name = st.text_input("FULL NAME")
    username = st.text_input("EMAIL / USERNAME").strip().lower()
    password = st.text_input("PASSWORD", type="password")

    if auth_mode == "SIGNUP":
        if st.button("CREATE ACCOUNT"):
            users = {}
            if os.path.exists("users.json"):
                with open("users.json", "r") as f: users = json.load(f)
            users[username] = {"password": hash_password(password), "name": full_name.strip().title()}
            with open("users.json", "w") as f: json.dump(users, f)
            st.success("ACCOUNT CREATED")
    else:
        if st.button("LOGIN"):
            users = {}
            if os.path.exists("users.json"):
                with open("users.json", "r") as f: users = json.load(f)
            if username in users and users[username]["password"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.full_name = users[username]["name"]
                load_user_data(username)
                st.rerun()
            else:
                st.error("INVALID OVERVIEW")

if not st.session_state.logged_in:
    st.warning("PLEASE LOGIN FROM SIDEBAR TO USE TERMINAL")
    st.stop()

# =========================================================
# APP MAIN TITLE
# =========================================================
st.markdown("<div class='main-title'>🚀 MarkeTGyan PRO Trading Terminal</div>", unsafe_allow_html=True)

r1, r2 = st.columns([10, 1])
with r1: st.markdown("<div class='sub-title' style='text-align:center;'>Professional Paper Trading Dashboard</div>", unsafe_allow_html=True)
with r2: 
    if st.button("🔄"): st.rerun()

u1, u2 = st.columns([6, 1])
with u1: st.markdown(f"<div class='userbar'>👋 WELCOME <span style='color:#00ffd5;font-weight:900'>{st.session_state.full_name}</span></div>", unsafe_allow_html=True)
with u2:
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

# =========================================================
# SUMMARY METRICS
# =========================================================
invested = sum(p["qty"] * p["avg_price"] for p in st.session_state.portfolio.values())
m1, m2, m3, m4, m5 = st.columns(5)
metrics_list = [
    ("AVAILABLE", f"₹ {round(st.session_state.margin,2)}"),
    ("INVESTED", f"₹ {round(invested,2)}"),
    ("POSITIONS", len(st.session_state.positions)),
    ("HOLDINGS", len(st.session_state.portfolio))
]
for col, (title, val) in zip([m1, m2, m3, m4], metrics_list):
    col.markdown(f"<div class='metric-box'><div class='metric-title'>{title}</div><div class='metric-value'>{val}</div></div>", unsafe_allow_html=True)

with m5:
    with st.popover("ADD MARGIN"):
        amount = st.number_input("ENTER AMOUNT", min_value=1, value=10000, step=1000)
        if st.button("ADD MONEY"):
            st.session_state.margin += amount
            save_user_data(st.session_state.username)
            st.success(f"₹ {amount} ADDED")
            st.rerun()

# =========================================================
# DISPLAY & GRIDS (LEFT: WATCHLIST, RIGHT: TABLES)
# =========================================================
left, right = st.columns([1.2, 1])

# --- WATCHLIST GRID ---
with left:
    st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📊 WATCHLIST</div>", unsafe_allow_html=True)
    
    stock_input = st.text_input(
        "Enter NSE Ticker Symbol:", 
        value="", 
        placeholder="e.g. RELIANCE, TCS, WIPRO", 
        key="my_custom_watchlist_input_key"
    )
    
    if st.button("➕ ADD STOCK TO WATCHLIST"):
        current_typed_stock = st.session_state.my_custom_watchlist_input_key.strip()
        if current_typed_stock:
            sym = make_symbol(current_typed_stock)
            if sym not in st.session_state.watchlist:
                st.session_state.watchlist.append(sym)
                save_user_data(st.session_state.username)
                st.success(f"{clean_symbol(sym)} Added Successfully!")
                time.sleep(0.4)
                st.rerun()
            else:
                st.warning(f"{clean_symbol(sym)} पहले से ही Watchlist में मौजूद है!")
        else:
            st.error("कृपया पहले स्टॉक का नाम टाइप करें!")

    st.markdown("---")

    sh1, sh2, sh3, sh4, sh5 = st.columns([2, 2, 2, 2, 4])
    sh1.markdown("<div class='table-header-custom'>SYMBOL</div>", unsafe_allow_html=True)
    sh2.markdown("<div class='table-header-custom'>PRICE</div>", unsafe_allow_html=True)
    sh3.markdown("<div class='table-header-custom'>CHANGE</div>", unsafe_allow_html=True)
    sh4.markdown("<div class='table-header-custom'>CHANGE%</div>", unsafe_allow_html=True)
    sh5.markdown("<div class='table-header-custom'>ACTIONS</div>", unsafe_allow_html=True)

    for stock in st.session_state.watchlist.copy():
        data = get_stock_data(stock)
        price, change, pct = data["price"], data["change"], data["pct"]
        color = "green" if change >= 0 else "red"

        c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 4])
        c1.markdown(f"**{clean_symbol(stock)}**")
        c2.markdown(f"₹ {price}")
        c3.markdown(f"<div class='{color}'>{change}</div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='{color}'>{pct}%</div>", unsafe_allow_html=True)
        
        b1, b2, b3 = c5.columns([1, 1, 1])
        with b1.popover("⚡"):
            st.markdown(f"<div class='trade-popup'><div class='trade-stock'>{clean_symbol(stock)}</div><div class='trade-label'>LIVE PRICE</div><div class='trade-price'>₹ {price}</div></div>", unsafe_allow_html=True)
            order_type = st.selectbox("ORDER TYPE", ["MARKET", "LIMIT"], key="otype_"+stock)
            trade_mode = st.radio("TRADE MODE", ["INTRADAY", "LONGTERM"], horizontal=True, key="mode_"+stock)
            qty = st.number_input("QUANTITY", min_value=1, value=1, key="qty_"+stock)
            limit_price = price
            if order_type == "LIMIT":
                limit_price = st.number_input("LIMIT PRICE", value=float(price), key="limit_"+stock)
            
            st.markdown(f"<div class='mode-box'>ORDER VALUE<h3 style='color:#00ffd5'>₹ {round(qty * limit_price, 2)}</h3></div>", unsafe_allow_html=True)
            
            bc1, bc2 = st.columns(2)
            with bc1:
                st.markdown('<div class="buy-btn">', unsafe_allow_html=True)
                if st.button("BUY", key="buy_"+stock):
                    execute_buy(stock, qty, price if order_type == "MARKET" else limit_price, trade_mode)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with bc2:
                st.markdown('<div class="sell-btn">', unsafe_allow_html=True)
                if st.button("SELL", key="sell_"+stock):
                    execute_sell(stock, qty, price if order_type == "MARKET" else limit_price)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        b2.link_button("📊", f"https://in.tradingview.com/chart/?symbol=NSE:{clean_symbol(stock)}")
        if b3.button("❌", key="del_"+stock):
            st.session_state.watchlist.remove(stock)
            save_user_data(st.session_state.username)
            st.rerun()
        st.markdown("<div class='watch-row'></div>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

# --- TABLES & SCANNER GRID ---
with right:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💼 PORTFOLIO", "📈 POSITIONS", "📑 ORDERS", "📚 HISTORY", "🎯 SCANNER"])

    with tab1:
        st.markdown("<div class='pro-card'><div class='section-title'>💼 PORTFOLIO</div>", unsafe_allow_html=True)
        if len(st.session_state.portfolio) == 0:
            st.info("NO CURRENT BALANCES / HOLDINGS")
        else:
            h1, h2, h3, h4, h5 = st.columns(5)
            h1.markdown("STOCK"); h2.markdown("QTY"); h3.markdown("AVG"); h4.markdown("LTP"); h5.markdown("P&L")
            st.markdown("---")
            for stock, pos in st.session_state.portfolio.items():
                live = get_stock_data(stock)
                ltp = live["price"]
                pnl = round((ltp - pos["avg_price"]) * pos["qty"], 2)
                pnl_pct = round(((ltp - pos["avg_price"]) / pos["avg_price"]) * 100, 2) if pos["avg_price"] != 0 else 0
                color = "green" if pnl >= 0 else "red"
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.markdown(clean_symbol(stock)); c2.markdown(pos["qty"]); c3.markdown(f"₹ {pos['avg_price']}"); c4.markdown(f"₹ {ltp}"); c5.markdown(f"<div class='{color}'>₹ {pnl} ({pnl_pct}%)</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='pro-card'><div class='section-title'>📈 POSITIONS</div>", unsafe_allow_html=True)
        if len(st.session_state.positions) == 0:
            st.info("NO ACTIVE POSITIONS")
        else:
            h1, h2, h3, h4, h5, h6 = st.columns(6)
            h1.markdown("STOCK"); h2.markdown("MODE"); h3.markdown("QTY"); h4.markdown("AVG"); h5.markdown("LTP"); h6.markdown("P&L")
            st.markdown("---")
            for stock, pos in st.session_state.positions.items():
                live = get_stock_data(stock)
                ltp = live["price"]
                pnl = round((ltp - pos["avg_price"]) * pos["qty"], 2)
                pnl_pct = round(((ltp - pos["avg_price"]) / pos["avg_price"]) * 100, 2) if pos["avg_price"] != 0 else 0
                color = "green" if pnl >= 0 else "red"
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                c1.markdown(clean_symbol(stock)); c2.markdown(pos.get("mode","-")); c3.markdown(pos["qty"]); c4.markdown(f"₹ {pos['avg_price']}"); c5.markdown(f"₹ {ltp}"); c6.markdown(f"<div class='{color}'>₹ {pnl} ({pnl_pct}%)</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='pro-card'><div class='section-title'>📑 ORDERS</div>", unsafe_allow_html=True)
        if len(st.session_state.orders) == 0:
            st.info("NO ORDERS RECORDED")
        else:
            h1, h2, h3, h4, h5, h6, h7 = st.columns(7)
            h1.markdown("TIME"); h2.markdown("STOCK"); h3.markdown("TYPE"); h4.markdown("MODE"); h5.markdown("QTY"); h6.markdown("PRICE"); h7.markdown("STATUS")
            st.markdown("---")
            for order in reversed(st.session_state.orders):
                color = "green" if order["type"] == "BUY" else "red"
                c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
                c1.markdown(order["time"]); c2.markdown(clean_symbol(order["stock"]))
                c3.markdown(f"<div class='{color}'>{order['type']}</div>", unsafe_allow_html=True)
                c4.markdown(order.get("mode","-")); c5.markdown(order["qty"]); c6.markdown(f"₹ {order['price']}")
                c7.markdown(f"<div class='orange'>{order['status']}</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("<div class='pro-card'><div class='section-title'>📚 HISTORY</div>", unsafe_allow_html=True)
        if len(st.session_state.history) == 0:
            st.info("NO AUDIT TRAILS FOUND")
        else:
            h1, h2, h3, h4, h5, h6, h7 = st.columns(7)
            h1.markdown("TIME"); h2.markdown("STOCK"); h3.markdown("TYPE"); h4.markdown("MODE"); h5.markdown("QTY"); h6.markdown("PRICE"); h7.markdown("STATUS")
            st.markdown("---")
            for hist in reversed(st.session_state.history):
                color = "green" if hist["type"] == "BUY" else "red"
                c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
                c1.markdown(hist["time"]); c2.markdown(clean_symbol(hist["stock"]))
                c3.markdown(f"<div class='{color}'>{hist['type']}</div>", unsafe_allow_html=True)
                c4.markdown(hist.get("mode","-")); c5.markdown(hist["qty"]); c6.markdown(f"₹ {hist['price']}")
                c7.markdown(f"<div class='orange'>{hist['status']}</div>", unsafe_allow_html=True)

    with tab5:
        st.markdown("<div class='pro-card'><div class='section-title'>🎯 SCANNER</div>", unsafe_allow_html=True)
        st.markdown("")

        # Styled RUN SCANNER Button
        st.markdown('<div class="scan-btn">', unsafe_allow_html=True)
        execute_scan = st.button("⚡ RUN SCANNER", key="run_breakout_scanner_final_fixed")
        st.markdown('</div>', unsafe_allow_html=True)

        if execute_scan:
            results = scan_all_nse_50_chunks()
            st.session_state.scan_results = results
            save_user_data(st.session_state.username)
            st.success("🎉 SAARE CHUNKS SUCCESSFULLY RUN HO GAYE HAIN!")
            st.balloons()
            st.rerun()

        if st.session_state.scan_results is None:
            st.info("Click the button above to execute scanning analytics.")
        elif len(st.session_state.scan_results) == 0:
            st.warning("No stocks matching breakout parameters found right now.")
        else:
            st.markdown("---")
            sh1, sh2, sh3, sh4, sh5 = st.columns([1, 2, 2, 3, 2])
            sh1.markdown("**S.No.**"); sh2.markdown("**STOCK**"); sh3.markdown("**PRICE**"); sh4.markdown("**CHANGE**"); sh5.markdown("**CHART**")
            st.markdown("---")

            for idx, item in enumerate(st.session_state.scan_results):
                sc_color = "green" if item["Price Change"] >= 0 else "red"
                sc1, sc2, sc3, sc4, sc5 = st.columns([1, 2, 2, 3, 2])
                
                sc1.markdown(f"{idx + 1}")
                sc2.markdown(f"**{item['Stock Name']}**")
                sc3.markdown(f"₹ {item['Current Price']}")
                sc4.markdown(f"<div class='{sc_color}'>₹ {item['Price Change']} ({item['Change Percentage']}%)</div>", unsafe_allow_html=True)
                
                sc5.link_button("📊 Chart", f"https://in.tradingview.com/chart/?symbol=NSE:{item['Stock Name']}", key=f"lnk_{idx}_{item['Stock Name']}")
                st.markdown("<div style='border-bottom:1px solid rgba(255,255,255,0.03); margin-top:2px; margin-bottom:2px;'></div>", unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================
st.markdown("<br><div style='text-align:center; color:#6b7280; font-size:12px;'>MarkeTGyan PRO • Ultra Professional Paper Trading Terminal</div>", unsafe_allow_html=True)
