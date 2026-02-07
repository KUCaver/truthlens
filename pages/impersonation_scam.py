import streamlit as st
import google.generativeai as genai

# 1. API 키 설정 (노출 경고가 떴던 그 키를 그대로 사용하되, 가급적 새로 발급 권장)
genai.configure(api_key="AIzaSyCTQRDuqx3xnc2NhkOcjpC375MfJ3MwGpo")

# 2. 모델 설정 (404 에러 방지를 위한 안전한 호출)
try:
    # 최신 flash 모델 시도
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    # 실패 시 가장 범용적인 pro 모델로 우회
    model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="Truth Lens - 사칭 사기 훈련", layout="centered")

# --- UI 스타일링 ---
st.markdown("""
<style>
    .stApp { background-color: #f0f2f6; }
    [data-testid="stChatMessage"] { border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# 3. 세션 상태 초기화 (사기꾼이 먼저 말을 거는 시나리오)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "서울중앙지검 김민수 수사관입니다. 귀하 명의의 통장이 범죄에 연루되어 연락드렸습니다. 지금 즉시 협조하지 않으면 구속 수사 대상입니다. 본인 맞습니까?", 
            "avatar": "⚖️"
        }
    ]
if "intervene" not in st.session_state:
    st.session_state.intervene = False

st.title("⚖️ 실시간 검찰 사칭 시뮬레이션")
st.info("상대방의 압박에 대응하며 사기 수법을 파악해 보세요.")

# 4. 채팅 내역 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        st.write(msg["content"])

# 5. 실시간 대화 로직
if not st.session_state.intervene:
    if prompt := st.chat_input("답변을 입력하세요..."):
        # 내 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "😨"})
        with st.chat_message("user", avatar="😨"):
            st.write(prompt)

        # Gemini의 사기꾼 연기
        # 이전 대화 맥락을 포함하여 고압적인 태도를 유지하도록 유도
        full_prompt = f"너는 지금 사기를 치는 검찰 수사관이야. 다음 사용자의 말에 더 고압적이고 무섭게 대답해. 결국 보안 앱 설치(http://bit.ly/malware-app)를 시켜야 해: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            ai_text = response.text
            
            st.session_state.messages.append({"role": "assistant", "content": ai_text, "avatar": "⚖️"})
            with st.chat_message("assistant", avatar="⚖️"):
                st.write(ai_text)

            # 개입 트리거 (키워드 감지)
            trigger_words = ["설치", "링크", "클릭", "http", "앱"]
            if any(word in ai_text for word in trigger_words):
                st.session_state.intervene = True
                st.rerun()
        except Exception as e:
            st.error(f"대화 중 오류가 발생했습니다: {e}")

# 6. Truth Lens 개입 (현실 자각 로직)
if st.session_state.intervene:
    st.divider()
    with st.container(border=True):
        st.error("🚨 Truth Lens 위험 감지!")
        st.subheader("사기꾼이 악성 링크 접속을 유도했습니다.")
        
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.warning(f"방어하려면 아래 문장을 정확히 입력하세요:\n\n**{target}**")
        
        user_input = st.text_input("여기에 입력:", key="verify_input")
        
        if st.button("차단 및 훈련 종료"):
            if user_input.strip() == target:
                st.success("✅ 성공! 사기 수법을 완벽히 간파하셨습니다.")
                st.balloons()
                if st.button("다시 하기"):
                    del st.session_state.messages
                    st.session_state.intervene = False
                    st.rerun()
            else:
                st.error("문장이 틀렸습니다. 다시 입력해서 위험을 인지하세요.")
