import streamlit as st
from google import genai  # 최신 SDK 방식
import os

# --- 1. API 키 설정 (Secrets 또는 사이드바) ---
with st.sidebar:
    st.title("🔑 설정")
    user_key = st.text_input("Gemini API Key", type="password")

# 우선순위: 사용자가 직접 입력한 키 -> 클라우드 Secrets에 저장된 키
api_key = user_key if user_key else st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.warning("API 키가 필요합니다. Secrets에 등록하거나 사이드바에 입력해주세요.")
    st.stop()

# --- 2. 클라이언트 및 최신 모델 설정 ---
# 404 에러 방지를 위해 현재 가장 권장되는 2.0 모델을 사용합니다
client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-2.0-flash" 

# --- 3. UI 및 시나리오 초기화 ---
st.set_page_config(page_title="Truth Lens - 실시간 체험", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "서울중앙지검 김민수 수사관입니다. 본인 맞습니까?", "avatar": "⚖️"}
    ]
if "intervene" not in st.session_state:
    st.session_state.intervene = False

st.title("⚖️ 검찰 사칭 대응 훈련")

# 채팅 내역 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        st.write(msg["content"])

# --- 4. 대화 로직 ---
if not st.session_state.intervene:
    if prompt := st.chat_input("수사관에게 답변하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "😨"})
        with st.chat_message("user", avatar="😨"):
            st.write(prompt)

        try:
            # 최신 SDK 호출 방식 적용
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=f"너는 사기꾼 수사관이야. 고압적으로 앱 설치(http://bit.ly/truth-lens-app)를 유도해: {prompt}"
            )
            ai_text = response.text
            st.session_state.messages.append({"role": "assistant", "content": ai_text, "avatar": "⚖️"})
            with st.chat_message("assistant", avatar="⚖️"):
                st.write(ai_text)

            # 앱 설치 유도 시 Truth Lens 개입
            if any(word in ai_text for word in ["설치", "링크", "http", "앱"]):
                st.session_state.intervene = True
                st.rerun()
        except Exception as e:
            st.error(f"대화 오류: {e}")

# --- 5. Truth Lens 개입 (현실 자각 로직) ---
if st.session_state.intervene:
    st.divider()
    with st.container(border=True):
        st.error("🚨 Truth Lens: 위험 감지!")
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.info(f"방어 문장을 입력하세요: **{target}**")
        
        user_input = st.text_input("입력:", key="defense")
        if st.button("방어 완료"):
            if user_input.strip() == target:
                st.success("✅ 안전하게 방어했습니다!")
                st.balloons()
                if st.button("새 훈련 시작"):
                    st.session_state.clear()
                    st.rerun()
