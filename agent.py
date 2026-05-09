import streamlit as st
import re
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from google import genai
from google.genai import types

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Nexus AI | Deep Research",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED SCIENTIFIC UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono&display=swap');
    
    :root {
        --nexus-cyan: #00d4ff;
        --nexus-bg: #0e1117;
        --nexus-card: #161b22;
        --nexus-border: #30363d;
    }

    .stApp { background-color: var(--nexus-bg); }

    /* Scientific Glow Effect for Headings */
    h1, h2, h3 {
        color: var(--nexus-cyan) !important;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    }

    /* Enhanced Derivation Box */
    .derivation-container {
        background-color: #1a1c24;
        border: 1px solid var(--nexus-cyan);
        border-left: 5px solid var(--nexus-cyan);
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);
    }
    
    .derivation-title {
        color: var(--nexus-cyan);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
        display: block;
    }

    /* Chat Styling */
    .stChatMessage {
        border: 1px solid var(--nexus-border) !important;
        background-color: var(--nexus-card) !important;
        border-radius: 12px !important;
    }

    /* Custom Sidebar Stats */
    .stat-box {
        padding: 10px;
        border-radius: 5px;
        background: #1c2128;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR & SETUP ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=60)
    st.title("Nexus Terminal")
    
    api_key = st.text_input("Gemini API Key", type="password", help="Get it from Google AI Studio")
    
    st.divider()
    mode = st.selectbox("Research Depth", ["Fast Scan", "Deep Derivation", "Experimental Simulation"])
    temp = st.slider("Stochasticity (Temp)", 0.0, 1.0, 0.3)
    
    if st.button("🗑 Reset Terminal", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- CONSTANTS & PROMPTS ---
SYSTEM_PROMPT = f"""
You are 'Nexus', a high-end Scientific AI Agent. 
Mode: {mode}. 

STRICT OUTPUT RULES:
1. Formatting: Use bullet points, bolding, and clear headers. No "walls of text".
2. Derivations: If you use math, wrap it in:
   <div class="derivation-container">
   <span class="derivation-title">Mathematical Proof</span>
   $$[LATEX HERE]$$
   </div>
3. Visuals: If explaining a trend or physics concept, write a Python block:
   ```python
   import plotly.graph_objects as go
   # ... setup data ...
   fig = go.Figure(...)
   fig.update_layout(template="plotly_dark", font_color="#00d4ff")
