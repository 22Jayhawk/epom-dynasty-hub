import streamlit as st
import pandas as pd
import requests

# --- SETTINGS & MAPPING ---
LEAGUE_ID = "1312559657998368768"
SHEET_ID = "1JhDhOf2Qkhl4dCOmv37GZhJNJqy41E5rOvt9IATfmc8"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
NICKNAMES = {"Selkow": "Jared", "Brodack": "Dak"}

st.set_page_config(page_title="EPOM Dynasty Hub", layout="wide", page_icon="🏈")

# --- PRO SPORTS UI DESIGN (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Rajdhani:wght@300;500;700&display=swap');
    
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; }
    
    /* Title Styling */
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 3rem; font-weight: 900; background: linear-gradient(to right, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0.5rem; }
    
    /* Modern Manager Cards */
    .manager-card {
        background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(148, 163, 184, 0.2);
        padding: 20px; border-radius: 16px; margin-bottom: 15px; transition: 0.3s;
        display: flex; justify-content: space-between; align-items: center;
    }
    .manager-card:hover { transform: scale(1.02); border-color: #60a5fa; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4); }
    .manager-name { font-size: 1.5rem; font-weight: 700; font-family: 'Rajdhani', sans-serif; color: #f1f5f9; }
    .stat-box { text-align: right; }
    .stat-label { font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 1px; }
    .stat-value { font-size: 1.25rem; font-weight: 700; color: #38bdf8; }

    /* Draft Recap Table Design */
    .draft-container { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }
    th { color: #94a3b8 !important; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; }
    .player-link { color: #38bdf8 !important; text-decoration: none !important; font-weight: 600; }
    .player-link:hover { color: #818cf8 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA ENGINES ---
@st.cache_data(ttl=600)
def fetch_standings():
    try:
        users = requests.get(f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/users").json()
        rosters = requests.get(f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/rosters").json()
        user_map = {u['user_id']: NICKNAMES.get(u['display_name'], u['display_name']) for u in users}
        data = []
        for r in rosters:
            pf = r['settings']['fpts'] + (r['settings']['fpts_decimal'] / 100)
            data.append({"name": user_map.get(r['owner_id']), "record": f"{r['settings']['wins']}-{r['settings']['losses']}", "pf": round(pf, 1)})
        return sorted(data, key=lambda x: x['pf'], reverse=True)
    except: return []

@st.cache_data(ttl=60)
def fetch_sheets():
    return pd.read_excel(SHEET_URL, sheet_name=None)

# --- THE UI ---
st.markdown('<h1 class="main-title">EPOM DYNASTY</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #94a3b8;">Sleeper Integrated Hall of Records</p>', unsafe_allow_html=True)

all_sheets = fetch_sheets()
standings = fetch_standings()

tab1, tab2, tab3 = st.tabs(["🔥 LIVE STANDINGS", "🎖️ HALL OF FAME", "📦 DRAFT ARCHIVE"])

with tab1:
    st.write(" ")
    for rank, entry in enumerate(standings, 1):
        st.markdown(f"""
            <div class="manager-card">
                <div>
                    <span style="color: #64748b; margin-right: 15px;">#{rank}</span>
                    <span class="manager-name">{entry['name']}</span>
                </div>
                <div style="display: flex; gap: 40px;">
                    <div class="stat-box"><div class="stat-label">Record</div><div class="stat-value">{entry['record']}</div></div>
                    <div class="stat-box"><div class="stat-label">Points For</div><div class="stat-value" style="color: #
