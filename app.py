# 실행: streamlit run app.py
import streamlit as st

from ui import chat_view

st.set_page_config(page_title="메뉴 추천 챗봇", page_icon="🍽️")
chat_view.render()
