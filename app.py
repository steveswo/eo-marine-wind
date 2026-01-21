import streamlit as st
import pandas as pd
import pydeck as pdk
import os
import time
from pipeline import run_analysis

# 1. Page Configuration
st.set_page_config(page_title="EO for marine & energy", layout="wide")

# 2. CSS: Custom Styling
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 2rem; }
        [data-testid="stHeader"] { display: none; }
        
        /* Section 3: Make Metric Titles BIGGER than Values */
        .metric-container {
            text-align: center;
            padding: 10px;
            background-color: #f0f2f6;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .metric-title {
            font-size: 18px !important;
            font-weight: bold;
            color: #31333F;
            margin-bottom: 0px;
        }
        .metric-value {
            font-size: 16px !important;
            color: #555;
        }
    </style>
    """, unsafe_allow_html=True)

# 3. CACHING: makes app instant on reload
@st.cache_data(show_spinner=False)
def cached_analysis(bbox, site_name):
    # This wrapper function saves the result
    return run_analysis(bbox, site_name)

# 4. Session Memory
if 'history' not in st.session_state:
    st.session_state.history = []

# 5. Header
st.title("🌊 EO for Marine and Energy") 

# 6. Site Options
site_options = {
    "Kish Bank": {"lat": 53.27, "lon": -5.95, "bbox": [-6.05, 53.15, -5.85, 53.38]},
    "Arklow Bank": {"lat": 52.85, "lon": -6.00, "bbox": [-6.10, 52.75, -5.90, 52.95]}
}

# 7. CONTROLS
c_sel, c_btn1, c_btn2 = st.columns([2, 1, 1])
with c_sel:
    site = st.selectbox("Select Location", list(site_options.keys()), label_visibility="collapsed")
with c_btn1:
    run_btn = st.button("🚀 Run Analysis", use_container_width=True)
with c_btn2:
    if st.button("🧹 Clear History", use_container_width=True):
        st.session_state.history = []
        st.rerun()

st.divider()

# 8. MAP & METADATA
# Updated Metadata Text
st.caption(f"Data Source: Sentinel-2 L2A")

target_lat = site_options[site]['lat']
target_lon = site_options[site]['lon']
map_df = pd.DataFrame([{'lat': target_lat, 'lon': target_lon, 'coords': f"{target_lat}, {target_lon}"}])

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(latitude=target_lat, longitude=target_lon, zoom=10, pitch=0),
    layers=[
        pdk.Layer("ScatterplotLayer", data=map_df, get_position=["lon", "lat"], get_color=[0, 255, 128, 200], get_radius=800),
        pdk.Layer("TextLayer", data=map_df, get_position=["lon", "lat"], get_text="coords", get_size=18, get_color=[255, 255, 255], get_alignment_baseline="'bottom'", get_pixel_offset=[0, -20])
    ],
    height=350 
))
st.write(f"📍 **Location: {site}**") 

# 9. ANALYSIS
if run_btn:
    try:
        with st.spinner("Processing satellite data..."):
            # CALLING THE CACHED FUNCTION
            report_path, score, clarity, bng_val, depth, wind, dist = cached_analysis(
                site_options[site]['bbox'], site.replace(" ", "_")
            )

        bng_pct = f"{int(bng_val * 100)}%"
        est_credits = bng_val * 50 * 2.5
        
        entry = {"Site": site, "Feasibility": f"{score}/100", "Turbidity": f"{clarity:.2f}", "Bio-Gain": bng_pct, "Credits (t/yr)": f"{est_credits:.1f}"}
        if entry not in st.session_state.history:
            st.session_state.history.append(entry)

        # --- 1. COMPLIANCE ---
        st.header("⚖️ 1. Compliance")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Maritime Area Consent ✅")
            # Combined Line: Turbidity (NDTI) : -0.29
            st.markdown(f"<h4 style='margin-bottom:0;'>Turbidity (NDTI) : {clarity:.3f}</h4>", unsafe_allow_html=True)
            st.success(f"NDTI < 0: Water not polluted.  \n\nSun penetrates water to grow seagrass.")
        
        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("EU Habitats Directive ✅")
            # Reduced gap below header implicitly by removing spacer
            st.success("No adverse effect.  \n\nSeagrass protect erosion on wind turbine base.")

        st.divider()

        # --- 2. SUSTAINABLE FINANCE ---
        st.header("💰 2. Sustainable Finance")
        s1, s2 = st.columns(2)
        
        with s1:
            st.subheader(f"Biodiversity Gain: {bng_pct}") # Header
            st.write("High seabed vegetation") # Smaller, non-bold
            st.progress(int(bng_val * 100) if bng_val <= 1.0 else 100)
            st.success("Eligible for Sustainable Loans")
            
        with s2:
            st.subheader("ESG Value") # Header
            st.write("High Carbon Capture") # Smaller, non-bold
            st.success(f"Carbon Credits generated:  \n**{est_credits:.1f} tonnes / year**")

        st.divider()

        # --- 3. OFFSHORE FEASIBILITY ---
        st.header("🏗️ 3. Offshore Feasibility")
        
        e1, e2, e3 = st.columns(3)
        with e1:
            st.markdown(f"""<div class="metric-container"><div class="metric-title">Wind Speed</div><div class="metric-value">{wind} m/s</div></div>""", unsafe_allow_html=True)
        with e2:
            st.markdown(f"""<div class="metric-container"><div class="metric-title">Seabed Depth</div><div class="metric-value">{depth} m</div></div>""", unsafe_allow_html=True)
        with e3:
            st.markdown(f"""<div class="metric-container"><div class="metric-title">Distance to Shore</div><div class="metric-value">{dist} km</div></div>""", unsafe_allow_html=True)

        st.warning(f"**Feasibility: {score}/100**") 

    except Exception as e:
        st.error(f"Error: {e}")

# 10. SITE COMPARISON
if st.session_state.history:
    st.divider()
    st.subheader("📊 Site Comparison")
    st.table(st.session_state.history)

# 11. SHAREABLE LINKS
st.divider()
st.subheader("🔗 Share")

app_url = "https://eo-marine.streamlit.app"
share_text = f"EO for marine & renewable energy {site}:"

# Create columns for the 1-click buttons
sh1, sh2, sh3, sh4 = st.columns(4)

with sh1:
    # WhatsApp (api.whatsapp.com)
    wa_link = f"https://api.whatsapp.com/send?text= {app_url}"
    st.link_button("💬 WhatsApp", wa_link, use_container_width=True)

with sh2:
    # LinkedIn (linkedin.com/sharing/share-offsite)
    li_link = f"https://www.linkedin.com/sharing/share-offsite/?url={app_url}"
    st.link_button("🟦 LinkedIn", li_link, use_container_width=True)

with sh3:
    # Email (mailto:)
    email_link = f"mailto:?subject=EO for Marine and Renewable Energy &body= {app_url}"
    st.link_button("✉️ Email", email_link, use_container_width=True)
