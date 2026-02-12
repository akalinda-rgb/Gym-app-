import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from PIL import Image
import datetime
import io
import json

# --- 1. AI SETUP ---
# To make this work, enter your Gemini API Key from aistudio.google.com
API_KEY = "YOUR_GEMINI_API_KEY_HERE" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Baller Rebound AI", layout="wide", page_icon="🏀")

# Custom CSS for a dark "Basketball Court" aesthetic
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. STATE MANAGEMENT ---
if 'weight_log' not in st.session_state:
    st.session_state.weight_log = pd.DataFrame(columns=["Date", "Weight"])
if 'macros' not in st.session_state:
    st.session_state.macros = {"Calories": 0, "Protein": 0, "Carbs": 0, "Fats": 0}
if 'workout_plan' not in st.session_state:
    st.session_state.workout_plan = "Your customized plan will appear here..."

# --- 4. AI LOGIC FUNCTIONS ---
def get_macros_from_image(image_bytes):
    prompt = """Analyze this nutrition label. Return ONLY a JSON object with: 
    {"Calories": int, "Protein": int, "Carbs": int, "Fats": int}. 
    If you cannot find a value, use 0."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        response = model.generate_content([prompt, img])
        # Cleaning the AI response to ensure it's valid JSON
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        return None

def get_basketball_plan(weight, days, years, refinement):
    prompt = f"""
    Create a professional basketball return-to-play workout for an athlete weighing {weight}kg.
    The athlete has not played for {years} years.
    Schedule: {', '.join(days)}.
    Focus on: Achilles and SI Joint health, vertical jumping foundation, and shooting rhythm.
    Incorporate this user feedback: {refinement}
    Provide a Week 1 to Week 4 progression in Markdown format.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Error connecting to AI Coach. Please check your API key."

# --- 5. APP LAYOUT ---
st.title("🏀 BALLER REBOUND")
st.subheader("AI-Driven Road to the Court")

tab1, tab2, tab3 = st.tabs(["🍎 Macro Scanner", "📅 AI Training Plan", "📈 Progress Reports"])

# --- TAB 1: MACROS ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 📸 Scan Label")
        uploaded_file = st.file_uploader("Upload nutrition label", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            img_bytes = uploaded_file.getvalue()
            st.image(img_bytes, width=300)
            if st.button("Extract Macros"):
                with st.spinner("AI analyzing..."):
                    data = get_macros_from_image(img_bytes)
                    if data:
                        st.session_state.macros.update(data)
                        st.success("Macros Logged!")
    
    with col2:
        st.write("### 📊 Daily Totals")
        st.write(st.session_state.macros)
        df = pd.DataFrame({
            "Nutrient": ["Protein", "Carbs", "Fats"],
            "Grams": [st.session_state.macros['Protein'], st.session_state.macros['Carbs'], st.session_state.macros['Fats']]
        })
        fig = px.pie(df, values='Grams', names='Nutrient', title="Macro Split", color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig)

# --- TAB 2: WORKOUTS ---
with tab2:
    st.sidebar.header("Player Stats")
    w_input = st.sidebar.number_input("Weight (kg)", value=89.0)
    d_input = st.sidebar.multiselect("Active Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], default=["Mon", "Wed", "Fri"])
    y_input = st.sidebar.slider("Years Off", 1, 10, 2)
    
    st.write("### 🏀 Your Custom Training Program")
    refine = st.text_input("Refine your workout (e.g. 'I have access to a full gym' or 'Fix my jumper')")
    
    if st.button("Generate/Update Plan"):
        with st.spinner("Consulting AI Coach..."):
            st.session_state.workout_plan = get_basketball_plan(w_input, d_input, y_input, refine)
    
    st.markdown("---")
    st.markdown(st.session_state.workout_plan)

# --- TAB 3: PROGRESS ---
with tab3:
    st.write("### 📈 Weight & Performance Tracking")
    new_weight = st.number_input("Input Today's Weight", value=w_input)
    if st.button("Save Weight Entry"):
        new_row = pd.DataFrame({"Date": [datetime.date.today()], "Weight": [new_weight]})
        st.session_state.weight_log = pd.concat([st.session_state.weight_log, new_row]).drop_duplicates()
    
    if not st.session_state.weight_log.empty:
        fig_line = px.line(st.session_state.weight_log, x="Date", y="Weight", title="Weight Journey", markers=True)
        st.plotly_chart(fig_line)
    else:
        st.info("Log your first weight entry to see the chart!")

st.divider()
st.caption("Baller Rebound AI - V1.0 | Always consult a doctor before starting a new regime.")
