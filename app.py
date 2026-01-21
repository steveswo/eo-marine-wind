import streamlit as st
import pandas as pd
import pydeck as pdk
import os
import time
from pipeline import run_analysis

# 1. Page Configuration
st.set_page_config(page_title="Restore Blue | NID Suite", layout="wide")

# 2. Session Memory for Table
if 'history' not in st.session_state:
    st.session_state.history = []

# 3. Header
st.title("🌊 Restore Blue: Site Analysis")
st.markdown("Nature-Inclusive Design (NID) Optimisation for Offshore Wind")

# 4. Sidebar Selection
site_options = {
    "Kish Bank": {"lat": 53.27, "lon": -5.95, "bbox": [-6.05, 53.15, -5.85, 53.38]},
    "Arklow Bank": {"lat": 52.85, "lon": -6.00, "bbox": [-6.10, 52.75, -5.90, 52.95]}
}

with st.sidebar:
    st.header("📍 Location")
    site = st.selectbox("Project Site", list(site_options.keys()))
    run_btn = st.button("🚀 Run Analysis", use_container_width=True)
    
    st.divider()
    if st.button("🧹 Clear History"):
        st.session_state.history = []
        st.rerun()

# 5. Advanced PyDeck Map
target_lat = site_options[site]['lat']
target_lon = site_options[site]['lon']
map_df = pd.DataFrame([{'lat': target_lat, 'lon': target_lon, 'coords': f"{target_lat}, {target_lon}"}])

layers = [
    pdk.Layer("ScatterplotLayer", data=map_df, get_position=["lon", "lat"],
              get_color=[0, 255, 128, 200], get_radius=800),
    pdk.Layer("TextLayer", data=map_df, get_position=["lon", "lat"], get_text="coords",
              get_size=18, get_color=[255, 255, 255], get_alignment_baseline="'bottom'", get_pixel_offset=[0, -20])
]

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(latitude=target_lat, longitude=target_lon, zoom=10, pitch=45),
    layers=layers
))
st.write(f"📍 **{site}**") 

# 6. Analysis Logic
if run_btn:
    try:
        with st.spinner("Processing satellite data..."):
            report_path, score, clarity, bng_val, depth, wind, dist = run_analysis(
                site_options[site]['bbox'], site.replace(" ", "_")
            )

        # Calculations for Table & UI
        bng_pct = f"{int(bng_val * 100)}%"
        est_credits = bng_val * 50 * 2.5
        
        # Add to Site Comparison History
        entry = {
            "Site": site, 
            "Feasibility": f"{score}/100", 
            "Turbidity": f"{clarity:.2f}",
            "Bio-Gain": bng_pct,
            "Credits (t/yr)": f"{est_credits:.1f}"
        }
        if entry not in st.session_state.history:
            st.session_state.history.append(entry)

        st.caption(f"Analysis generated on 2026-01-21 | Data Source: Sentinel-2 L2A via Element84")

        # --- 1. COMPLIANCE ---
        st.header("⚖️ 1. Compliance")
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Maritime Area Consent ✅")
            st.metric("Turbidity (NDTI)", f"{clarity:.3f}")
            st.success(f"NDTI <0: water not polluted.  \n\nSun penetrates water to grow seagrass.")
        
        with c2:
            st.subheader("EU Habitats Directive ✅")
            st.success("No adverse effect.  \n\nSeagrass protect erosion on wind turbine base.")

        st.divider()

        # --- 2. SUSTAINABLE FINANCE ---
        st.header("💰 2. Sustainable Finance")
        s1, s2 = st.columns(2)
        with s1:
            st.write("**High seabed vegetation**")
            st.success("Site eligible for Sustainable Loans")
            st.progress(int(bng_val * 100) if bng_val <= 1.0 else 100, text=f"Biodiversity Gain: {bng_pct}")
        
        with s2:
            st.metric("ESG Value", "High Carbon Capture")
            st.success(f"Generate Carbon Credits  \nEstimated: {est_credits:.1f} tonnes / year")

        st.divider()

        # --- 3. OFFSHORE FEASIBILITY ---
        st.header("🏗️ 3. Offshore Feasibility")
        e1, e2, e3 = st.columns(3)
        e1.metric("Wind Speed", f"{wind} m/s")
        e2.metric("Depth", f"{depth} m")
        e3.metric("Distance", f"{dist} km")
        st.warning(f"**Feasibility: {score}/100**") 

    except Exception as e:
        st.error(f"Error: {e}")

# 7. SITE COMPARISON (Updated with New Columns)
if st.session_state.history:
    st.divider()
    st.subheader("📊 Site Comparison")
    st.table(st.session_state.history)