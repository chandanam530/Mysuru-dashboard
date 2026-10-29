"""Mysuru Environmental Dashboard - Streamlit app (login + dashboard).

Run:  streamlit run app.py
Default login:  username = admin   password = Mysuru@2026
(Change it by adding username / password to .streamlit/secrets.toml)
"""
import hmac
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Mysuru Environmental Dashboard", page_icon="🌿",
                   layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------------- settings
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
ZONES = ["Urban", "Semi-Urban", "Rural"]
COLORS = {"Urban": "#0284c7", "Semi-Urban": "#34d399", "Rural": "#047857"}
DATA_FILE = Path(__file__).parent / "mysuru_environmental_dashboard_data.csv"


def credentials():
    try:
        return st.secrets["username"], st.secrets["password"]
    except Exception:
        return "admin", "Mysuru@2026"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df["Month"] = pd.Categorical(df["Month"], categories=MONTHS, ordered=True)
    return df


# ---------------------------------------------------------------- styling
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp {font-family:'Inter',sans-serif;}
#MainMenu, footer, header[data-testid="stHeader"] {visibility:hidden; height:0;}
.block-container {padding-top:0 !important; padding-left:1.6rem; padding-right:1.6rem; max-width:100%;}
.hero {margin:0 -1.6rem 1.4rem; padding:26px 20px; text-align:center; color:#fff;
       background:linear-gradient(90deg,#064e3b,#0e7490);}
.hero h1 {margin:0; font-size:clamp(26px,3.6vw,44px); font-weight:800; letter-spacing:1px; color:#fff; padding:0;}
.hero span {display:block; margin-top:8px; opacity:.85; font-size:15px;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#0c2e27,#0a2420);}
[data-testid="stSidebar"] * {color:#c3d9d0;}
[data-testid="stSidebar"] label p {color:#fff !important; font-weight:500; font-size:14px;}
[data-testid="stSidebar"] [data-baseweb="select"] * {color:#12302a !important;}
.mh {font-size:11px; font-weight:700; letter-spacing:1.5px; color:#6f9a8b !important; margin:22px 0 8px;}
.up {display:flex; align-items:center; gap:12px; margin-bottom:6px;}
.av {width:44px; height:44px; border-radius:12px; background:linear-gradient(135deg,#10b981,#0e7490);
     display:flex; align-items:center; justify-content:center; font-weight:700; font-size:18px; color:#fff !important;}
.up b {color:#fff !important; display:block;}
.nav-on {background:rgba(52,211,153,.16); color:#fff !important; padding:10px 14px; border-radius:10px; font-weight:500;}
[data-testid="stSidebar"] .stButton button {width:100%; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.14);
     color:#fff !important; border-radius:10px; text-align:left;}
.kpi {display:flex; align-items:center; gap:16px; background:#fff; border:1px solid #e0e9e4; border-radius:14px;
      padding:18px 22px; box-shadow:0 1px 2px rgba(16,50,40,.06),0 4px 14px rgba(16,50,40,.06);}
.kpi .ic {width:54px; height:54px; border-radius:14px; display:flex; align-items:center; justify-content:center; color:#fff;}
.kpi small {color:#64796f; font-weight:500; font-size:13px;}
.kpi b {display:block; font-size:30px; font-weight:800; color:#12302a;}
div[data-testid="stVerticalBlockBorderWrapper"] {background:#fff; border-radius:14px; border-color:#e0e9e4 !important;
      box-shadow:0 1px 2px rgba(16,50,40,.06),0 4px 14px rgba(16,50,40,.06);}
.ct {font-size:16px; font-weight:700; color:#12302a; border-left:4px solid #10b981; padding-left:10px; line-height:1.2;}
.cs {font-size:13px; color:#64796f; margin:4px 0 6px 14px;}
table.t {width:100%; border-collapse:collapse; font-size:14px;}
table.t th {background:#f3f7f5; color:#64796f; font-size:12px; text-transform:uppercase; letter-spacing:.8px; text-align:left; padding:11px 12px;}
table.t td {padding:11px 12px; border-bottom:1px solid #e0e9e4;}
.dot {display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:8px;}
ul.k {padding-left:20px; margin:0;} ul.k li {margin:9px 0; line-height:1.55; font-size:14px;} ul.k li::marker {color:#10b981;}
.foot {margin-top:18px; padding:14px 0; border-top:1px solid #e0e9e4; color:#64796f; font-size:13px;}
.lv {background:linear-gradient(145deg,#064e3b,#0e7490); color:#fff; border-radius:18px; padding:56px 48px; min-height:430px;}
.lv small {letter-spacing:3px; font-weight:600; opacity:.8;} .lv h2 {font-size:42px; font-weight:800; line-height:1.15; margin:12px 0; color:#fff; padding:0;}
.lv p {font-size:16px; opacity:.85; line-height:1.6; margin:0;}
div[data-testid="stForm"] {border:0; padding:0;}
.stButton button[kind="primaryFormSubmit"], div[data-testid="stForm"] button {background:#0f766e; color:#fff; border:0; border-radius:10px; font-weight:600; padding:.6rem 1rem;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def show(fig):
    """Render a Plotly figure full width (works on old and new Streamlit)."""
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def card_title(title, sub=""):
    st.markdown(f'<div class="ct">{title}</div>' + (f'<div class="cs">{sub}</div>' if sub else ""),
                unsafe_allow_html=True)


def style_fig(fig, height=320):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, sans-serif", color="#12302a"),
                      legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0, title=None))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#e0e9e4")
    return fig


# ---------------------------------------------------------------- login
def login_page():
    st.markdown("<style>[data-testid='stSidebar'],[data-testid='collapsedControl']{display:none;}"
                ".block-container{padding-top:3rem !important;}</style>", unsafe_allow_html=True)
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        st.markdown('<div class="lv"><small>MYSURU</small><h2>Environmental Dashboard</h2>'
                    '<p>Explore temperature, humidity and rainfall across urban, semi-urban and rural areas of Mysuru.</p></div>',
                    unsafe_allow_html=True)
    with right:
        st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
        st.markdown("## Welcome back")
        st.caption("Sign in to view the climate analysis.")
        with st.form("login"):
            user = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            ok = st.form_submit_button("Sign In")
        if ok:
            u, p = credentials()
            if hmac.compare_digest(user, u) and hmac.compare_digest(pwd, p):
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Invalid username or password.")


# ---------------------------------------------------------------- dashboard
def dashboard():
    df = load_data()

    with st.sidebar:
        st.markdown('<div class="up"><div class="av">A</div><div><b>Admin</b>Online</div></div>'
                    '<div class="mh">MAIN NAVIGATION</div><div class="nav-on">Dashboard</div>'
                    '<div class="mh">SELECT OPTIONS</div>', unsafe_allow_html=True)
        year = st.selectbox("Select Year", ["All Years", 2024, 2025, 2026], index=3)
        zone = st.selectbox("Select Area Type", ["All Areas"] + ZONES, index=2)
        st.markdown('<div class="mh">ACCOUNT</div>', unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    by_year = df if year == "All Years" else df[df["Year"] == year]
    sel = by_year if zone == "All Areas" else by_year[by_year["Zone Type"] == zone]
    zones_shown = ZONES if zone == "All Areas" else [zone]

    st.markdown('<div class="hero"><h1>MYSURU ENVIRONMENTAL DASHBOARD</h1>'
                '<span>Temperature, humidity and rainfall analysis · 2024 to 2026</span></div>', unsafe_allow_html=True)

    # KPI cards
    svg = ('<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round"><path d="{}"/></svg>')
    k1, k2 = st.columns(2, gap="medium")
    k1.markdown(f'<div class="kpi"><div class="ic" style="background:linear-gradient(135deg,#10b981,#047857)">'
                f'{svg.format("M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z")}</div>'
                f'<div><small>Average Temperature (°C)</small><b>{sel["Avg Temp (C)"].mean():.1f}</b></div></div>',
                unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi"><div class="ic" style="background:linear-gradient(135deg,#38bdf8,#0369a1)">'
                f'{svg.format("M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z")}</div>'
                f'<div><small>Average Humidity (%)</small><b>{sel["Avg Humidity (%)"].mean():.1f}</b></div></div>',
                unsafe_allow_html=True)
    st.write("")

    # 1. temperature by month
    temp = sel.groupby(["Month", "Zone Type"], observed=True)["Avg Temp (C)"].mean().round(2).reset_index()
    with st.container(border=True):
        card_title("How hot is it each month?", "Each line is an area type. Higher line = hotter month.")
        fig = px.line(temp, x="Month", y="Avg Temp (C)", color="Zone Type", markers=True,
                      color_discrete_map=COLORS, category_orders={"Month": MONTHS, "Zone Type": zones_shown})
        fig.update_traces(line=dict(width=3, shape="spline"), marker=dict(size=8, line=dict(width=2, color="#fff")))
        fig.update_yaxes(title="Avg Temp (°C)")
        show(style_fig(fig, 360))

    # 2. donut + rainfall bars (the donut ignores the area filter, like the Power BI report)
    c1, c2 = st.columns([1, 1.5], gap="medium")
    with c1, st.container(border=True):
        card_title("Who gets the most rain?", "A bigger slice means a bigger share of the rain.")
        share = by_year.groupby("Zone Type")["Rainfall (mm)"].sum().reindex(ZONES).reset_index()
        fig = px.pie(share, names="Zone Type", values="Rainfall (mm)", hole=0.62, color="Zone Type",
                     color_discrete_map=COLORS)
        fig.update_traces(marker=dict(line=dict(color="#fff", width=3)), textinfo="percent")
        show(style_fig(fig, 320))
    with c2, st.container(border=True):
        card_title("How much does it rain each month?",
                   "Taller bar = rainier month. Urban = city, Semi-Urban = town outskirts, Rural = villages.")
        rain = sel.groupby(["Month", "Zone Type"], observed=True)["Rainfall (mm)"].mean().round(1).reset_index()
        fig = px.bar(rain, x="Month", y="Rainfall (mm)", color="Zone Type", barmode="group",
                     color_discrete_map=COLORS, category_orders={"Month": MONTHS, "Zone Type": zones_shown})
        fig.update_yaxes(title="Avg Rainfall (mm)")
        show(style_fig(fig, 320))

    # 3. table (also ignores the area filter)
    with st.container(border=True):
        card_title("Hottest and Coolest Temperature by Place")
        t = by_year.groupby(["Location Name", "Zone Type"]).agg(hi=("Max Temp (C)", "max"), lo=("Min Temp (C)", "min"))
        t = t.reset_index().sort_values("hi", ascending=False)
        rows = "".join(f'<tr><td>{r["Location Name"]}</td><td><span class="dot" style="background:{COLORS[r["Zone Type"]]}"></span>'
                       f'{r["Zone Type"]}</td><td>{r.hi:.1f}</td><td>{r.lo:.1f}</td></tr>' for _, r in t.iterrows())
        st.markdown('<table class="t"><thead><tr><th>Location</th><th>Area Type</th><th>Highest °C</th><th>Lowest °C</th>'
                    f'</tr></thead><tbody>{rows}</tbody></table>', unsafe_allow_html=True)

    # 4. key points + conclusions
    p1, p2 = st.columns(2, gap="medium")
    mon = sel.groupby("Month", observed=True).mean(numeric_only=True)
    label = ("all years" if year == "All Years" else str(year)) + ", " + ("all areas" if zone == "All Areas" else f"{zone} areas")
    lead = share.set_index("Zone Type")["Rainfall (mm)"]
    points = [
        f"Showing: <b>{label}</b>. Average temperature is <b>{sel['Avg Temp (C)'].mean():.1f} °C</b>; "
        f"the air is about <b>{sel['Avg Humidity (%)'].mean():.0f}%</b> humid.",
        f"Hottest month: <b>{mon['Avg Temp (C)'].idxmax()}</b> ({mon['Avg Temp (C)'].max():.1f} °C). "
        f"Coolest: <b>{mon['Avg Temp (C)'].idxmin()}</b> ({mon['Avg Temp (C)'].min():.1f} °C).",
        f"Rainiest month: <b>{mon['Rainfall (mm)'].idxmax()}</b> (about {mon['Rainfall (mm)'].max():.0f} mm).",
        f"Stickiest air: <b>{mon['Avg Humidity (%)'].idxmax()}</b>. Driest air: <b>{mon['Avg Humidity (%)'].idxmin()}</b>.",
        f"<b>{lead.idxmax()}</b> areas get the biggest share of rain ({lead.max() / lead.sum() * 100:.0f}%).",
    ]
    zt = df.groupby("Zone Type")["Avg Temp (C)"].mean()
    zr = df.groupby("Zone Type")["Rainfall (mm)"].sum()
    am = df.groupby("Month", observed=True).mean(numeric_only=True)
    dry2 = am["Avg Humidity (%)"].nsmallest(2).index.tolist()
    yt = df.groupby("Year")["Avg Temp (C)"].mean()
    concl = [
        f"Cities are warmer than villages by about {zt['Urban'] - zt['Rural']:.1f} °C.",
        f"Villages get about {zr['Rural'] / zr['Urban']:.1f} times the rain of cities and feel more humid.",
        f"{am['Avg Temp (C)'].idxmax()} is the hottest month. {dry2[0]} and {dry2[1]} are the driest.",
        f"{am['Rainfall (mm)'].idxmax()} is the rainiest month.",
        f"The pattern is almost the same every year (yearly average temperature varies by only {yt.max() - yt.min():.2f} °C).",
    ]
    with p1, st.container(border=True):
        card_title("Key Points")
        st.markdown('<ul class="k">' + "".join(f"<li>{x}</li>" for x in points) + "</ul>", unsafe_allow_html=True)
        st.caption("These points change when you change the year or area type.")
    with p2, st.container(border=True):
        card_title("Conclusions")
        st.markdown('<ul class="k">' + "".join(f"<li>{x}</li>" for x in concl) + "</ul>", unsafe_allow_html=True)

    st.markdown('<div class="foot">Copyright © 2026 Mysuru Environmental Dashboard. All rights reserved.</div>',
                unsafe_allow_html=True)


# ---------------------------------------------------------------- router
if st.session_state.get("auth"):
    dashboard()
else:
    login_page()
