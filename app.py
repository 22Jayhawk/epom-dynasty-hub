import streamlit as st
import pandas as pd
import requests

# --- CORE CONFIG ---
LEAGUE_ID = "1312559657998368768"
SHEET_ID = "1JhDhOf2Qkhl4dCOmv37GZhJNJqy41E5rOvt9IATfmc8"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
NICKNAMES = {"Selkow": "Jared", "Brodack": "Dak"}

st.set_page_config(page_title="EPOM Dynasty", layout="wide")

# --- CUSTOM CSS (THE DESIGN OVERHAUL) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #050505; }
    .stApp { background: #050505; }
    
    /* GLASS CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    /* STANDINGS ROW */
    .standings-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 24px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        margin-bottom: 8px;
        transition: 0.3s ease;
    }
    .standings-row:hover { background: rgba(255, 255, 255, 0.05); border: 1px solid #4F46E5; }
    
    .rank-circle {
        height: 32px; width: 32px; border-radius: 50%;
        background: #4F46E5; display: flex; align-items: center;
        justify-content: center; font-weight: 800; font-size: 14px; margin-right: 15px;
    }
    
    /* TYPOGRAPHY */
    .hero-text { font-size: 4rem; font-weight: 800; letter-spacing: -2px; color: white; margin-bottom: 0; }
    .accent-text { color: #4F46E5; font-weight: 700; }
    .label { color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }
    .val { color: #f8fafc; font-size: 18px; font-weight: 700; }

    /* HIDE STREAMLIT BOREDOM */
    [data-testid="stHeader"], [data-testid="stFooter"] { display: none; }
    .stTabs [data-baseweb="tab-list"] { background: transparent; gap: 30px; }
    .stTabs [data-baseweb="tab"] { background: transparent; border: none; font-size: 18px; color: #64748b; }
    .stTabs [aria-selected="true"] { color: white !important; font-weight: 700; border-bottom: 2px solid #4F46E5 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA ---
@st.cache_data(ttl=600)
def load_league():
    try:
        u = requests.get(f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/users").json()
        r = requests.get(f"https://api.sleeper.app/v1/league/{LEAGUE_ID}/rosters").json()
        umap = {user['user_id']: NICKNAMES.get(user['display_name'], user['display_name']) for user in u}
        data = []
        for ros in r:
            pf = ros['settings']['fpts'] + (ros['settings']['fpts_decimal'] / 100)
            data.append({"Manager": umap.get(ros['owner_id']), "Record": f"{ros['settings']['wins']}-{ros['settings']['losses']}", "PF": round(pf, 1)})
        return sorted(data, key=lambda x: x['PF'], reverse=True)
    except: return []

@st.cache_data(ttl=60)
def load_sheets():
    return pd.read_excel(SHEET_URL, sheet_name=None)

# --- APP ---
st.markdown('<h1 class="hero-text">EPOM<span class="accent-text">.</span></h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #64748b; margin-left: 5px;">DYNASTY LEAGUE HUB</p>', unsafe_allow_html=True)

data = load_league()
sheets = load_sheets()

# TOP BAR CARDS
if data:
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="glass-card"><p class="label">Points Leader</p><p class="val">{data[0]["Manager"]}</p></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="glass-card"><p class="label">Total PF</p><p class="val">{data[0]["PF"]}</p></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="glass-card"><p class="label">Season</p><p class="val">2025/26</p></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Standings", "History", "Drafts"])

with tab1:
    st.write(" ")
    for i, m in enumerate(data, 1):
        st.markdown(f"""
            <div class="standings-row">
                <div style="display: flex; align-items: center;">
                    <div class="rank-circle">{i}</div>
                    <div class="val">{m['Manager']}</div>
                </div>
                <div style="display: flex; gap: 40px;">
                    <div style="text-align: right;"><p class="label">Record</p><p class="val">{m['Record']}</p></div>
                    <div style="text-align: right;"><p class="label">PF</p><p class="val" style="color:#4F46E5;">{m['PF']}</p></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with tab2:
    sn = "Champs, Chumps and Oh So Close"
    if sn in sheets:
        # Style the dataframe minimally to keep the look
        st.dataframe(sheets[sn].replace(NICKNAMES), use_container_width=True, hide_index=True)

with tab3:
    years = [s for s in sheets.keys() if "20" in s and s != sn]
    y = st.selectbox("Draft Year", sorted(years, reverse=True))
    if y:
        st.dataframe(sheets[y].replace(NICKNAMES), use_container_width=True, hide_index=True)
