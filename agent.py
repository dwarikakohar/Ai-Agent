

import streamlit as st
import re
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from google import genai
from google.genai import types

# Configure Streamlit page
st.set_page_config(page_title="Deep Research AI Agent", page_icon="🧠", layout="wide")

# Custom CSS for better UI
st.markdown("""
<style>
    .reportview-container { margin-top: -2em; }
    .stChatFloatingInputContainer { bottom: 20px; }
    .css-1d391kg { padding-top: 1rem; }
    .stPlotlyChart { border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Configuration ---
with st.sidebar:
    st.title("⚙️ Agent Configuration")
    st.write("Welcome! Please enter your Google Gemini API Key to start researching.")
    st.markdown("[👉 Get your FREE API key here](https://aistudio.google.com/app/apikey)")
    api_key = st.text_input("Google API Key", type="password", help="Get this from Google AI Studio")
    
    st.divider()
    st.markdown("""
    ### Example Commands:
    * **"Diogenes"** (History, philosophy, and images)
    * **"Projectile Motion"** (Step-by-step derivation + interactive simulation)
    * **"Black Holes"** (Physics explained simply with visuals)
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- Helper Logic ---

def execute_viz_code(code):
    """Executes visualization code and returns the figure object."""
    local_vars = {'np': np, 'plt': plt, 'go': go, 'px': px, 'st': st}
    try:
        exec(code, globals(), local_vars)
        return local_vars.get('fig')
    except Exception as e:
        return f"Error: {str(e)}"

def render_content_with_viz(text):
    """Parses text for code blocks and renders text and plots sequentially."""
    parts = re.split(r'```python(.*?)```', text, flags=re.DOTALL)
    for i, part in enumerate(parts):
        if i % 2 == 0:
            if part.strip():
                st.markdown(part)
        else:
            code = part.strip()
            with st.expander("👨‍💻 View Logic/Code", expanded=False):
                st.code(code, language='python')
            
            result = execute_viz_code(code)
            if isinstance(result, (go.Figure, plt.Figure)):
                if isinstance(result, go.Figure):
                    st.plotly_chart(result, use_container_width=True)
                else:
                    st.pyplot(result)
            elif isinstance(result, str) and result.startswith("Error"):
                st.error(f"Visualization failed: {result}")

# --- Main App Logic ---
st.title("🧠 Deep Research AI Agent")
st.write("Providing deep insights with derivations, images, and live simulations.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history (Re-executing viz blocks so they persist)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            render_content_with_viz(message["content"])
        else:
            st.markdown(message["content"])

# System Prompt with stricter Visualization rules
SYSTEM_PROMPT = """
You are an elite Deep Research AI Agent. 
Explain concepts from first principles (zero knowledge assumed).

STRICT OUTPUT RULES:
1. **Structure:** Use H2/H3 headers and LaTeX for ALL math (e.g., $v = u + at$).
2. **Images:** Use Markdown `![description](url)` for historical/scientific context. Prefer Wikimedia Commons.
3. **Visualizations (MANDATORY for Science/Math):**
    - Provide self-contained Python code in ```python ... ``` blocks.
    - **Plotly Symbol Rule:** Only use supported symbols: ['circle', 'square', 'diamond', 'cross', 'x', 'triangle-up'].
    - **Mandatory Variable:** You MUST assign the final plot to a variable named `fig`.
    - **Clean Code:** Do not use `fig.show()` or `plt.show()`.
    - Assume `np`, `plt`, `go`, `px` are pre-imported.
"""

# Chat input
if prompt := st.chat_input("Ask me to research something..."):
    if not api_key:
        st.sidebar.error("Please enter your API Key first!")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Deep researching and simulating..."):
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
                
                full_response = response.text
                render_content_with_viz(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Agent encountered an error: {e}")
