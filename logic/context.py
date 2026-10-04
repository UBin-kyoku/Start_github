# 대화 기록과 제외 조건을 st.session_state에 보관한다.
import streamlit as st


def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []      # [{"role": "user"/"assistant", "content": "..."}]
    if "excluded" not in st.session_state:
        st.session_state.excluded = set()   # 싫어하는 태그 모음
    if "last_emotion" not in st.session_state:
        st.session_state.last_emotion = None


def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})
