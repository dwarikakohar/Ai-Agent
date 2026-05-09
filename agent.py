
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

# --- CUSTOM SCIENTIFIC UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono&display=swap');
    
    :root {
        --nexus-cyan: #00d4ff;
        --nexus-bg: #0e1117;
        --nexus-card: #161b22;
        --nexus-border: #30363d;
    }

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: var(--nexus-bg);
    }

    h1, h2, h3 {
        color: var(--nexus-cyan) !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
        text-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
    }

    .derivation-container {
        background-color: #1a1c24;
        border-left: 5px solid var(--nexus-cyan);
        padding: 25px;
        border-radius: 8px;
        margin: 25px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .derivation-title {
        color: var(--nexus-cyan);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 15px;
        display: block;
        opacity: 0.8;
    }

    .stChatMessage {
        background-color: var(--nexus-card) !important;
        border: 1px solid var(--nexus-border) !important;
        border-radius: 12px !important;
        margin-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=60)
    st.title("Nexus Terminal")
    st.caption("v2.1 | Scientific Research Agent")
    st.markdown("---")
    
    api_key = st.text_input("🔑 Google API Key", type="password", placeholder="Paste Gemini API key...")
    st.markdown("[Get API Key](https://aistudio.google.com/app/apikey)")
    
    st.markdown("---")
    mode = st.selectbox("Focus Area", ["Comprehensive", "Theoretical Physics", "Quantitative Math", "Historical Tech"])
    temp = st.slider("Response Creativity", 0.0, 1.0, 0.2)
    
    if st.button("🗑 Clear Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = f"""
You are 'Nexus', a high-end Scientific AI Agent. 
Current Focus: {mode}

RULES:
1. **Visuals:** You MUST generate a simulation using Plotly for motion/data. 
   - Code must be in a standard ```python block.
   - Assign the result to a variable named `fig`.
   - Use `fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')`.
2. **Derivations:** Wrap math proofs in:
   <div class="derivation-container">
   <span class="derivation-title">Mathematical Derivation</span>
   [Double dollar LaTeX here]
   </div>
3. **Formatting:** Use bold headers and bullet points. No walls of text.
4. **Media:** Start with one relevant Wikimedia image link: ![Image](url).
"""

# --- LOGIC FUNCTIONS ---
def execute_viz_code(code_string):
    """Clean and execute Python code safely."""
    # Robustly extract code between backticks if they exist
    if "```python" in code_string:
        clean_code = code_string.split("```python")[1].split("```")[0].strip()
    else:
        clean_code = code_string.strip()
    
    local_vars = {'np': np, 'plt': plt, 'go': go, 'px': px, 'st': st}
    try:
        # Use only local_vars dict for isolated execution
        exec(clean_code, local_vars)
        return local_vars.get('fig')
    except Exception as e:
        return f"Visualization Engine Error: {str(e)}"

def render_nexus_content(text):
    """Parses and renders complex segments of the research output."""
    # Split content into segments (Text vs Code vs Derivations)
    pattern = r'(```python.*?```|<div class="derivation-container">.*?</div>)'
    segments = re.split(pattern, text, flags=re.DOTALL)

    for segment in segments:
        if not segment.strip():
            continue
            
        if "```python" in segment:
            with st.expander("🛠 Simulation Source Code", expanded=False):
                display_code = segment.replace("```python", "").replace("```", "").strip()
                st.code(display_code, language='python')
            
            fig = execute_viz_code(segment)
            if isinstance(fig, (go.Figure, plt.Figure)):
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"💡 Simulation Info: {fig}")
                
        elif 'class="derivation-container"' in segment:
            st.markdown(segment, unsafe_allow_html=True)
        else:
            st.markdown(segment, unsafe_allow_html=True)

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        render_nexus_content(msg["content"])

if prompt := st.chat_input("Enter research topic..."):
    if not api_key:
        st.error("Nexus Error: API Key missing in sidebar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            client = genai.Client(api_key=api_key)
            # Standard Gemini 2.0 Flash call
            stream = client.models.generate_content_stream(
                model='gemini-2.0-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=temp,
                )
            )
            
            for chunk in stream:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
            
            # Finalize rendering
            response_placeholder.empty()
            render_nexus_content(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Nexus Core Error: {e}")
