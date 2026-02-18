import streamlit as st
import pandas as pd
import requests

# --- CONFIG ---
LEAGUE_ID = "1312559657998368768"
SHEET_ID = "1JhDhOf2Qkhl4dCOmv37GZhJNJqy41E5rOvt9IATfmc8"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

st.set_page_config(page_title="EPOM Dynasty Hall of Records", layout="wide", page_icon="🏆")

# --- DATA FETCHING ---
@st.cache_data(ttl=600)
def get_sleeper_data():
    try:
        users = requests.get(f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/users").json()
        rosters = requests.get(f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/rosters").json()
        user_map = {u['user_id']: u['display_name'] for u in users}
        standings = []
        for r in rosters:
            standings.append({
                "Manager": user_map.get(r['owner_id'], "Unknown"),
                "W-L": f"{r['settings']['wins']}-{r['settings']['losses']}",
                "Points For": r['settings']['fpts'] + (r['settings']['fpts_decimal'] / 100),
                "Max PF": r['settings'].get('ppts', 0)
            })
        return pd.DataFrame(standings).sort_values("Points For", ascending=False)
    except:
        return pd.DataFrame({"Error": ["Connecting to Sleeper..."]})

@st.cache_data(ttl=60)
def load_all_sheets():
    # Reads all sheets from your Google Sheet link
    return pd.read_excel(SHEET_URL, sheet_name=None)

# --- UI LAYOUT ---
st.title("🏆 EPOM Dynasty Hall of Records")

# Load everything once
all_sheets = load_all_sheets()

tab1, tab2, tab3 = st.tabs(["📊 Live Standings", "📜 League History", "📅 Draft Archive"])

with tab1:
    st.header("Current Season (Live Sleeper)")
    st.dataframe(get_sleeper_data(), use_container_width=True)

with tab2:
    st.header("Champs, Chumps and Oh So Close")
    sheet_name = "Champs, Chumps and Oh So Close"
    if sheet_name in all_sheets:
        st.dataframe(all_sheets[sheet_name], use_container_width=True)
    else:
        st.error(f"Could not find sheet named: {sheet_name}")

with tab3:
    st.header("Historical Drafts")
    # Finds all years (like 2022-23, 2023-24) automatically
    draft_years = [s for s in all_sheets.keys() if "20" in s and s != sheet_name]
    selected_year = st.selectbox("Select Draft Year", sorted(draft_years, reverse=True))
    
    if selected_year:
        st.dataframe(all_sheets[selected_year], use_container_width=True)
