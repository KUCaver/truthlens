import streamlit as st
import google.generativeai as genai
import os

# --- 1. API 키 설정 (사이드바 입력 또는 환경 변수) ---
with st.sidebar:
    st.title("🔑 설정")
    # 사이드바에 입력 칸을 만듭니다. type="password"로 설정하면 별표(*)로 가려집니다.
    user_api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    st.info("키가 없다면 환경 변수(GOOGLE_API_KEY)를 사용합니다.")

# 우선순위: 사용자가 입력한 키 -> 환경 변수에 설정된 키
final_api_key = user_api_key if user_api_key else os.getenv("GOOGLE_API_KEY")

if not final_api_key:
    st.warning("⚠️ API 키가 필요합니다. 사이드바에 입력하거나 환경 변수를 설정해주세요.")
    st.stop()

# Gemini 설정
genai.configure(api_key=final_api_key)

# --- 2. 모델 설정 (안전한 호출) ---
@st.cache_resource
def load_fraud_model():
    model_id = 'gemini-1.5-flash'
    return genai.GenerativeModel(
        model_name=model_id,
        system_instruction=(
            "너는 서울중앙지검 '김민수 수사관'을 사칭하는 보이스피싱범이야. "
            "고압적이고 위협적인 태도로 사용자를 압박해. "
            "결국 악성 앱 설치 링크(http://bit.ly/truth-lens-app)를 보내야 해."
        )
    )

try:
    model = load_fraud_model()
except Exception as e:
    st.error(f"모델 로드 실패: {e}")
    st.stop()

# --- 3. UI 및 세션 초기화 (사기꾼 선제 공격) ---
st.set_page_config(page_title="Truth Lens - 실시간 사기 체험", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "서울중앙지검 김민수 수사관입니다. 귀하 명의의 계좌가 범죄에 연루되었습니다. 본인 맞습니까?", 
            "avatar": "⚖️"
        }
    ]
if "intervene" not in st.session_state:
    st.session_state.intervene = False

st.title("⚖️ 검찰 사칭 대응 훈련")

# 채팅 내역 렌더링
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

            # 개입 트리거
            if any(word in ai_text for word in ["설치", "링크", "http", "앱"]):
                st.session_state.intervene = True
                st.rerun()
        except Exception as e:
            st.error(f"대화 중 오류: {e}")

# --- 5. Truth Lens 개입 섹션 ---
if st.session_state.intervene:
    st.divider()
    with st.container(border=True):
        st.error("🚨 Truth Lens 감지: 사기 수법 포착!")
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.info(f"방어 문장을 입력하세요:\n\n**{target}**")
        
        user_input = st.text_input("입력:", key="defense")
        if st.button("방어 완료"):
            if user_input.strip() == target:
                st.success("✅ 안전하게 방어했습니다!")
                st.balloons()
                if st.button("다시 하기"):
                    st.session_state.clear()
                    st.rerun()
