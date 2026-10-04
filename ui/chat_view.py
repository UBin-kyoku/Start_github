# Streamlit 채팅 화면
import streamlit as st

from logic import api_client, context, rule_engine

FALLBACK = "잘 이해하지 못했어요. 지금 기분을 다른 표현으로 말해줄래요?"


def render():
    st.title("🍽️ 기분별 메뉴 추천 챗봇")
    st.caption("지금 기분을 말해주면 어울리는 메뉴를 추천해드려요.")

    context.init_state()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    text = st.chat_input("예: 오늘 너무 우울해")
    if not text:
        return

    context.add_message("user", text)
    with st.chat_message("user"):
        st.write(text)

    # 1) 규칙 기반 → 2) 실패하면 API → 3) 그래도 실패하면 폴백
    reply = rule_engine.answer(text, st.session_state)
    if reply is None:
        reply = api_client.ask_claude(st.session_state.messages, st.session_state.excluded)
    if reply is None:
        reply = FALLBACK

    context.add_message("assistant", reply)
    with st.chat_message("assistant"):
        st.write(reply)
