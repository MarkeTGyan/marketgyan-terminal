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
    page_title="MarkeTGyan Trading Terminal",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {

    background-color:#0b0e11;
    color:white;

}

.stApp {

    background-color:#0b0e11;

}

.block-container {

    padding-top:4rem;
    padding-bottom:1rem;
    padding-left:1rem;
    padding-right:1rem;

}

div[data-testid="stVerticalBlock"] {

    gap:0.25rem;

}

hr {

    margin-top:4px !important;
    margin-bottom:4px !important;

}

/* =====================================================
BUTTONS
===================================================== */

.stButton > button {

    width:100%;
    height:32px;

    border-radius:8px;

    border:none;

    font-size:11px;

    font-weight:bold;

}

/* =====================================================
BUY BUTTON
===================================================== */

.buy-green button {

    background:linear-gradient(
        135deg,
        #00c853,
        #00e676
    ) !important;

    color:white !important;

}

/* =====================================================
SELL BUTTON
===================================================== */

.sell-red button {

    background:linear-gradient(
        135deg,
        #ff1744,
        #ff5252
    ) !important;

    color:white !important;

}

/* =====================================================
PANELS
===================================================== */

.panel-box {

    background:#111827;

    border:1px solid #00ffd5;

    border-radius:12px;

    padding:12px;

    margin-bottom:12px;

}

/* =====================================================
SECTION TITLE
===================================================== */

.section-title {

    color:#00ffd5;

    font-size:24px;

    font-weight:bold;

    margin-bottom:10px;

}

/* =====================================================
TRADE POPUP
===================================================== */

.trade-popup-box {

    background:linear-gradient(
        135deg,
        #111827,
        #1f2937
    );

    padding:12px;

    border-radius:10px;

    border:1px solid #00ffd5;

    margin-bottom:8px;

}

.trade-title {

    color:#00ffd5;

    text-align:center;

    font-size:22px;

    font-weight:bold;

}

/* =====================================================
MOBILE VIEW
===================================================== */

@media (max-width:768px) {

    .block-container {

        padding-left:0.5rem;
        padding-right:0.5rem;

    }

    h1 {

        font-size:22px !important;

    }

    .stButton > button {

        height:28px;
        font-size:10px;

    }

}

