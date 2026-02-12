import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Baller Rebound", layout="wide", page_icon="🏀")

# --- 2. THEMES & STYLING ---
st.markdown("""
    <style>
    .metric-card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #333; }
    stMetric { background-color: #0e1117; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PERSISTENT DATA (Session State) ---
if 'meal_log' not in st.session_state:
    st.session_state.meal_log = []
if 'weight_data' not in st.session_state:
    st.session_state.weight_data = pd.DataFrame(columns=["Date", "Weight"])

# --- 4. APP LAYOUT ---
st.title("🏀 Baller Rebound: Manual Tracker")
st.info("No API Key connected. Manual logging mode active.")

tab1, tab2, tab3 = st.tabs(["🍎 Daily Nutrition", "🏋️ Workout Library", "📈 Progress Tracker"])

# --- TAB 1: NUTRITION ---
with tab1:
    # Math for the day
    total_p = sum(m['Protein'] for m in st.session_state.meal_log)
    total_c = sum(m['Carbs'] for m in st.session_state.meal_log)
    total_f = sum(m['Fats'] for m in st.session_state.meal_log)
    total_cal = (total_p * 4) + (total_c * 4) + (total_f * 9)

    # Dashboard
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Calories", f"{total_cal}", "Goal: 2800")
    c2.metric("Protein", f"{total_p}g", "Goal: 180g")
    c3.metric("Carbs", f"{total_c}g", "Goal: 350g")
    c4.metric("Fats", f"{total_f}g", "Goal: 80g")

    st.divider()

    # Manual Entry instead of AI Scan
    with st.form("manual_meal"):
        st.write("### Log Your Food")
        name = st.text_input("Meal Name (e.g., Post-Workout Shake)")
        col_p, col_c, col_f = st.columns(3)
        p = col_p.number_input("Protein (g)", 0)
        c = col_c.number_input("Carbs (g)", 0)
        f = col_f.number_input("Fats (g)", 0)
        if st.form_submit_button("Add Meal"):
            st.session_state.meal_log.append({"Meal": name, "Protein": p, "Carbs": c, "Fats": f})
            st.rerun()

    if st.session_state.meal_log:
        st.write("### Today's Meals")
        st.table(pd.DataFrame(st.session_state.meal_log))
        if st.button("Reset Day"):
            st.session_state.meal_log = []
            st.rerun()

# --- TAB 2: WORKOUT LIBRARY ---
with tab2:
    st.header("Return-to-Play Programs")
    st.write("Since AI is offline, choose a pre-set routine for your 89kg frame:")
    
    plan = st.selectbox("Select Focus", ["SI Joint Stability", "Achilles Strengthening", "Shooting Mechanics"])
    
    if plan == "SI Joint Stability":
        st.warning("Focus: Glute activation and core stability to protect the lower back.")
        st.markdown("""
        1. **Glute Bridges:** 3 sets x 15 reps
        2. **Bird-Dogs:** 3 sets x 10 reps per side
        3. **Deadbugs:** 3 sets x 12 reps
        4. **Plank:** 3 sets x 45 seconds
        """)
    elif plan == "Achilles Strengthening":
        st.warning("Focus: Eccentric loading to rebuild tendon durability.")
        st.markdown("""
        1. **Slow Heel Drops:** 3 sets x 15 reps (off a step)
        2. **Isometric Calf Hold:** 4 sets x 30 seconds
        3. **Tibialis Raises:** 3 sets x 20 reps
        """)
    else:
        st.markdown("""
        1. **Form Shooting:** 50 makes from 3 feet
        2. **Elbow Jumper:** 10 makes from each side
        3. **Free Throws:** 2 sets of 10
        """)

# --- TAB 3: PROGRESS ---
with tab3:
    st.header("Weight History")
    w_val = st.number_input("Today's Weight (kg)", 89.0)
    if st.button("Log Progress"):
        new_w = pd.DataFrame({"Date": [datetime.date.today()], "Weight": [w_val]})
        st.session_state.weight_data = pd.concat([st.session_state.weight_data, new_w])
    
    if not st.session_state.weight_data.empty:
        st.plotly_chart(px.line(st.session_state.weight_data, x="Date", y="Weight", markers=True), use_container_width=True)
