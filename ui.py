# ui.py
import streamlit as st
import requests

st.title("💬 Hybrid AI Travel Assistant")

query = st.text_input("Ask your travel question:")
if st.button("Generate"):
    if query:
        with st.spinner("Generating ..."):
            try:
                res = requests.get("http://localhost:8000/ask", params={"query": query})
                st.markdown(res.json()["response"])
            except Exception as e:
                st.error(f"Request failed: {e}")
