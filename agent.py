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

    /* Science Style Headings */
    h1, h2, h3 {
        color: var(--nexus-cyan) !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
        text-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
    }

    /* The Derivation Box */
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

    /* Chat Styling */
    .stChatMessage {
        background-color: var(--nexus-card) !important;
        border: 1px solid var(--nexus-border) !important;
        border-radius: 12px !important;
        margin-bottom: 1rem !important;
    }

    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        background: var(--nexus-bg);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--nexus-border);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=60)
    st.title("Nexus Terminal")
    st.caption("v2.0 | Scientific Research Agent")
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
You are 'Nexus', a high-end Scientific AI Agent. Your goal is deep, technical research.
Current Focus: {mode}

RULES:
1. **Visuals:** You MUST generate a simulation using Plotly for motion/data. 
   - Assign the result to a variable named `fig`.
   - Use `fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')`.
   - Only use Plotly symbols: ['circle', 'square', 'diamond', 'cross', 'x'].
2. **Derivations:** Wrap math proofs in:
   <div class="derivation-container">
   <span class="derivation-title">Mathematical Derivation</span>
   [Use double dollar signs for LaTeX here]
   </div>
3. **Formatting:** Use bold headers and bullet points. Avoid dense paragraphs.
4. **Media:** Always start with one relevant high-quality Wikimedia image link: ![Image](url).
"""

# --- LOGIC FUNCTIONS ---
def execute_viz_code(code):
    """Clean and execute the AI-generated Python code for visualizations."""
    # Strip markdown code blocks if present
    clean_code = re.sub(r'```python|
```', '', code).strip()
    
    local_vars = {'np': np, 'plt': plt, 'go': go, 'px': px, 'st': st}
    try:
        exec(clean_code, globals(), local_vars)
        return local_vars.get('fig')
    except Exception as e:
        return f"Simulation Error: {str(e)}"

def render_nexus_content(text):
    """Splits and renders text, derivations, and code blocks."""
    # Split by code blocks or derivation containers
    pattern = r'(```python.*?```|<div class="derivation-container">.*?</div>)'
    segments = re.split(pattern, text, flags=re.DOTALL)

    for segment in segments:
        if not segment.strip():
            continue
            
        if segment.startswith('```python'):
            code = segment.replace('
```python', '').replace('```', '').strip()
            with st.expander("🛠 Simulation Source Code", expanded=False):
                st.code(code, language='python')
            res = execute_viz_code(code)
            if isinstance(res, (go.Figure, plt.Figure)):
                st.plotly_chart(res, use_container_width=True)
            else:
                st.warning(res)
        elif segment.startswith('<div class="derivation-container">'):
            st.markdown(segment, unsafe_allow_html=True)
        else:
            st.markdown(segment, unsafe_allow_html=True)

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        render_nexus_content(msg["content"])

# User Input
if prompt := st.chat_input("Enter research topic (e.g., 'Quantum Entanglement Dynamics')..."):
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
            # Using streaming for the 'Nexus' feel
            stream = client.models.generate_content_stream(
                model='gemini-2.0-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=[{"google_search": {}}],
                    temperature=temp,
                )
            )
            
            for chunk in stream:
                full_response += chunk.text
                # Live typing effect
                response_placeholder.markdown(full_response + "▌")
            
            # Final Render (replacing stream with formatted blocks)
            response_placeholder.empty()
            render_nexus_content(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Nexus Core Error: {e}")
