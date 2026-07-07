"""💻 SENTINEL UI - Streamlit Interface
Beautiful web interface for SENTINEL
"""

import streamlit as st
from src.sentinel_main import Sentinel
import time

# Page config
st.set_page_config(
    page_title="🛡️ SENTINEL",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .main { max-width: 1200px; margin: 0 auto; }
    .stButton > button { width: 100%; }
    h1 { color: #1f77b4; }
</style>
""", unsafe_allow_html=True)

# Initialize
if 'sentinel' not in st.session_state:
    st.session_state.sentinel = Sentinel()
    st.session_state.history = []

sentinel = st.session_state.sentinel

# Header
st.markdown("# 🛡️ SENTINEL")
st.markdown("**One AI to rule them all** - Transparent, Secure, Honest AI")
st.divider()

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    user_id = st.text_input("User ID", "anonymous")
    show_details = st.checkbox("Show execution details", True)
    st.divider()
    
    st.markdown("## 📊 Stats")
    if st.session_state.history:
        total = len(st.session_state.history)
        avg_score = sum(h['quality_score'] for h in st.session_state.history) / total
        st.metric("Total Executions", total)
        st.metric("Avg Quality", f"{avg_score:.0%}")

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 Enter Your Instruction")
    instruction = st.text_area(
        "What do you want SENTINEL to do?",
        placeholder="e.g., Write a Python function for fibonacci",
        height=100
    )

with col2:
    st.markdown("### 🚀 Execute")
    execute_button = st.button("Execute", use_container_width=True, type="primary")

# Execute
if execute_button and instruction:
    with st.spinner("🛡️ SENTINEL processing..."):
        start_time = time.time()
        result = sentinel.execute(instruction, user_id)
        execution_time = time.time() - start_time
    
    if result['success']:
        st.success("✅ Execution successful!")
        
        # Store in history
        st.session_state.history.append({
            'instruction': instruction,
            'quality_score': result['quality_score'],
            'model': result['model_used'],
            'time': execution_time
        })
        
        # Response
        st.divider()
        st.markdown("### 📤 Response")
        st.text_area("Result:", result['response'], height=200, disabled=True)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Quality Score", f"{result['quality_score']:.0%}")
        with col2:
            st.metric("Model Used", result['model_used'])
        with col3:
            st.metric("Effectiveness", f"{result['effectiveness']:.0%}")
        with col4:
            st.metric("Execution Time", f"{execution_time:.2f}s")
        
        # Details
        if show_details:
            st.divider()
            st.markdown("### 📊 Execution Details")
            with st.expander("View full details"):
                st.json({
                    "execution_id": result['execution_id'],
                    "quality_score": result['quality_score'],
                    "model_used": result['model_used'],
                    "effectiveness": result['effectiveness'],
                    "execution_time": execution_time,
                })
    else:
        st.error(f"❌ Execution failed: {result.get('error')}")

# History
if st.session_state.history:
    st.divider()
    st.markdown("### 📜 Execution History")
    for i, h in enumerate(st.session_state.history[-5:], 1):
        with st.expander(f"{i}. {h['instruction'][:50]}..."):
            st.write(f"**Model:** {h['model']}")
            st.write(f"**Quality:** {h['quality_score']:.0%}")
            st.write(f"**Time:** {h['time']:.2f}s")

# Footer
st.divider()
st.markdown("""
---
🛡️ **SENTINEL** - One AI to rule them all
- 100% Open Source
- Zero Costs
- Fully Auditable
- Local First
""")
