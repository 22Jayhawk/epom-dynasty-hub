import streamlit as st
import pandas as pd
import requests

# --- CONFIG ---
LEAGUE_ID = "1312559657998368768"
SHEET_ID = "1JhDhOf2Qkhl4dCOmv37GZhJNJqy41E5rOvt9IATfmc8"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

# NICKNAME MAPPING
NICKNAMES = {
    "Selkow": "Jared",
    "Dak": "Brodack"
}

st.set_page_config(page_title="EPOM Dynasty Command Center", layout="wide", page_icon="🏈")

# --- DATA ENGINES ---
@st.cache_data(ttl=3600)
def get_player_database():
    # Downloads the full NFL player list (Slow first time, then cached)
    players = requests.get("https://api.sleeper.app/v1/players/nfl").json()
    return {f"{v.get('first_name')} {v.get('last_name')}": k for k, v in players.items()}

@st.cache_data(ttl=600)
def get_live_data():
    try:
        users = requests.get(f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/users").json()
        rosters = requests.get(f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/rosters").json()
        
        # Create user mapping with nicknames
        user_map = {}
        for u in users:
            name = u['display_name']
            clean_name = NICKNAMES.get(name, name) # Swap Jared/Brodack if found
            user_map[u['user_id']] = clean_name
            
        standings = []
        for r in rosters:
            fpts = r['settings']['fpts'] + (r['settings']['fpts_decimal'] / 100)
            standings.append({
                "Manager": user_map.get(r['owner_id'], "Unknown"),
                "Record": f"{r['settings']['wins']}-{r['settings']['losses']}",
                "Points For": round(fpts, 2),
                "Max PF (Potential)": r['settings'].get('ppts', 0)
            })
        return pd.DataFrame(standings).sort_values("Points For", ascending=False)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_sheets():
    return pd.read_excel(SHEET_URL, sheet_name=None)

# --- UI START ---
st.title("🏆 EPOM Dynasty Command Center")
all_data = load_sheets()
player_db = get_player_database()

tab1, tab2, tab3 = st.tabs(["📊 LIVE LEAGUE STANDINGS", "📜 HALL OF RECORDS", "📅 DRAFT RECAPS"])

with tab1:
    st.subheader("Current Season Pulse")
    df_live = get_live_data()
    if not df_live.empty:
        st.dataframe(df_live, use_container_width=True, hide_index=True)
    
with tab2:
    st.subheader("League Legends & Losers")
    history_sheet = "Champs, Chumps and Oh So Close"
    if history_sheet in all_data:
        # Apply Nicknames to History sheet if they appear there
        df_hist = all_data[history_sheet].replace(NICKNAMES)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Historical Draft Picks")
    draft_years = [s for s in all_data.keys() if "20" in s and s != "Champs, Chumps and Oh So Close"]
    selected_year = st.selectbox("Select Year", sorted(draft_years, reverse=True))
    
    if selected_year:
        df_draft = all_data[selected_year].replace(NICKNAMES)
        
        # CREATE CLICKABLE PLAYER LINKS
        def make_link(name):
            p_id = player_db.get(str(name))
            if p_id:
                return f"[{name}](https://sleeper.app/players/{p_id})"
            return name

        # We assume your sheet has a 'Player' column
        if 'Player' in df_draft.columns:
            df_draft['Player'] = df_draft['Player'].apply(make_link)
            st.info("💡 Click a player's name to see their live Sleeper profile and stats.")
            st.markdown(df_draft.to_markdown(index=False), unsafe_allow_html=True)
        else:
            st.dataframe(df_draft, use_container_width=True, hide_index=True)
