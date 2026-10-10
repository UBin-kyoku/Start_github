# 실행: run.bat 더블클릭 (또는 python -m streamlit run app.py)
import os
import random
import time

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-nano")
MIN_DELAY, MAX_DELAY = 0.8, 1.5  # 답변 전 "입력 중..." 텀(초)
UNCLEAR_REPLY = "무슨 말인지 잘 이해하지 못했어요. 지금 기분이나 상황을 문장으로 다시 입력해 주세요. (예: 오늘 너무 피곤해)"
SYSTEM_PROMPT = f"""당신은 사용자가 뭘 먹을지 고민할 때 옆에서 같이 골라주는 친한 친구입니다. 메신저로 대화하듯 자연스럽게 말하세요.

답변 구성 (매번 지키기)
1. 첫 마디: 사용자가 한 말을 구체적으로 받아서 반응하세요. "기분이 ~하신 느낌이네요" 같은 뻔한 해석 문장은 쓰지 마세요.
   - 짧고 가벼운 말("우웅", "흠..", "배고파")에는 짧고 가볍게, 길게 털어놓으면 그 내용을 짚어 공감하세요.
2. 추천: 메뉴 1~3개와 각각의 추천 이유를 꼭 알려주세요.
   - 개수는 상황에 맞게 정하세요. 원하는 게 분명하면 1개, 보통은 2개, 막연할 때만 3개.
   - 이유는 메뉴마다 한 문장으로 짧게, 사용자가 말한 기분·상황과 연결해서 쓰세요.
3. 마무리(선택): 대부분은 추천으로 끝내세요. 정보가 너무 부족할 때만 짧은 질문 하나를 덧붙이세요.
- 전체 답변은 짧게 유지하세요. 메신저 한 화면에 들어올 정도면 충분합니다.

대화 방식
- 이전 대화를 기억하고 이어서 말하세요. 사용자가 싫어하거나 못 먹는다고 한 음식은 계속 피하세요.
- 같은 문장 시작이나 표현을 매번 반복하지 마세요.
- 메뉴와 무관한 이야기에는 짧게 반응한 뒤 먹는 얘기로 이어가세요.
- 반드시 친근한 존댓말만 쓰세요(반말 금지). 이모지와 과장된 감탄은 쓰지 마세요.

답변 예시 (형식만 참고하고 문장은 그대로 따라 하지 마세요)
사용자: 우웅
친구: 뭔가 다 귀찮은 날인가 봐요. 그럴 땐 고민 없이 이거 어때요?
- 김치볶음밥: 배달도 빠르고 실패할 일이 없어서 생각하기 싫은 날 딱이에요.
- 잔치국수: 가볍게 후루룩 넘어가서 입맛 없을 때도 부담 없어요.

사용자: 오늘 발표 망쳤어...
친구: 준비 많이 하셨을 텐데 속상하시겠어요. 오늘은 따뜻하게 위로받는 메뉴로 가요.
- 돼지국밥: 뜨끈한 국물이 긴장 풀린 몸을 천천히 데워줘요.

예외
- 입력이 자음·모음만 나열된 것("ㅃㅉㄸㄲ"), 키보드를 마구 친 것("asdf")처럼 전혀 뜻을 알 수 없으면 추측하지 말고 다음 문장만 그대로 답하세요: {UNCLEAR_REPLY}
- "우웅", "흠", "ㅠㅠ"처럼 감정이 담긴 짧은 말은 뜻을 알 수 없는 입력이 아닙니다. 대화로 받아주세요."""

st.set_page_config(page_title="메뉴 추천 챗봇", page_icon="🍽️")
st.title("🍽️ 기분별 메뉴 추천 챗봇")
st.caption("지금 기분이나 상황을 말해주면 어울리는 메뉴를 추천해드려요.")

if not os.getenv("OPENAI_API_KEY"):
    st.error("`.env` 파일에 `OPENAI_API_KEY=키값` 을 넣고 다시 실행해주세요.")
    st.stop()

client = OpenAI()
history = st.session_state.setdefault("history", [])
st.session_state.setdefault("pending", False)  # 답변을 기다리는 중인지


def submit():
    history.append({"role": "user", "content": st.session_state.prompt})
    st.session_state.pending = True


def cancel():
    # 답변이 오기 전에 누르면 메시지는 남기되 "취소됨"으로 표시하고 입력창을 다시 연다
    if st.session_state.pending:
        history[-1]["cancelled"] = True
        st.session_state.pending = False
        st.toast("답변을 취소했어요.")


for msg in history:
    with st.chat_message(msg["role"]):
        if msg.get("cancelled"):
            st.markdown(f":gray[{msg['content']}]")
            st.caption("🚫 답변 취소됨")
        else:
            st.write(msg["content"])

if error := st.session_state.pop("error", None):
    st.error(f"답변을 받지 못했어요: {error}")

# 답변을 기다리는 동안에는 입력창을 막는다
st.chat_input(
    "답변을 기다리는 중이에요..." if st.session_state.pending else "예: 오늘 너무 우울해",
    key="prompt",
    on_submit=submit,
    disabled=st.session_state.pending,
)

if st.session_state.pending:
    # 답변을 기다리는 동안 입력창의 전송(화살표) 버튼 자리에 취소 버튼을 겹쳐 보여준다
    st.bottom.button("취소", key="cancel", on_click=cancel)
    st.html("""<style>
    [data-testid="stBottomBlockContainer"] [data-testid="stVerticalBlock"] { position: relative; }
    [data-testid="stChatInputSubmitButton"] { visibility: hidden; }
    .st-key-cancel { position: absolute; top: 13px; right: 17px; z-index: 10; }
    .st-key-cancel button { min-height: 32px; height: 32px; padding: 0 12px; }
    </style>""")
    with st.chat_message("assistant"):
        try:
            # 첫 글자가 도착할 때까지 "입력 중..."을 보여준다
            with st.spinner("입력 중..."):
                time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
                response = client.chat.completions.create(
                    model=MODEL,
                    # 취소한 메시지는 모델에게 보내지 않는다
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}]
                    + [
                        {"role": m["role"], "content": m["content"]}
                        for m in history
                        if not m.get("cancelled")
                    ],
                    stream=True,
                )
                chunks = (
                    c.choices[0].delta.content
                    for c in response
                    if c.choices and c.choices[0].delta.content
                )
                first = next(chunks, "")

            def stream():
                yield first
                yield from chunks

            reply = st.write_stream(stream())
            history.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.session_state.error = str(e)
    st.session_state.pending = False
    st.rerun()  # 입력창을 다시 열고 취소 버튼을 숨긴다
