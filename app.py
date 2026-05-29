# =========================================================
# 🚀 MarkeTGyan PRO Trading Terminal
# ULTRA FINAL PROFESSIONAL VERSION
# =========================================================

import streamlit as st
import yfinance as yf
from datetime import datetime
import json
import os
import hashlib

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MarkeTGyan PRO",
    page_icon="📈",
    layout="wide"
)

# =========================================================
# FOLDERS
# =========================================================
if not os.path.exists("userdata"):
    os.makedirs("userdata")

# =========================================================
# CSS
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

/* ===================================================== */

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

/* ===================================================== */

.userbar{
    background:#0f172a;
    padding:12px;
    border-radius:14px;
    border:1px solid rgba(255,255,255,0.05);
    margin-bottom:15px;
}

/* ===================================================== */

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

/* ===================================================== */

.pro-card{
    background:linear-gradient(145deg,#0d1526,#111b31);
    border-radius:18px;
    padding:15px;
    border:1px solid rgba(255,255,255,0.05);
    margin-bottom:15px;
}

/* ===================================================== */

.section-title{
    color:#00ffd5;
    font-size:22px;
    font-weight:800;
    margin-bottom:10px;
}

/* ===================================================== */

.watch-row{
    padding-top:10px;
    padding-bottom:10px;
    border-bottom:1px solid rgba(255,255,255,0.06);
}

/* ===================================================== */

.trade-popup{
    background:linear-gradient(145deg,#0f172a,#111827);
    padding:15px;
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

/* ===================================================== */

.green{
    color:#00ff88;
    font-weight:700;
}

.red{
    color:#ff4d6d;
    font-weight:700;
}

.orange{
    color:orange;
    font-weight:700;
}

/* ===================================================== */

.stButton > button{
    width:100%;
    border:none;
    border-radius:10px;
    height:36px;
    font-weight:bold;
}

/* ===================================================== */

.buy-btn button{
    background:linear-gradient(135deg,#00c853,#00e676)!important;
    color:white!important;
}

.sell-btn button{
    background:linear-gradient(135deg,#ff1744,#ff5252)!important;
    color:white!important;
}

/* ===================================================== */

.stTextInput input,
.stNumberInput input{
    background:#111827!important;
    color:white!important;
    border-radius:10px!important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HASH PASSWORD
# =========================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================================================
# SAVE USER DATA
# =========================================================
def save_user_data(username):

    data = {

        "watchlist": st.session_state.watchlist,
        "portfolio": st.session_state.portfolio,
        "positions": st.session_state.positions,
        "orders": st.session_state.orders,
        "margin": st.session_state.margin,
        "name": st.session_state.full_name

    }

    with open(f"userdata/{username}.json", "w") as f:
        json.dump(data, f)

# =========================================================
# LOAD USER DATA
# =========================================================
def load_user_data(username):

    path = f"userdata/{username}.json"

    if os.path.exists(path):

        with open(path, "r") as f:
            data = json.load(f)

        st.session_state.watchlist = data.get("watchlist", [])
        st.session_state.portfolio = data.get("portfolio", {})
        st.session_state.positions = data.get("positions", {})
        st.session_state.orders = data.get("orders", [])
        st.session_state.margin = data.get("margin", 100000)
        st.session_state.full_name = data.get("name", username)

# =========================================================
# SESSION STATE
# =========================================================
defaults = {

    "logged_in": False,
    "username": "",
    "full_name": "",
    "watchlist": [],
    "portfolio": {},
    "positions": {},
    "orders": [],
    "margin": 100000

}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# SYMBOL
# =========================================================
def make_symbol(x):

    x = x.strip().upper()

    if not x.endswith(".NS"):
        x += ".NS"

    return x

def clean_symbol(x):
    return x.replace(".NS", "")

# =========================================================
# STOCK DATA
# =========================================================
def get_stock_data(symbol):

    try:

        df = yf.download(
            symbol,
            period="2d",
            interval="1m",
            progress=False
        )

        if df.empty:
            return None

        price = round(float(df["Close"].iloc[-1]), 2)

        prev = round(float(df["Close"].iloc[-2]), 2)

        change = round(price - prev, 2)

        pct = round((change / prev) * 100, 2)

        return {

            "price": price,
            "change": change,
            "pct": pct

        }

    except:
        return None

# =========================================================
# BUY
# =========================================================
def execute_buy(stock, qty, price, mode):

    value = qty * price

    if st.session_state.margin < value:

        st.error("INSUFFICIENT MARGIN")
        return

    st.session_state.margin -= value

    # POSITIONS
    if stock not in st.session_state.positions:

        st.session_state.positions[stock] = {

            "qty": qty,
            "avg_price": price,
            "mode": mode

        }

    else:

        old_qty = st.session_state.positions[stock]["qty"]

        old_avg = st.session_state.positions[stock]["avg_price"]

        new_qty = old_qty + qty

        avg = (
            (old_qty * old_avg)
            +
            (qty * price)
        ) / new_qty

        st.session_state.positions[stock]["qty"] = new_qty

        st.session_state.positions[stock]["avg_price"] = round(avg,2)

        st.session_state.positions[stock]["mode"] = mode

    # LONGTERM ONLY
    if mode == "LONGTERM":

        if stock not in st.session_state.portfolio:

            st.session_state.portfolio[stock] = {

                "qty": qty,
                "avg_price": price

            }

        else:

            old_qty = st.session_state.portfolio[stock]["qty"]

            old_avg = st.session_state.portfolio[stock]["avg_price"]

            new_qty = old_qty + qty

            avg = (
                (old_qty * old_avg)
                +
                (qty * price)
            ) / new_qty

            st.session_state.portfolio[stock]["qty"] = new_qty

            st.session_state.portfolio[stock]["avg_price"] = round(avg,2)

    st.session_state.orders.append({

        "time": datetime.now().strftime("%H:%M:%S"),
        "stock": stock,
        "type": "BUY",
        "qty": qty,
        "price": price,
        "mode": mode,
        "status": "EXECUTED"

    })

    save_user_data(st.session_state.username)

# =========================================================
# SELL
# =========================================================
def execute_sell(stock, qty, price):

    if stock not in st.session_state.positions:
        return

    value = qty * price

    st.session_state.margin += value

    # POSITIONS
    remain = st.session_state.positions[stock]["qty"] - qty

    if remain <= 0:

        del st.session_state.positions[stock]

    else:

        st.session_state.positions[stock]["qty"] = remain

    # PORTFOLIO
    if stock in st.session_state.portfolio:

        remain2 = st.session_state.portfolio[stock]["qty"] - qty

        if remain2 <= 0:

            del st.session_state.portfolio[stock]

        else:

            st.session_state.portfolio[stock]["qty"] = remain2

    st.session_state.orders.append({

        "time": datetime.now().strftime("%H:%M:%S"),
        "stock": stock,
        "type": "SELL",
        "qty": qty,
        "price": price,
        "mode": "EXIT",
        "status": "EXECUTED"

    })

    save_user_data(st.session_state.username)

# =========================================================
# AUTO SQUARE OFF
# =========================================================
try:

    current_time = datetime.now().strftime("%H:%M")

    if current_time >= "15:25":

        intraday_positions = list(
            st.session_state.positions.items()
        )

        for stock, pos in intraday_positions:

            if pos.get("mode") == "INTRADAY":

                live = get_stock_data(stock)

                if live:

                    qty = pos.get("qty", 0)

                    if qty > 0:

                        execute_sell(

                            stock,
                            qty,
                            live["price"]

                        )

except:
    pass

# =========================================================
# LOGIN SIDEBAR
# =========================================================
with st.sidebar:

    st.title("🔐 LOGIN")

    mode = st.radio(
        "SELECT",
        ["LOGIN", "SIGNUP"]
    )

    full_name = ""

    if mode == "SIGNUP":

        full_name = st.text_input("FULL NAME")

    username = st.text_input(
        "EMAIL / USERNAME"
    ).strip().lower()

    password = st.text_input(
        "PASSWORD",
        type="password"
    )

    # =====================================================
    # SIGNUP
    # =====================================================
    if mode == "SIGNUP":

        if st.button("CREATE ACCOUNT"):

            users = {}

            if os.path.exists("users.json"):

                with open("users.json", "r") as f:
                    users = json.load(f)

            users[username] = {

                "password": hash_password(password),

                "name": full_name.strip().title()

            }

            with open("users.json", "w") as f:
                json.dump(users, f)

            st.success("ACCOUNT CREATED")

    # =====================================================
    # LOGIN
    # =====================================================
    else:

        if st.button("LOGIN"):

            users = {}

            if os.path.exists("users.json"):

                with open("users.json", "r") as f:
                    users = json.load(f)

            if (
                username in users
                and
                users[username]["password"] == hash_password(password)
            ):

                st.session_state.logged_in = True

                st.session_state.username = username

                st.session_state.full_name = users[username]["name"]

                load_user_data(username)

                st.rerun()

            else:

                st.error("INVALID LOGIN")

# =========================================================
# LOGIN CHECK
# =========================================================
if not st.session_state.logged_in:

    st.warning("PLEASE LOGIN")
    st.stop()

# =========================================================
# TITLE
# =========================================================
st.markdown("""
<div class='main-title'>
🚀 MarkeTGyan PRO Trading Terminal
</div>
""", unsafe_allow_html=True)

# =========================================================
# SUBTITLE + REFRESH
# =========================================================
r1,r2 = st.columns([10,1])

with r1:

    st.markdown("""
    <div class='sub-title'>
    Professional Paper Trading Dashboard
    </div>
    """, unsafe_allow_html=True)

with r2:

    if st.button("🔄"):
        st.rerun()

# =========================================================
# USER BAR
# =========================================================
u1,u2 = st.columns([6,1])

with u1:

    st.markdown(f"""
    <div class='userbar'>
    👋 WELCOME
    <span style='color:#00ffd5;font-weight:900'>
    {st.session_state.full_name}
    </span>
    </div>
    """, unsafe_allow_html=True)

with u2:

    if st.button("LOGOUT"):

        st.session_state.logged_in = False

        st.rerun()

# =========================================================
# METRICS
# =========================================================
invested = 0

for s,p in st.session_state.portfolio.items():

    invested += p["qty"] * p["avg_price"]

m1,m2,m3,m4,m5 = st.columns(5)

metrics = [

    ("AVAILABLE", f"₹ {round(st.session_state.margin,2)}"),
    ("INVESTED", f"₹ {round(invested,2)}"),
    ("POSITIONS", len(st.session_state.positions)),
    ("HOLDINGS", len(st.session_state.portfolio))

]

for col, data in zip([m1,m2,m3,m4], metrics):

    title, value = data

    col.markdown(f"""
    <div class='metric-box'>
    <div class='metric-title'>{title}</div>
    <div class='metric-value'>{value}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# ADD MARGIN
# =========================================================
with m5:

    popup = st.popover("ADD MARGIN")

    with popup:

        amount = st.number_input(
            "ENTER AMOUNT",
            min_value=1,
            value=10000,
            step=1000
        )

        if st.button("ADD MONEY"):

            st.session_state.margin += amount

            save_user_data(st.session_state.username)

            st.success(f"₹ {amount} ADDED")

            st.rerun()

# =========================================================
# MAIN LAYOUT
# =========================================================
left,right = st.columns([1.2,1])

# =========================================================
# WATCHLIST
# =========================================================
with left:

    st.markdown("""
    <div class='pro-card'>
    <div class='section-title'>
    📊 WATCHLIST
    </div>
    """, unsafe_allow_html=True)

    a1,a2 = st.columns([4,1])

    with a1:

        stock_input = st.text_input(
            "",
            placeholder="Add NSE Stock..."
        )

    with a2:

    if st.button("ADD"):

        if stock_input:

            sym = make_symbol(stock_input)

            if sym not in st.session_state.watchlist:

                st.session_state.watchlist.append(sym)

                save_user_data(st.session_state.username)

                st.rerun()

        sym = make_symbol(stock_input)

        if sym not in st.session_state.watchlist:

            st.session_state.watchlist.append(sym)

            try:
                save_user_data(st.session_state.username)
            except:
                pass

            st.success(f"{clean_symbol(sym)} ADDED")

            st.rerun()
    st.markdown("---")

    for stock in st.session_state.watchlist.copy():

        data = get_stock_data(stock)

        if data:

            price = data["price"]
            change = data["change"]
            pct = data["pct"]

            color = "green" if change >= 0 else "red"

            c1,c2,c3,c4,c5 = st.columns([2,2,2,2,4])

            c1.markdown(f"**{clean_symbol(stock)}**")

            c2.markdown(f"₹ {price}")

            c3.markdown(f"""
            <div class='{color}'>
            {change}
            </div>
            """, unsafe_allow_html=True)

            c4.markdown(f"""
            <div class='{color}'>
            {pct}%
            </div>
            """, unsafe_allow_html=True)

            b1,b2,b3 = c5.columns([1,1,1])

            # =================================================
            # TRADE POPUP
            # =================================================
            popup = b1.popover("⚡")

            with popup:

                st.markdown(f"""
                <div class='trade-popup'>

                <div class='trade-stock'>
                {clean_symbol(stock)}
                </div>

                <div class='trade-label'>
                LIVE MARKET PRICE
                </div>

                <div class='trade-price'>
                ₹ {price}
                </div>

                </div>
                """, unsafe_allow_html=True)

                st.markdown("")

                order_type = st.selectbox(

                    "ORDER TYPE",

                    ["MARKET", "LIMIT"],

                    key="otype"+stock

                )

                trade_mode = st.radio(

                    "TRADE MODE",

                    ["INTRADAY", "LONGTERM"],

                    horizontal=True,

                    key="mode"+stock

                )

                qty = st.number_input(

                    "QUANTITY",

                    min_value=1,

                    value=1,

                    key="qty"+stock

                )

                limit_price = price

                if order_type == "LIMIT":

                    limit_price = st.number_input(

                        "LIMIT PRICE",

                        value=float(price),

                        key="limit"+stock

                    )

                order_value = round(qty * limit_price, 2)

                st.markdown(f"""
                <div class='mode-box'>

                ORDER VALUE

                <h3 style='color:#00ffd5'>
                ₹ {order_value}
                </h3>

                </div>
                """, unsafe_allow_html=True)

                if trade_mode == "INTRADAY":

                    st.warning(
                        "⚠️ Auto square-off at 3:25 PM"
                    )

                bc1,bc2 = st.columns(2)

                # BUY
                with bc1:

                    st.markdown(
                        '<div class="buy-btn">',
                        unsafe_allow_html=True
                    )

                    if st.button("BUY", key="buy"+stock):

                        trade_price = (
                            price
                            if order_type == "MARKET"
                            else limit_price
                        )

                        execute_buy(

                            stock,
                            qty,
                            trade_price,
                            trade_mode

                        )

                        st.success("BUY EXECUTED")

                    st.markdown(
                        '</div>',
                        unsafe_allow_html=True
                    )

                # SELL
                with bc2:

                    st.markdown(
                        '<div class="sell-btn">',
                        unsafe_allow_html=True
                    )

                    if st.button("SELL", key="sell"+stock):

                        trade_price = (
                            price
                            if order_type == "MARKET"
                            else limit_price
                        )

                        execute_sell(

                            stock,
                            qty,
                            trade_price

                        )

                        st.success("SELL EXECUTED")

                    st.markdown(
                        '</div>',
                        unsafe_allow_html=True
                    )

            tv = (
                f"https://in.tradingview.com/chart/?symbol=NSE:{clean_symbol(stock)}"
            )

            b2.link_button("📊", tv)

            if b3.button("❌", key="del"+stock):

                st.session_state.watchlist.remove(stock)

                save_user_data(st.session_state.username)

                st.rerun()

            st.markdown("""
            <div class='watch-row'></div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# RIGHT PANEL
# =========================================================
with right:

    tab1,tab2,tab3 = st.tabs([

        "💼 PORTFOLIO",
        "📈 POSITIONS",
        "📑 ORDERS"

    ])

    # =====================================================
    # PORTFOLIO
    # =====================================================
    with tab1:

        st.markdown("""
        <div class='pro-card'>
        <div class='section-title'>
        💼 PORTFOLIO
        </div>
        """, unsafe_allow_html=True)

        if len(st.session_state.portfolio) == 0:

            st.info("NO HOLDINGS")

        else:

            h1,h2,h3,h4,h5 = st.columns(5)

            h1.markdown("STOCK")
            h2.markdown("QTY")
            h3.markdown("AVG")
            h4.markdown("LTP")
            h5.markdown("P&L")

            st.markdown("---")

            for stock,pos in st.session_state.portfolio.items():

                live = get_stock_data(stock)

                if live:

                    ltp = live["price"]

                    pnl = round(
                        (ltp - pos["avg_price"]) * pos["qty"],
                        2
                    )

                    pnl_pct = round(
                        ((ltp - pos["avg_price"]) / pos["avg_price"]) * 100,
                        2
                    )

                    color = "green" if pnl >= 0 else "red"

                    c1,c2,c3,c4,c5 = st.columns(5)

                    c1.markdown(clean_symbol(stock))
                    c2.markdown(pos["qty"])
                    c3.markdown(f"₹ {pos['avg_price']}")
                    c4.markdown(f"₹ {ltp}")

                    c5.markdown(f"""
                    <div class='{color}'>
                    ₹ {pnl} ({pnl_pct}%)
                    </div>
                    """, unsafe_allow_html=True)

    # =====================================================
    # POSITIONS
    # =====================================================
    with tab2:

        st.markdown("""
        <div class='pro-card'>
        <div class='section-title'>
        📈 POSITIONS
        </div>
        """, unsafe_allow_html=True)

        if len(st.session_state.positions) == 0:

            st.info("NO POSITIONS")

        else:

            h1,h2,h3,h4,h5,h6 = st.columns(6)

            h1.markdown("STOCK")
            h2.markdown("MODE")
            h3.markdown("QTY")
            h4.markdown("AVG")
            h5.markdown("LTP")
            h6.markdown("P&L")

            st.markdown("---")

            for stock,pos in st.session_state.positions.items():

                live = get_stock_data(stock)

                if live:

                    ltp = live["price"]

                    pnl = round(
                        (ltp - pos["avg_price"]) * pos["qty"],
                        2
                    )

                    pnl_pct = round(
                        ((ltp - pos["avg_price"]) / pos["avg_price"]) * 100,
                        2
                    )

                    color = "green" if pnl >= 0 else "red"

                    c1,c2,c3,c4,c5,c6 = st.columns(6)

                    c1.markdown(clean_symbol(stock))
                    c2.markdown(pos.get("mode","-"))
                    c3.markdown(pos["qty"])
                    c4.markdown(f"₹ {pos['avg_price']}")
                    c5.markdown(f"₹ {ltp}")

                    c6.markdown(f"""
                    <div class='{color}'>
                    ₹ {pnl} ({pnl_pct}%)
                    </div>
                    """, unsafe_allow_html=True)

    # =====================================================
    # ORDERS
    # =====================================================
    with tab3:

        st.markdown("""
        <div class='pro-card'>
        <div class='section-title'>
        📑 ORDERS
        </div>
        """, unsafe_allow_html=True)

        if len(st.session_state.orders) == 0:

            st.info("NO ORDERS")

        else:

            h1,h2,h3,h4,h5,h6,h7 = st.columns(7)

            h1.markdown("TIME")
            h2.markdown("STOCK")
            h3.markdown("TYPE")
            h4.markdown("MODE")
            h5.markdown("QTY")
            h6.markdown("PRICE")
            h7.markdown("STATUS")

            st.markdown("---")

            for order in reversed(st.session_state.orders):

                color = (
                    "green"
                    if order["type"] == "BUY"
                    else "red"
                )

                c1,c2,c3,c4,c5,c6,c7 = st.columns(7)

                c1.markdown(order["time"])
                c2.markdown(clean_symbol(order["stock"]))

                c3.markdown(f"""
                <div class='{color}'>
                {order['type']}
                </div>
                """, unsafe_allow_html=True)

                c4.markdown(order.get("mode","-"))
                c5.markdown(order["qty"])
                c6.markdown(f"₹ {order['price']}")

                c7.markdown(f"""
                <div class='orange'>
                {order['status']}
                </div>
                """, unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<br>

<div style='
text-align:center;
color:#6b7280;
font-size:12px;
'>

MarkeTGyan PRO • Ultra Professional Paper Trading Terminal

</div>
""", unsafe_allow_html=True)
