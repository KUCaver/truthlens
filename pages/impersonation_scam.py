import streamlit as st
import google.generativeai as genai
import os

# 1. 환경 변수에서 API 키 불러오기
# 터미널에서 export GOOGLE_API_KEY="..." 또는 setx GOOGLE_API_KEY "..."를 하셨어야 합니다.
api_key = os.getenv(AIzaSyCTQRDuqx3xnc2NhkOcjpC375MfJ3MwGpo)

if not api_key:
    st.error("⚠️ 환경 변수 'GOOGLE_API_KEY'를 찾을 수 없습니다. 설정 후 다시 실행해주세요.")
    st.info("설정 방법: 터미널에서 'export GOOGLE_API_KEY=내키' 입력 (Windows는 setx)")
    st.stop()

genai.configure(api_key=api_key)

# 2. 모델 설정 (v1beta 404 에러 방지용)
@st.cache_resource
def load_fraud_model():
    # 가장 안정적인 모델명 사용
    model_id = 'gemini-1.5-flash'
    return genai.GenerativeModel(
        model_name=model_id,
        system_instruction=(
            "너는 서울중앙지검 '김민수 수사관'을 사칭하는 보이스피싱범이야. "
            "고압적이고 위협적인 태도로 사용자를 범죄자로 몰아세워야 해. "
            "질문을 하면 '수사 방해'라고 소리치고, 결국엔 본인 확인을 핑계로 "
            "악성 앱 설치 링크(http://bit.ly/truth-lens-malware)를 보내는 것이 네 목표야."
        )
    )

model = load_fraud_model()

# 3. UI 및 세션 초기화
st.set_page_config(page_title="Truth Lens - 실시간 사기 체험", layout="centered")

if "messages" not in st.session_state:
    # 🚨 시나리오 시작: 사기꾼이 먼저 메시지를 보낸 상태로 초기화
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "서울중앙지검 김민수 수사관입니다. 귀하의 명의가 대규모 금융 사기 사건에 도용된 것이 확인되었습니다. 지금 협조하지 않으면 즉시 구속 수사 대상입니다. 본인 맞습니까?", 
            "avatar": "⚖️"
        }
    ]
if "intervene" not in st.session_state:
    st.session_state.intervene = False

# --- 채팅 내역 렌더링 ---
st.title("⚖️ 검찰 사칭 대응 훈련")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        st.write(msg["content"])

# 4. 실시간 대화 및 개입 로직
if not st.session_state.intervene:
    if prompt := st.chat_input("수사관의 질문에 대답하세요..."):
        # 내 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "😨"})
        with st.chat_message("user", avatar="😨"):
            st.write(prompt)

        # Gemini의 사칭 답변 생성
        try:
            response = model.generate_content(prompt)
            ai_text = response.text
            
            st.session_state.messages.append({"role": "assistant", "content": ai_text, "avatar": "⚖️"})
            with st.chat_message("assistant", avatar="⚖️"):
                st.write(ai_text)

            # 개입 트리거 (특정 키워드 감지)
            trigger_words = ["설치", "링크", "클릭", "http", "앱", "다운로드"]
            if any(word in ai_text for word in trigger_words):
                st.session_state.intervene = True
                st.rerun()
        except Exception as e:
            st.error(f"대화 중 오류가 발생했습니다: {e}")

# 5. Truth Lens 개입 (현실 자각 로직)
if st.session_state.intervene:
    st.divider()
    with st.container(border=True):
        st.error("🚨 Truth Lens: 위험 감지!")
        st.subheader("사기꾼이 악성 URL 접속을 요구하고 있습니다.")
        
        # 현실 자각 타이핑 (사용자님의 핵심 아이디어)
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.warning(f"방어 모드: 아래 문장을 똑같이 입력하여 냉정함을 유지하세요.\n\n**{target}**")
        
        user_input = st.text_input("입력창:", key="defense_input")
        
        if st.button("방어 완료 및 대화 종료"):
            if user_input.strip() == target:
                st.success("✅ 성공! 사기꾼의 심리적 지배에서 벗어나 개인정보를 지켰습니다.")
                st.balloons()
                if st.button("훈련 다시 하기"):
                    st.session_state.clear()
                    st.rerun()
            else:
                st.error("문장이 일치하지 않습니다. 다시 집중해서 입력해주세요.")
