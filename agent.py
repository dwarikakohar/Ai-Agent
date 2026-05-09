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
    /* Main Background and Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: #0e1117;
    }

    /* Science Style Headings */
    h1, h2, h3 {
        color: #00d4ff !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }

    /* The Derivation Box */
    .derivation-container {
        background-color: #1a1c24;
        border-left: 5px solid #00d4ff;
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .derivation-title {
        color: #00d4ff;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        text-transform: uppercase;
        margin-bottom: 10px;
        display: block;
    }

    /* Chat Styling */
    .stChatMessage {
        background-color: #161b22 !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        border: 1px solid #30363d !important;
    }

    /* Code Blocks */
    code {
        color: #ff79c6 !important;
        background-color: #282a36 !important;
        padding: 2px 5px !important;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("Nexus Research")
    st.markdown("---")
    st.markdown("### 🔑 Authentication")
    st.markdown("[Get Free Google API Key](https://aistudio.google.com/app/apikey)")
    api_key = st.text_input("Enter API Key", type="password", placeholder="Paste key here...")
    
    st.markdown("---")
    st.markdown("### 🛠 Mode")
    mode = st.radio("Focus Area", ["Comprehensive", "Math/Physics", "Historical"])
    
    if st.button("🗑 Clear Session"):
        st.session_state.messages = []
        st.rerun()

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are 'Nexus', a high-end Scientific AI Agent. Your goal is to provide deep, interactive research.

RULES FOR INTERACTIVITY:
1. **Formatting:** Never write in long, boring paragraphs. Use bullet points and bold keywords. 
2. **Derivations:** Whenever you explain math or physics, wrap the derivation in a special HTML block:
   <div class="derivation-container">
   <span class="derivation-title">Mathematical Derivation</span>
   [Insert LaTeX math here]
   </div>
3. **LaTeX:** Always use double dollar signs for centered math: $$E = mc^2$$.
4. **Visuals:** You MUST generate a simulation if the topic involves motion, data, or logic. 
   - Use Plotly for interactive charts.
   - Assign the result to a variable named `fig`.
   - Only use these Plotly symbols: ['circle', 'square', 'diamond', 'cross', 'x'].
5. **Images:** Include at least one high-quality image link from Wikimedia at the start of your research.
"""

# --- LOGIC FUNCTIONS ---
def execute_viz_code(code):
    local_vars = {'np': np, 'plt': plt, 'go': go, 'px': px, 'st': st}
    try:
        exec(code, globals(), local_vars)
        return local_vars.get('fig')
    except Exception as e:
        return f"Error: {str(e)}"

def render_content(text):
    """Parses and renders text, HTML-wrapped derivations, and code blocks."""
    # Split text into segments: standard text, HTML-divs (derivations), and Python code
    # We use a broader regex to capture our custom div blocks and code blocks
    pattern = r'(```python.*?```|<div class="derivation-container">.*?</div>)'
    segments = re.split(pattern, text, flags=re.DOTALL)

    for segment in segments:
        if segment.startswith('```python'):
            code = segment.replace('```python', '').replace('```', '').strip()
            with st.expander("🛠 Simulation Source Code", expanded=False):
                st.code(code, language='python')
            res = execute_viz_code(code)
            if isinstance(res, (go.Figure, plt.Figure)):
                st.plotly_chart(res, use_container_width=True) if isinstance(res, go.Figure) else st.pyplot(res)
        elif segment.startswith('<div class="derivation-container">'):
            # Render derivation with custom styling
            st.markdown(segment, unsafe_allow_html=True)
        else:
            # Regular Markdown
            if segment.strip():
                st.markdown(segment, unsafe_allow_html=True)

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            render_content(msg["content"])
        else:
            st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask Nexus to research..."):
    if not api_key:
        st.error("Please provide an API Key in the sidebar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing data streams..."):
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        tools=[{"google_search": {}}],
                        temperature=0.2,
                    )
                )
                render_content(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Nexus encountered an error: {e}")
