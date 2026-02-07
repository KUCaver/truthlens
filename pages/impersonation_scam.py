import streamlit as st
from google import genai  # 최신 SDK 라이브러리
import os

# --- 1. API 설정 ---
# 새로 발급받으신 키를 기본값으로 설정합니다.
DEFAULT_API_KEY = "AIzaSyDH-4lwnsiRzQkWNd02AAk_xlBf4Slr41k"

with st.sidebar:
    st.title("🔑 Truth Lens 설정")
    # 직접 입력하거나 기본키를 사용합니다.
    user_key = st.text_input("Gemini API Key 입력", type="password")

# 우선순위: 사용자 입력 키 -> 기본 제공 키 -> 환경 변수
api_key = user_key if user_key else DEFAULT_API_KEY

try:
    client = genai.Client(api_key=api_key)
    MODEL_ID = "gemini-2.0-flash" # 최신 안정화 모델
except Exception as e:
    st.error(f"API 연결 오류: {e}")
    st.stop()

# --- 2. UI 스타일 (사용자님의 기존 스타일 유지) ---
st.set_page_config(page_title="Truth Lens - 실시간 사칭 대응", layout="centered")
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 2rem; }
    .main > div { background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
    [data-testid="stChatMessageContent"] { background: #f8f9fa; border-radius: 15px; padding: 1rem; color: #333 !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. 세션 초기화 및 시나리오 시작 ---
if "messages" not in st.session_state:
    # 2월 1일 "Truth Lens" 프로젝트 초기 시나리오 반영
    st.session_state.messages = [
        {"role": "assistant", "content": "서울중앙지검 김민수 수사관입니다. 귀하의 계좌가 금융 범죄에 도용되었습니다. 본인 확인 절차에 응하지 않으면 즉각 체포영장 집행합니다. 본인 맞습니까?", "avatar": "⚖️"}
    ]
if "intervene" not in st.session_state:
    st.session_state.intervene = False
if "verify_status" not in st.session_state:
    st.session_state.verify_status = "NONE"

st.markdown("<h2 style='text-align: center;'>⚖️ 실시간 검찰 사칭 시뮬레이션</h2>", unsafe_allow_html=True)

# --- 4. 채팅 화면 렌더링 ---
chat_container = st.container(border=True)
with chat_container:
    for msg in st.session_state.messages:
        avatar = "⚖️" if msg["role"] == "assistant" else "😨"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

# --- 5. 실시간 대화 및 Truth Lens 개입 로직 ---
if not st.session_state.intervene:
    if prompt := st.chat_input("수사관에게 답변하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="😨"):
            st.write(prompt)

        try:
            # 사기꾼 수사관 페르소나 주입 및 실시간 답변 생성
            fraud_instruction = (
                "너는 지금 서울중앙지검 김민수 수사관을 사칭하는 보이스피싱범이야. "
                "고압적인 태도로 상대를 압박하고, 결국 본인 확인용 보안 앱(http://bit.ly/truth-lens-app)을 "
                "설치하라고 강요해야 해. 답변은 짧고 위협적으로 해줘."
            )
            response = client.models.generate_content(
                model=MODEL_ID, 
                contents=f"{fraud_instruction}\n\n사용자: {prompt}"
            )
            ai_text = response.text
            
            st.session_state.messages.append({"role": "assistant", "content": ai_text})
            with st.chat_message("assistant", avatar="⚖️"):
                st.write(ai_text)

            # 앱 설치 유도 키워드 감지 시 Truth Lens 작동
            if any(word in ai_text for word in ["설치", "링크", "http", "앱", "다운로드"]):
                st.session_state.intervene = True
                st.rerun()
        except Exception as e:
            st.error(f"대화 중 오류 발생: {e}")

# --- 6. Truth Lens 개입 (현실 자각 로직) ---
if st.session_state.intervene:
    st.divider()
    nudge_container = st.container(border=True)
    with nudge_container:
        st.error("🚨 Truth Lens: 악성 앱 설치 유도 차단!")
        st.write("상대방이 공포감을 조성해 이성을 마비시키려 하고 있습니다.")

        # 퀴즈 및 따라쓰기 로직
        target_sentence = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.warning(f"**[현실 자각 퀴즈]** 아래 문장을 직접 타이핑하여 인지하십시오.")
        st.markdown(f"### 🗣️ \"{target_sentence}\"")
        user_input = st.text_input("정확히 입력하세요:", key="defense_input")

        if st.button("확인 및 진행"):
            if user_input.strip() == target_sentence:
                st.session_state.verify_status = "SUCCESS"
            else:
                st.error("⚠️ 문장이 일치하지 않습니다. 다시 입력하세요.")

        if st.session_state.verify_status == "SUCCESS":
            st.success("✅ 인지 확인 완료. 사기꾼의 심리적 지배에서 벗어났습니다.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📲 무시하고 앱 설치 (위험)", type="primary"):
                    st.error("💀 악성 앱이 설치되었습니다. 개인정보가 유출 중입니다...")
            with col2:
                if st.button("🚫 차단 및 대화 종료 (권장)"):
                    st.balloons()
                    st.success("✅ 방어 성공! 훈련을 마칩니다.")
                    if st.button("다시 하기"):
                        st.session_state.clear()
                        st.rerun()
