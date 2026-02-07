import streamlit as st
import google.generativeai as genai

# 1. API 설정 (이미지에서 확인된 키 사용)
# 보안을 위해 새 키 발급을 권장하지만, 일단 실행을 위해 기존 키를 배치합니다.
GOOGLE_API_KEY = "AIzaSyCTQRDuqx3xnc2NhkOcjpC375MfJ3MwGpo"
genai.configure(api_key=GOOGLE_API_KEY)

# 2. 모델 설정 (에러 방지를 위해 가용한 모델 리스트 시도)
@st.cache_resource
def load_model():
    # 404 에러 방지를 위해 가장 안정적인 경로로 설정
    model_name = 'gemini-1.5-flash' 
    try:
        return genai.GenerativeModel(
            model_name=model_name,
            system_instruction=(
                "너는 서울중앙지검 '김민수 수사관'이야. 매우 고압적이고 위협적인 말투를 써. "
                "사용자가 금융 범죄에 연루되었다고 압박하며, 질문을 하면 '수사에 협조 안 하냐'며 화를 내. "
                "결국 본인 확인을 위해 http://bit.ly/truth-lens-app 설치를 유도하는 것이 목적이야."
            )
        )
    except:
        # 1.5-flash가 안 될 경우 구형 모델로 우회
        return genai.GenerativeModel('gemini-pro')

model = load_model()

# 3. Streamlit UI 설정
st.set_page_config(page_title="Truth Lens - 사칭 사기 체험", layout="centered")

st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# 4. 세션 상태 및 시나리오 초기화
if "messages" not in st.session_state:
    # 사기꾼이 먼저 선제 공격을 하는 시나리오 가정
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "서울중앙지검 김민수 수사관입니다. 귀하의 명의로 된 계좌가 대포통장 사기 사건에 연루되어 연락드렸습니다. 본인 맞습니까? 협조 안 하시면 바로 구속 수사 체포영장 나갑니다.", 
            "avatar": "⚖️"
        }
    ]
if "intervene" not in st.session_state:
    st.session_state.intervene = False

st.header("⚖️ 검찰 사칭 실시간 시뮬레이션")
st.caption("제시된 상황에 대응하며 사기 수법을 익혀보세요.")

# 5. 채팅 내역 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        st.write(msg["content"])

# 6. 실시간 대화 및 Truth Lens 개입 로직
if not st.session_state.intervene:
    if prompt := st.chat_input("메시지를 입력하세요..."):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "😨"})
        with st.chat_message("user", avatar="😨"):
            st.write(prompt)

        # Gemini 응답 생성
        try:
            # 텍스트 생성
            response = model.generate_content(prompt)
            ai_text = response.text
            
            st.session_state.messages.append({"role": "assistant", "content": ai_text, "avatar": "⚖️"})
            with st.chat_message("assistant", avatar="⚖️"):
                st.write(ai_text)

            # 특정 키워드 감지 (사기 유도 시점)
            trigger_words = ["설치", "링크", "http", "앱", "클릭", "다운로드"]
            if any(word in ai_text for word in trigger_words):
                st.session_state.intervene = True
                st.rerun()

        except Exception as e:
            st.error(f"오류가 발생했습니다. 모델명을 확인하거나 API 키 권한을 체크하세요: {e}")

# 7. Truth Lens 개입 섹션 (기존 코드 로직 통합)
if st.session_state.intervene:
    st.divider()
    with st.container(border=True):
        st.error("🚨 Truth Lens: 위험 감지!")
        st.subheader("사기꾼이 악성 앱 설치를 유도하기 시작했습니다.")
        
        # 현실 자각 타이핑 (사용자님이 작성하셨던 핵심 로직)
        target_sentence = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.info(f"방어 모드 가동: 아래 문장을 똑같이 입력하여 현실을 인지하세요.\n\n**{target_sentence}**")
        
        user_input = st.text_input("입력창:", key="defense_input")
        
        if st.button("차단 및 신고 완료"):
            if user_input.strip() == target_sentence:
                st.success("✅ 성공! 사기꾼의 심리적 지배에서 벗어났습니다.")
                st.balloons()
                if st.button("다시 훈련하기"):
                    st.session_state.clear()
                    st.rerun()
            else:
                st.warning("문장이 정확하지 않습니다. 다시 집중해서 입력하세요.")