</style>
""", unsafe_allow_html=True)

# =========================================================
# USER FILES
# =========================================================

if not os.path.exists("users.json"):

    with open("users.json", "w") as f:

        json.dump({}, f)

if not os.path.exists("userdata"):

    os.mkdir("userdata")

with open("users.json") as f:

    users = json.load(f)

# =========================================================
# PASSWORD HASH
# =========================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()

# =========================================================
# LOGIN STATE
# =========================================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False

# =========================================================
# LOGIN SCREEN
# =========================================================

if st.session_state.logged_in == False:

    st.title("🔐 LOGIN SYSTEM")

    tab1, tab2 = st.tabs([
        "LOGIN",
        "SIGNUP"
    ])

    # LOGIN

    with tab1:

        email = st.text_input("GMAIL")

        password = st.text_input(
            "PASSWORD",
            type="password"
        )

        if st.button("LOGIN ACCOUNT"):

            if email in users:

                if users[email]["password"] == hash_password(password):

                    st.session_state.logged_in = True

                    st.session_state.user_email = email

                    st.session_state.user_name = users[email]["name"]

                    st.rerun()

                else:

                    st.error("WRONG PASSWORD")

            else:

                st.error("ACCOUNT NOT FOUND")

    # SIGNUP

    with tab2:

        new_name = st.text_input("FULL NAME")

        new_email = st.text_input("GMAIL ADDRESS")

        new_password = st.text_input(
            "CREATE PASSWORD",
            type="password"
        )

        if st.button("CREATE ACCOUNT"):

            if new_email in users:

                st.warning("ACCOUNT ALREADY EXISTS")

            else:

                users[new_email] = {

                    "name": new_name,

                    "password": hash_password(new_password)

                }

                with open("users.json", "w") as f:

                    json.dump(users, f)

                st.success("ACCOUNT CREATED")

    st.stop()

# =========================================================
# USER DATA
# =========================================================

current_user = st.session_state.user_email

current_name = st.session_state.user_name

safe_email = current_user.replace(
    "@",
    "_"
).replace(".", "_")

user_file = f"userdata/{safe_email}.json"

if os.path.exists(user_file):

    with open(user_file) as f:

        user_data = json.load(f)

else:

    user_data = {

        "watchlist": [],
        "positions": {},
        "orders": [],
        "available_margin": 1000000,
        "invested_margin": 0

    }

# =========================================================
# SESSION STATE
# =========================================================

if "watchlist" not in st.session_state:
    st.session_state.watchlist = user_data["watchlist"]

if "positions" not in st.session_state:
    st.session_state.positions = user_data["positions"]

if "orders" not in st.session_state:
    st.session_state.orders = user_data["orders"]

if "available_margin" not in st.session_state:
    st.session_state.available_margin = user_data["available_margin"]

if "invested_margin" not in st.session_state:
    st.session_state.invested_margin = user_data["invested_margin"]

# =========================================================
# SAVE DATA
# =========================================================

def save_user_data():

    data = {

        "watchlist": st.session_state.watchlist,

        "positions": st.session_state.positions,

        "orders": st.session_state.orders,

        "available_margin": st.session_state.available_margin,

        "invested_margin": st.session_state.invested_margin

    }

    with open(user_file, "w") as f:

        json.dump(data, f)

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
# LIVE DATA
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

        price = round(float(df["Close"].iloc[-1]),2)

        prev = round(float(df["Close"].iloc[-2]),2)

        change = round(price-prev,2)

        pct = round((change/prev)*100,2)

        return {

            "price":price,
            "change":change,
            "pct":pct

        }

    except:

        return None

# =========================================================
# MARGIN
# =========================================================

def recalculate_margin():

    invested = 0

    for stock, pos in st.session_state.positions.items():

        invested += (

            pos["qty"]
            *
            pos["avg_price"]

        )

    st.session_state.invested_margin = round(
        invested,
        2
    )

    st.session_state.available_margin = round(
        1000000 - invested,
        2
    )

# =========================================================
# BUY
# =========================================================

def execute_buy(stock, qty, price):

    value = qty * price

    if value > st.session_state.available_margin:

        st.error("INSUFFICIENT MARGIN")
        return

    st.session_state.orders.append({

        "time": datetime.now().strftime("%H:%M:%S"),

        "stock": stock,

        "type": "BUY",

        "qty": qty,

        "price": price,

        "status": "EXECUTED"

    })

    if stock not in st.session_state.positions:

        st.session_state.positions[stock] = {

            "qty": qty,
            "avg_price": price

        }

    else:

        old_qty = st.session_state.positions[stock]["qty"]

        old_price = st.session_state.positions[stock]["avg_price"]

        new_qty = old_qty + qty

        avg = (

            (old_qty * old_price)
            +
            (qty * price)

        ) / new_qty

        st.session_state.positions[stock]["qty"] = new_qty

        st.session_state.positions[stock]["avg_price"] = round(avg,2)

    recalculate_margin()

    save_user_data()

# =========================================================
# SELL
# =========================================================

def execute_sell(stock, qty, price):

    if stock not in st.session_state.positions:

        st.error("NO POSITION")
        return

    current_qty = st.session_state.positions[stock]["qty"]

    if qty > current_qty:

        st.error("NOT ENOUGH QTY")
        return

    st.session_state.orders.append({

        "time": datetime.now().strftime("%H:%M:%S"),

        "stock": stock,

        "type": "SELL",

        "qty": qty,

        "price": price,

        "status": "EXECUTED"

    })

    remaining = current_qty - qty

    if remaining <= 0:

        del st.session_state.positions[stock]

    else:

        st.session_state.positions[stock]["qty"] = remaining

    recalculate_margin()

    save_user_data()

# =========================================================
# TOP BAR
# =========================================================

top1, top2, top3, top4 = st.columns([5,2,1,1])

with top1:

    st.markdown("""

    <h1 style='
    color:#00ffd5;
    font-size:34px;
    margin-bottom:0px;
    '>

    🚀 MarkeTGyan Trading Terminal

    </h1>

    """, unsafe_allow_html=True)

with top2:

    st.markdown(f"""

    <div style='
    margin-top:15px;
    font-size:18px;
    font-weight:bold;
    text-align:right;
    color:white;
    '>

    👤 {current_name}

    </div>

    """, unsafe_allow_html=True)

with top3:

    st.markdown("<div style='margin-top:10px'></div>",
    unsafe_allow_html=True)

    if st.button("🔄"):

        st.rerun()

with top4:

    st.markdown("<div style='margin-top:10px'></div>",
    unsafe_allow_html=True)

    if st.button("LOGOUT"):

        st.session_state.logged_in = False

        st.rerun()

# =========================================================
# MARGIN
# =========================================================

m1, m2 = st.columns(2)

with m1:

    st.markdown(f"""

    <div class="panel-box">

    <div style="
    color:#00ffd5;
    font-size:16px;
    font-weight:bold;
    ">

    AVAILABLE MARGIN

    </div>

    <div style="
    font-size:28px;
    font-weight:bold;
    ">

    ₹ {round(st.session_state.available_margin,2)}

    </div>

    </div>

    """, unsafe_allow_html=True)

with m2:

    st.markdown(f"""

    <div class="panel-box">

    <div style="
    color:#00ffd5;
    font-size:16px;
    font-weight:bold;
    ">

    INVESTED MARGIN

    </div>

    <div style="
    font-size:28px;
    font-weight:bold;
    ">

    ₹ {round(st.session_state.invested_margin,2)}

    </div>

    </div>

    """, unsafe_allow_html=True)

# =========================================================
# MAIN LAYOUT
# =========================================================

left, divider, right = st.columns([3,0.05,3])

# =========================================================
# DIVIDER
# =========================================================

with divider:

    st.markdown("""
    <div style='
        border-left:2px solid #00ffd5;
        height:2500px;
        margin:auto;
        opacity:0.5;
    '></div>
    """, unsafe_allow_html=True)

# =========================================================
# WATCHLIST
# =========================================================

with left:

    st.markdown("""
    <div class="panel-box">
    <div class="section-title">
    WATCHLIST
    </div>
    """, unsafe_allow_html=True)

    stock_input = st.text_input(
        "ADD STOCK"
    )

    if st.button("ADD"):

        if stock_input:

            sym = make_symbol(stock_input)

            if sym not in st.session_state.watchlist:

                st.session_state.watchlist.append(sym)

                save_user_data()

    st.markdown("---")

    for stock in st.session_state.watchlist.copy():

        data = get_stock_data(stock)

        if data:

            price = data["price"]

            chg = data["change"]

            pct = data["pct"]

            color = "#00ff66" if chg >= 0 else "#ff4d4d"

            c1, c2, c3, c4, c5 = st.columns([2,2,2,2,5])

            c1.markdown(clean_symbol(stock))

            c2.markdown(f"₹ {price}")

            c3.markdown(
                f"<span style='color:{color}'>{chg}</span>",
                unsafe_allow_html=True
            )

            c4.markdown(
                f"<span style='color:{color}'>{pct}%</span>",
                unsafe_allow_html=True
            )

            b1, b2, b3 = c5.columns([1,1,1])

            trade_popup = b1.popover("⚡")

            with trade_popup:

                st.markdown(f"""
                <div class='trade-popup-box'>
                <div class='trade-title'>
                {clean_symbol(stock)}
                </div>
                </div>
                """, unsafe_allow_html=True)

                order_type = st.selectbox(

                    "ORDER TYPE",

                    ["MARKET", "LIMIT"],

                    key="otype"+stock

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

                bc1, bc2 = st.columns(2)

                with bc1:

                    st.markdown(
                        '<div class="buy-green">',
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "BUY",
                        key="buy"+stock
                    ):

                        execute_buy(
                            stock,
                            qty,
                            limit_price if order_type == "LIMIT" else price
                        )

                        st.success("BUY EXECUTED")

                    st.markdown(
                        '</div>',
                        unsafe_allow_html=True
                    )

                with bc2:

                    st.markdown(
                        '<div class="sell-red">',
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "SELL",
                        key="sell"+stock
                    ):

                        execute_sell(
                            stock,
                            qty,
                            limit_price if order_type == "LIMIT" else price
                        )

                        st.success("SELL EXECUTED")

                    st.markdown(
                        '</div>',
                        unsafe_allow_html=True
                    )

            tv_url = (
                f"https://in.tradingview.com/chart/?symbol=NSE:{clean_symbol(stock)}"
            )

            b2.link_button(
                "📊",
                tv_url
            )

            if b3.button(
                "❌",
                key="delete"+stock
            ):

                st.session_state.watchlist.remove(stock)

                save_user_data()

                st.rerun()

            st.markdown("---")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# RIGHT PANEL
# =========================================================

with right:

    # =====================================================
    # PORTFOLIO
    # =====================================================

    st.markdown("""
    <div class="panel-box">
    <div class="section-title">
    PORTFOLIO
    </div>
    """, unsafe_allow_html=True)

    if len(st.session_state.positions) == 0:

        st.info("NO HOLDINGS")

    else:

        p1, p2, p3, p4, p5 = st.columns(5)

        p1.markdown("##### STOCK")
        p2.markdown("##### QTY")
        p3.markdown("##### AVG")
        p4.markdown("##### LTP")
        p5.markdown("##### VALUE")

        st.markdown("---")

        total_value = 0

        for stock, pos in st.session_state.positions.items():

            live_data = get_stock_data(stock)

            if live_data:

                ltp = live_data["price"]

                value = round(
                    ltp * pos["qty"],
                    2
                )

                total_value += value

                c1, c2, c3, c4, c5 = st.columns(5)

                c1.markdown(clean_symbol(stock))

                c2.markdown(str(pos["qty"]))

                c3.markdown(f"₹ {pos['avg_price']}")

                c4.markdown(f"₹ {ltp}")

                c5.markdown(f"₹ {value}")

        st.markdown(f"""
        <div style="
        text-align:right;
        color:#00ffd5;
        font-size:20px;
        font-weight:bold;
        margin-top:10px;
        ">
        TOTAL VALUE : ₹ {round(total_value,2)}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # POSITIONS
    # =====================================================

    st.markdown("""
    <div class="panel-box">
    <div class="section-title">
    POSITIONS
    </div>
    """, unsafe_allow_html=True)

    if len(st.session_state.positions) == 0:

        st.info("NO POSITIONS")

    else:

        h1, h2, h3, h4, h5 = st.columns(5)

        h1.markdown("##### STOCK")
        h2.markdown("##### QTY")
        h3.markdown("##### AVG")
        h4.markdown("##### LTP")
        h5.markdown("##### P&L")

        st.markdown("---")

        for stock, pos in st.session_state.positions.items():

            live_data = get_stock_data(stock)

            if live_data:

                live = live_data["price"]

                pnl = round(

                    (live - pos["avg_price"])
                    *
                    pos["qty"],

                    2

                )

                pnl_color = (
                    "#00ff66"
                    if pnl >= 0
                    else "#ff4d4d"
                )

                c1, c2, c3, c4, c5 = st.columns(5)

                c1.markdown(clean_symbol(stock))

                c2.markdown(str(pos["qty"]))

                c3.markdown(f"₹ {pos['avg_price']}")

                c4.markdown(f"₹ {live}")

                c5.markdown(
                    f"<span style='color:{pnl_color}'>₹ {pnl}</span>",
                    unsafe_allow_html=True
                )

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # ORDERS
    # =====================================================

    st.markdown("""
    <div class="panel-box">
    <div class="section-title">
    ORDERS
    </div>
    """, unsafe_allow_html=True)

    if len(st.session_state.orders) == 0:

        st.info("NO ORDERS")

    else:

        o1, o2, o3, o4, o5, o6 = st.columns(6)

        o1.markdown("##### TIME")
        o2.markdown("##### STOCK")
        o3.markdown("##### TYPE")
        o4.markdown("##### QTY")
        o5.markdown("##### PRICE")
        o6.markdown("##### STATUS")

        st.markdown("---")

        for order in reversed(st.session_state.orders):

            type_color = (
                "#00ff66"
                if order["type"] == "BUY"
                else "#ff4d4d"
            )

            c1, c2, c3, c4, c5, c6 = st.columns(6)

            c1.markdown(order["time"])

            c2.markdown(
                clean_symbol(order["stock"])
            )

            c3.markdown(
                f"<span style='color:{type_color}'>{order['type']}</span>",
                unsafe_allow_html=True
            )

            c4.markdown(str(order["qty"]))

            c5.markdown(f"₹ {order['price']}")

            c6.markdown(order["status"])

    st.markdown("</div>", unsafe_allow_html=True)