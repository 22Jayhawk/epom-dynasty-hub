import streamlit as st
import pandas as pd
import requests

# --- SETTINGS ---
LEAGUE_ID = "1312559657998368768"
SHEET_ID = "1JhDhOf2Qkhl4dCOmv37GZhJNJqy41E5rOvt9IATfmc8"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
NICKNAMES = {"Selkow": "Jared", "Brodack": "Dak"}

st.set_page_config(page_title="EPOM Hub", layout="wide")

# --- CLEAN DESIGN CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    [data-testid="stMetric"] { 
        background-color: #161B22; 
        border: 1px solid #30363D; 
        padding: 15px; 
        border-radius: 10px; 
    }
    .manager-row {
        display: flex;
        justify-content: space-between;
        padding: 15px;
        margin: 10px 0;
        background: #1C2128;
        border-left: 5px solid #58A6FF;
        border-radius: 8px;
    }
    .name-text { font-size: 20px; font-weight: bold; color: #F0F6FC; }
    .stat-text { color: #8B949E; font-size: 14px; }
    .val-text { color: #58A6FF; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# --- SECURE DATA FETCHING ---
@st.cache_data(ttl=600)
def get_data():
    try:
        u = requests.get(f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/users").json()
        r = requests.get(f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/rosters").json()
        umap = {user['user_id']: NICKNAMES.get(user['display_name'], user['display_name']) for user in u}
        
        standings = []
        for ros in r:
            pf = ros['settings']['fpts'] + (ros['settings']['fpts_decimal'] / 100)
            standings.append({
                "Manager": umap.get(ros['owner_id'], "Unknown"),
                "Record": f"{ros['settings']['wins']}-{ros['settings']['losses']}",
                "PF": round(pf, 2)
            })
        return sorted(standings, key=lambda x: x['PF'], reverse=True)
    except:
        return []

@st.cache_data(ttl=60)
def get_sheets():
    try: return pd.read_excel(SHEET_URL, sheet_name=None)
    except: return {}

# --- BUILD UI ---
st.title("🏆 EPOM DYNASTY HUB")

data = get_data()
sheets = get_sheets()

if data:
    # Top 3 Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Points Leader", data[0]['Manager'], f"{data[0]['PF']} PF")
    m2.metric("Second Place", data[1]['Manager'], f"{data[1]['PF']} PF")
    m3.metric("League Median", f"{round(sum(d['PF'] for d in data)/len(data), 1)}")

    st.write("---")

    t1, t2, t3 = st.tabs(["🔥 STANDINGS", "📜 HISTORY", "📅 DRAFTS"])

    with t1:
        for entry in data:
            st.markdown(f"""
                <div class="manager-row">
                    <div class="name-text">{entry['Manager']}</div>
                    <div style="display: flex; gap: 30px;">
                        <div style="text-align: center;"><div class="stat-text">RECORD</div><div class="val-text">{entry['Record']}</div></div>
                        <div style="text-align: center;"><div class="stat-text">POINTS</div><div class="val-text">{entry['PF']}</div></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with t2:
        sn = "Champs, Chumps and Oh So Close"
        if sn in sheets:
            st.dataframe(sheets[sn].replace(NICKNAMES), use_container_width=True, hide_index=True)

    with t3:
        years = [s for s in sheets.keys() if "20" in s and s != sn]
        y = st.selectbox("Select Year", sorted(years, reverse=True))
        if y:
            st.dataframe(sheets[y].replace(NICKNAMES), use_container_width=True, hide_index=True)
else:
    st.error("League data failed to load. Check Sleeper ID.")
