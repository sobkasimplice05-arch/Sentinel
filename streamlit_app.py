import streamlit as st
from src.sentinel_main import Sentinel
import time

st.set_page_config(page_title="🛡️ SENTINEL", page_icon="🛡️", layout="wide")
st.markdown("# 🛡️ SENTINEL\n**One AI to rule them all**")

if 'sentinel' not in st.session_state:
    st.session_state.sentinel = Sentinel()

sentinel = st.session_state.sentinel

instruction = st.text_area("What do you want SENTINEL to do?", height=100)
if st.button("Execute", type="primary"):
    with st.spinner("🛡️ Processing..."):
        result = sentinel.execute(instruction)
    
    if result['success']:
        st.success("✅ Success!")
        st.write(result['response'])
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Quality", f"{result['quality_score']:.0%}")
        with col2:
            st.metric("Model", result['model_used'])
        with col3:
            st.metric("Time", f"{result['execution_time']:.2f}s")
    else:
        st.error(f"❌ Failed")
