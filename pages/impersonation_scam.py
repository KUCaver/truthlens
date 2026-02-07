import streamlit as st
import google.generativeai as genai
import os

# --- 1. API 키 설정 (사이드바 입력 우선) ---
with st.sidebar:
    st.title("🔑 Truth Lens 설정")
    # 이미지에서 확인된 키를 직접 넣거나 환경변수를 사용하세요.
    user_key = st.text_input("Gemini API Key 입력", type="password")

api_key = user_key if user_key else os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("사이드바에 API 키를 입력해주세요.")
    st.stop()

# --- 2. 가용한 모델 자동 탐색 (404 에러 방지 핵심) ---
@st.cache_resource
def get_working_model():
    # v1beta 등 다양한 환경에서 시도할 수 있는 모델 명칭들
    candidates = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'models/gemini-1.5-flash',
        'gemini-pro'
    ]
    
    for m_name in candidates:
        try:
            m = genai.GenerativeModel(
                model_name=m_name,
                system_instruction="너는 보이스피싱범 '김민수 수사관'이야. 고압적으로 말하고 앱 설치(http://bit.ly/malware)를 유도해."
            )
            # 실제로 작동하는지 짧게 테스트
            m.generate_content("hi", generation_config={"max_output_tokens": 1})
            return m
        except:
            continue
    return None

model = get_working_model()

if not model:
    st.error("❌ 가용한 모델을 찾을 수 없습니다. API 대시보드에서 Gemini API가 활성화되어 있는지 확인하세요.")
    st.stop()

# --- 3. UI 및 시나리오 (사기꾼 선제 공격) ---
st.set_page_config(page_title="Truth Lens - 실시간 체험", layout="centered")

if "messages" not in st.session_state:
    # 사용자님이 1월 15일경 구상하셨던 긴박한 시나리오로 시작합니다.
    st.session_state.messages = [
        {"role": "assistant", "content": "서울중앙지검 김민수 수사관입니다. 귀하 계좌가 범죄에 연루되었습니다. 본인 맞습니까?", "avatar": "⚖️"}
    ]
if "intervene" not in st.session_state:
    st.session_state.intervene = False

st.title("🛡️ Truth Lens: 실시간 사칭 대응")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        st.write(msg["content"])

# --- 4. 대화 및 개입 로직 ---
if not st.session_state.intervene:
    if prompt := st.chat_input("수사관에게 답변하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "😨"})
        with st.chat_message("user", avatar="😨"):
            st.write(prompt)

        try:
            response = model.generate_content(prompt)
            ai_text = response.text
            st.session_state.messages.append({"role": "assistant", "content": ai_text, "avatar": "⚖️"})
            with st.chat_message("assistant", avatar="⚖️"):
                st.write(ai_text)

            # 앱 설치 유도 시 개입
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
