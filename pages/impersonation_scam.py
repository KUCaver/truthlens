import streamlit as st
import google.generativeai as genai

# 1. API 키 설정 (사용자님 대시보드에서 확인된 키)
genai.configure(api_key="AIzaSyCTQRDuqx3xnc2NhkOcjpC375MfJ3MwGpo")

# 2. 모델 설정 (404 에러 방지를 위한 안정적 설정)
@st.cache_resource
def get_model():
    # v1beta에서 가장 안정적인 최신 모델 명칭 사용
    model_id = 'gemini-1.5-flash'
    return genai.GenerativeModel(
        model_name=model_id,
        system_instruction=(
            "너는 검찰을 사칭하는 사기꾼 '김민수 수사관'이야. "
            "사용자를 범죄자로 몰아세우며 매우 무섭고 고압적으로 말해. "
            "결국 본인 인증을 위해 http://bit.ly/truth-lens-app 설치를 유도해야 해."
        )
    )

model = get_model()

# 3. 세션 상태 및 첫 메시지 설정 (사기꾼의 선제 공격)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "서울중앙지검 김민수 수사관입니다. 본인 명의 계좌가 대포통장 사기 사건에 연루되었습니다. 협조 안 하시면 즉시 영장 발부됩니다. 본인 맞습니까?", 
            "avatar": "⚖️"
        }
    ]
if "intervene" not in st.session_state:
    st.session_state.intervene = False

# --- UI 설정 ---
st.set_page_config(page_title="Truth Lens - 실시간 체험", layout="centered")
st.title("🛡️ Truth Lens: 사칭 사기 대응 훈련")

# 채팅 내역 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        st.write(msg["content"])

# 4. 실시간 대화 및 개입 로직
if not st.session_state.intervene:
    if prompt := st.chat_input("메시지를 입력하세요..."):
        # 사용자 메시지 표시
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "😨"})
        with st.chat_message("user", avatar="😨"):
            st.write(prompt)

        # Gemini 응답 생성
        try:
            response = model.generate_content(prompt)
            ai_text = response.text
            
            st.session_state.messages.append({"role": "assistant", "content": ai_text, "avatar": "⚖️"})
            with st.chat_message("assistant", avatar="⚖️"):
                st.write(ai_text)

            # 개입 트리거 (특정 키워드 감지)
            trigger_words = ["설치", "링크", "클릭", "http", "앱"]
            if any(word in ai_text for word in trigger_words):
                st.session_state.intervene = True
                st.rerun()
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# 5. Truth Lens 개입 (사용자님의 2월 1일 프로젝트 로직 통합)
if st.session_state.intervene:
    st.divider()
    with st.container(border=True):
        st.error("🚨 Truth Lens: 위험 감지!")
        st.subheader("사기꾼이 악성 앱 설치를 유도했습니다.")
        
        # 현실 자각 타이핑 로직
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.info(f"방어 모드: 아래 문장을 똑같이 입력하여 냉정함을 되찾으세요.\n\n**{target}**")
        
        user_input = st.text_input("여기에 정확히 입력하세요:", key="defense")
        
        if st.button("차단 및 방어 완료"):
            if user_input.strip() == target:
                st.success("✅ 성공! 사기꾼의 심리적 지배를 끊어냈습니다.")
                st.balloons()
                if st.button("새 훈련 시작"):
                    st.session_state.clear()
                    st.rerun()
            else:
                st.warning("문장이 틀렸습니다. 다시 입력하여 위험을 인지하세요.")
