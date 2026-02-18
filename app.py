import streamlit as st
import pandas as pd
import requests

# --- LEAGUE SETTINGS ---
LEAGUE_ID = "1312559657998368768"
SHEET_ID = "1JhDhOf2Qkhl4dCOmv37GZhJNJqy41E5rOvt9IATfmc8"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

# Mapping for the boys
NICKNAMES = {"Selkow": "Jared", "Brodack": "Dak"}

st.set_page_config(page_title="EPOM Dynasty", layout="wide", page_icon="🏈")

# --- EXECUTIVE STYLING (The "Un-Tackifier") ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0E1117; }
    .stApp { background: #0E1117; }
    
    /* Card Styling */
    .metric-card {
        background: #161B22; border: 1px solid #30363D; border-radius: 12px;
        padding: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-title { color: #8B949E; font-size: 14px; text-transform: uppercase; font-weight: 700; margin-bottom: 8px; }
    .metric-value { color: #58A6FF; font-size: 28px; font-weight: 800; }
    
    /* Clean Tabs */
    .stTabs [data-baseweb="tab-list"] { background: #161B22; padding: 10px; border-radius: 12px; }
    .stTabs [data-baseweb="tab"] { color: #8B949E; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #58A6FF !important; border-bottom-color: #58A6FF !important; }
    
    /* Table Cleanup */
    [data-testid="stDataFrame"] { border: 1px solid #30363D; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA FETCHING ---
@st.cache_data(ttl=3600)
def get_player_db():
    try:
        data = requests.get("https://api.sleeper.app/v1/players/nfl").json()
        return {f"{v.get('first_name')} {v.get('last_name')}": k for k, v in data.items()}
    except: return {}

@st.cache_data(ttl=600)
def get_league_data():
    try:
        users = requests.get(f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/users").json()
        rosters = requests.get(f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/rosters").json()
        user_map = {u['user_id']: NICKNAMES.get(u['display_name'], u['display_name']) for u in users}
        
        data = []
        for r in rosters:
            pf = r['settings']['fpts'] + (r['settings']['fpts_decimal'] / 100)
            data.append({
                "Manager": user_map.get(r['owner_id'], "Unknown"),
                "Record": f"{r['settings']['wins']}-{r['settings']['losses']}",
                "PF": round(pf, 2),
                "Max PF": r['settings'].get('ppts', 0)
            })
        return pd.DataFrame(data).sort_values("PF", ascending=False)
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def get_sheets():
    return pd.read_excel(SHEET_URL, sheet_name=None)

# --- APP LAYOUT ---
st.markdown("<h1 style='text-align: center; color: white;'>EPOM DYNASTY HUB</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8B949E;'>Hall of Records & Live Command Center</p>", unsafe_allow_html=True)

df_live = get_league_data()
all_sheets = get_sheets()
players = get_player_db()

# Premium Metric Row
if not df_live.empty:
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-title">Points Leader</div><div class="metric-value">{df_live.iloc[0]["Manager"]}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="metric-title">League High PF</div><div class="metric-value">{df_live.iloc[0]["PF"]}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="metric-title">Active Season</div><div class="metric-value">2024-25</div></div>', unsafe_allow_html=True)

st.write("---")

t1, t2, t3 = st.tabs(["📊 STANDINGS", "📜 HISTORY", "📅 DRAFT RECAPS"])

with t1:
    st.dataframe(df_live, use_container_width=True, hide_index=True)

with t2:
    sheet_name = "Champs, Chumps and Oh So Close"
    if sheet_name in all_sheets:
        hist_df = all_sheets[sheet_name].replace(NICKNAMES)
        st.dataframe(hist_df, use_container_width=True, hide_index=True)

with t3:
    draft_years = [s for s in all_sheets.keys() if "20" in s and s != "Champs, Chumps and Oh So Close"]
    col_a, col_b = st.columns([1, 3])
    with col_a:
        year = st.selectbox("Draft Year", sorted(draft_years, reverse=True))
    
    if year:
        df_d = all_sheets[year].replace(NICKNAMES)
        if 'Player' in df_d.columns:
            def link(n):
                pid = players.get(str(n))
                return f'<a href="https://sleeper.app/players/{pid}" target="_blank" style="color: #58A6FF; text-decoration: none;">{n}</a>' if pid else n
            df_d['Player'] = df_d['Player'].apply(link)
            st.write(df_d.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.dataframe(df_d, use_container_width=True, hide_index=True)
