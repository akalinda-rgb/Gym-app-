import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from PIL import Image
import datetime
import io
import json

# --- 1. AI CONFIGURATION ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ AI Key not found in Secrets. Please add GEMINI_API_KEY.")
    st.stop()

# --- 2. SETTINGS & STYLING ---
st.set_page_config(page_title="BallerPro Fitness", layout="wide", page_icon="🏀")
st.markdown("""
    <style>
    .metric-card { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE (The "Database") ---
if 'food_log' not in st.session_state:
    st.session_state.food_log = []
if 'weight_history' not in st.session_state:
    st.session_state.weight_history = pd.DataFrame(columns=["Date", "Weight"])

# --- 4. CALCULATE GOALS ---
# Basketball Performance Target: High Protein, Moderate Carbs
daily_cal_goal = 2800 
p_goal, c_goal, f_goal = 180, 350, 80

# --- 5. APP LAYOUT ---
st.title("🏀 BallerPro Performance Tracker")
st.caption("Professional Grade Nutrition & Training for Basketball Comebacks")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🍎 Nutrition Logger", "🏋️ Workout Coach", "📉 History"])

# --- TAB 1: DASHBOARD (MyFitnessPal Style) ---
with tab1:
    st.subheader("Today's Summary")
    
    # Calculate Totals
    total_p = sum(item['Protein'] for item in st.session_state.food_log)
    total_c = sum(item['Carbs'] for item in st.session_state.food_log)
    total_f = sum(item['Fats'] for item in st.session_state.food_log)
    total_cal = (total_p * 4) + (total_c * 4) + (total_f * 9)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Calories", f"{total_cal} / {daily_cal_goal}", f"{daily_cal_goal - total_cal} left")
    col2.metric("Protein", f"{total_p}g", f"{p_goal - total_p}g left")
    col3.metric("Carbs", f"{total_c}g", f"{c_goal - total_c}g left")
    col4.metric("Fats", f"{total_f}g", f"{f_goal - total_f}g left")

    # Progress Bars
    st.progress(min(total_cal / daily_cal_goal, 1.0))
    
    if st.session_state.food_log:
        st.write("### Today's Meals")
        st.table(pd.DataFrame(st.session_state.food_log))

# --- TAB 2: NUTRITION LOGGER ---
with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### 📸 AI Photo Scan")
        cam_file = st.file_uploader("Snap a meal or label", type=['jpg', 'jpeg', 'png'])
        if cam_file:
            st.image(cam_file, width=250)
            if st.button("Identify Meal & Macros"):
                with st.spinner("AI is analyzing..."):
                    prompt = "Identify this food and estimate Protein, Carbs, and Fats in grams. Return ONLY JSON: {'Meal': 'name', 'Protein': 0, 'Carbs': 0, 'Fats': 0}"
                    response = model.generate_content([prompt, Image.open(cam_file)])
                    try:
                        data = json.loads(response.text.strip('```json').strip())
                        st.session_state.food_log.append(data)
                        st.success(f"Added {data['Meal']}!")
                        st.rerun()
                    except:
                        st.error("AI couldn't read the image. Try manual entry.")

    with col_b:
        st.write("### ✍️ Manual Entry")
        with st.form("manual_meal"):
            m_name = st.text_input("Meal Name")
            m_p = st.number_input("Protein (g)", 0)
            m_c = st.number_input("Carbs (g)", 0)
            m_f = st.number_input("Fats (g)", 0)
            if st.form_submit_button("Add Meal"):
                st.session_state.food_log.append({"Meal": m_name, "Protein": m_p, "Carbs": m_c, "Fats": m_f})
                st.rerun()

# --- TAB 3: WORKOUT COACH ---
with tab3:
    st.write("### 🏃‍♂️ Return-to-Play Training")
    weight = st.number_input("Current Weight (kg)", 89.0)
    focus = st.selectbox("Today's Focus", ["Foundation (Legs/SI Joint)", "Skill Work (Shooting/Handles)", "Conditioning", "Full Body Strength"])
    
    if st.button("Generate Dynamic Workout"):
        with st.spinner("Consulting Pro Coach..."):
            workout_prompt = f"Create a detailed basketball workout for an 89kg athlete focusing on {focus}. Must be safe for Achilles/SI Joint. Include sets, reps, and rest times."
            res = model.generate_content(workout_prompt)
            st.markdown(res.text)

# --- TAB 4: HISTORY & WEIGHT ---
with tab4:
    st.header("Weight Tracker")
    w_val = st.number_input("Log Weight", value=weight)
    if st.button("Save Weight"):
        new_w = pd.DataFrame({"Date": [datetime.date.today().strftime('%Y-%m-%d')], "Weight": [w_val]})
        st.session_state.weight_history = pd.concat([st.session_state.weight_history, new_w]).drop_duplicates()
    
    if not st.session_state.weight_history.empty:
        fig = px.line(st.session_state.weight_history, x="Date", y="Weight", title="Weight Over Time", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    if st.button("Clear All Data"):
        st.session_state.food_log = []
        st.rerun()
