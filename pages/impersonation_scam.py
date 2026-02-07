import streamlit as st
from google import genai
import os
import random

# --- 1. API 및 클라이언트 설정 ---
API_KEY = "AIzaSyDH-4lwnsiRzQkWNd02AAk_xlBf4Slr41k"
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.0-flash" 

# --- 2. 스마트폰 내부 렌더링을 위한 다크 스타일 ---
st.set_page_config(page_title="Truth Lens", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    
    /* 스마트폰 프레임 고정 */
    .phone-frame {
        border: 10px solid #2d2d2d;
        border-radius: 40px;
        width: 360px;
        height: 720px;
        margin: auto;
        background-color: #161b22;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        position: relative;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }

    /* 상단 노치 영역 */
    .phone-notch {
        width: 120px;
        height: 20px;
        background: #2d2d2d;
        border-bottom-left-radius: 15px;
        border-bottom-right-radius: 15px;
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        z-index: 100;
    }

    /* 내부 콘텐츠 스크롤 영역 */
    .phone-content {
        padding: 40px 20px 20px 20px;
        height: 100%;
        overflow-y: auto;
        scrollbar-width: none; /* 파이어폭스 */
    }
    .phone-content::-webkit-scrollbar { display: none; } /* 크롬/사파리 */

    /* 대화창 다크 스타일링 */
    [data-testid="stChatMessage"] {
        background-color: #21262d !important;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 시스템 설정 ---
FRAUD_INSTRUCTION = "너는 보이스피싱범 김민수 수사관이야. 고압적인 문자 스타일로 앱 설치 링크(http://bit.ly/secure-app)를 보내."
SECURITY_ALERTS = [
    "🛡️ Truth Lens: 사기 패턴 98.7% 일치",
    "🛡️ Truth Lens: 수사기관은 문자로 링크 안 보냄",
    "🛡️ Truth Lens: 심리적 압박 수법 감지됨"
]

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "서울중앙지검 김민수 수사관입니다. 본인 맞습니까?", "avatar": "⚖️"}]
if "first_view" not in st.session_state:
    st.session_state.first_view = True
if "show_barrier" not in st.session_state:
    st.session_state.show_barrier = False

# --- 4. 폰 프레임 내부 구성 ---
# HTML 태그를 사용하여 프레임을 열어줍니다.
st.markdown('<div class="phone-frame"><div class="phone-notch"></div><div class="phone-content">', unsafe_allow_html=True)

# 폰 내부 콘텐츠 (Step 1 ~ Step 4)
if st.session_state.first_view:
    st.subheader("⚖️ 긴급 통지")
    if os.path.exists("fraud_evidence.png"):
        st.image("fraud_evidence.png")
    else:
        st.error("❗ [긴급] 전자 기록물 통지")
        st.caption("귀하는 금융범죄 피의자로 지정되었습니다.")
    if st.button("메시지 확인"):
        st.session_state.first_view = False
        st.rerun()
else:
    # 채팅 내역
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg.get("avatar", "😨")):
            st.write(msg["content"])

    # 상시 보안 팝업
    st.warning(random.choice(SECURITY_ALERTS))

    # 입력창 (폰 내부에서 처리하기 위해 st.chat_input 대신 폰 전용 입력 방식 사용 시도)
    if not st.session_state.show_barrier:
        # 폰 내부 느낌을 위해 st.text_input 사용 (chat_input은 폰 밖에 생길 확률이 큼)
        user_reply = st.text_input("답장 입력...", key="chat_input_phone")
        if st.button("전송"):
            st.session_state.messages.append({"role": "user", "content": user_reply})
            response = client.models.generate_content(model=MODEL_ID, contents=f"{FRAUD_INSTRUCTION}\n\n사용자: {user_reply}")
            st.session_state.messages.append({"role": "assistant", "content": response.text, "avatar": "⚖️"})
            st.rerun()

    # 링크 감지 및 방지턱
    last_msg = st.session_state.messages[-1]["content"]
    if "http" in last_msg and not st.session_state.show_barrier:
        if st.button("🔗 보안 링크 확인 (클릭)", type="primary"):
            st.session_state.show_barrier = True
            st.rerun()

    if st.session_state.show_barrier:
        st.error("🛑 Truth Lens 차단")
        st.button("📞 1301 즉시 신고")
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.info(f"**과속 방지턱: 아래 문장 입력**\n\n{target}")
        user_input = st.text_input("타이핑 하세요:", key="barrier")
        if user_input.strip() == target:
            st.error("❗ 최종 경고: 자산 탈취 위험!")
            st.link_button("⚠️ 위험 무시하고 이동", "https://www.polico.go.kr/index.do")

# 프레임을 닫아줍니다.
st.markdown('</div></div>', unsafe_allow_html=True)
