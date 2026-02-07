import streamlit as st
import google.generativeai as genai
import os

# --- 1. API 키 설정 (사이드바 입력) ---
with st.sidebar:
    st.title("🔑 Truth Lens 설정")
    user_key = st.text_input("Gemini API Key 입력", type="password")

api_key = user_key if user_key else os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("사이드바에 API 키를 입력해주세요.")
    st.stop()

# --- 2. 가용한 모델 자동 탐색 및 로드 ---
@st.cache_resource
def get_working_model():
    # 시도해볼 모델 후보 리스트
    model_candidates = [
        'gemini-1.5-flash-latest', 
        'gemini-1.5-flash', 
        'gemini-pro',
        'models/gemini-1.5-flash',
        'models/gemini-pro'
    ]
    
    for model_name in model_candidates:
        try:
            m = genai.GenerativeModel(
                model_name=model_name,
                system_instruction="너는 고압적인 검찰 수사관 '김민수'야. 사기 앱 설치를 유도해."
            )
            # 모델이 실제로 작동하는지 가벼운 테스트
            m.generate_content("test", generation_config={"max_output_tokens": 1})
            return m
        except Exception:
            continue
    return None

model = get_working_model()

if model is None:
    st.error("❌ 가용한 Gemini 모델을 찾을 수 없습니다. API 키의 프로젝트 설정을 확인해주세요.")
    st.stop()

# --- 3. UI 및 시나리오 (사기꾼 선제 공격) ---
st.set_page_config(page_title="Truth Lens - 실시간 체험", layout="centered")

if "messages" not in st.session_state:
    # 2월 1일 "Truth Lens" 프로젝트 초기 시나리오 반영
    st.session_state.messages = [
        {"role": "assistant", "content": "서울중앙지검 김민수 수사관입니다. 귀하의 계좌가 대포통장 범죄에 연루되었습니다. 본인 맞습니까?", "avatar": "⚖️"}
    ]
if "intervene" not in st.session_state:
    st.session_state.intervene = False

st.title("⚖️ 검찰 사칭 대응 훈련")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        st.write(msg["content"])

# --- 4. 대화 및 개입 로직 ---
if not st.session_state.intervene:
    if prompt := st.chat_input("메시지를 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "😨"})
        with st.chat_message("user", avatar="😨"):
            st.write(prompt)

        try:
            response = model.generate_content(prompt)
            ai_text = response.text
            st.session_state.messages.append({"role": "assistant", "content": ai_text, "avatar": "⚖️"})
            with st.chat_message("assistant", avatar="⚖️"):
                st.write(ai_text)

            # 개입 트리거: 설치 유도 단어 감지
            if any(word in ai_text for word in ["설치", "링크", "http", "앱"]):
                st.session_state.intervene = True
                st.rerun()
        except Exception as e:
            st.error(f"대화 중 오류: {e}")

# --- 5. Truth Lens 개입 섹션 ---
if st.session_state.intervene:
    st.divider()
    with st.container(border=True):
        st.error("🚨 Truth Lens: 위험 감지!")
        # 사용자님이 1월 16일 등에 구상했던 정보처리기사 공부 내용처럼 정확한 인지가 필요함
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.info(f"방어 문장을 입력하세요: **{target}**")
        
        user_input = st.text_input("입력:", key="defense")
        if st.button("차단 완료"):
            if user_input.strip() == target:
                st.success("✅ 성공적으로 방어했습니다!")
                st.balloons()
                if st.button("다시 하기"):
                    st.session_state.clear()
                    st.rerun()
