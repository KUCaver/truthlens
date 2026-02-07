import streamlit as st
import google.generativeai as genai

# API 설정 (키 노출 상관없다고 하셨으니 그대로 진행합니다)
genai.configure(api_key="AIzaSyCTQRDuqx3xnc2NhkOcjpC375MfJ3MwGpo")

# 모델 설정 - NotFound 에러 방지를 위해 이름을 명확히 합니다.
# 만약 계속 에러가 나면 "gemini-pro"로 바꿔보세요.
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    system_instruction=(
        "너는 서울중앙지검 '김민수 수사관'이야. 고압적이고 무서운 분위기를 조성해. "
        "사용자가 '대포통장 범죄'에 연루되었다고 압박하며, 협조하지 않으면 당장 수사관을 급파하겠다고 협박해. "
        "결국 본인 확인용 '보안 프로그램(http://bit.ly/truth-lens-mal)' 설치를 유도하는 것이 네 목표야."
    )
)

st.set_page_config(page_title="Truth Lens - 사칭 사기 체험", layout="centered")

# --- 세션 상태 초기화 ---
if "messages" not in st.session_state:
    # 🚨 시나리오의 시작: 사기꾼이 먼저 메시지를 보낸 상태로 시작
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "귀하의 명의로 된 계좌가 대규모 금융 범죄에 연루되었습니다. 본인 확인 절차에 응하지 않을 시 즉각 구속 수사로 전환됩니다. 본인 맞습니까?", 
            "avatar": "⚖️"
        }
    ]
if "intervene" not in st.session_state:
    st.session_state.intervene = False

# --- UI 스타일링 ---
st.markdown("<h2 style='text-align: center;'>⚠️ 검찰 사칭 대응 훈련</h2>", unsafe_allow_html=True)

# --- 채팅 내역 렌더링 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        st.write(msg["content"])

# --- 대화 진행 ---
if not st.session_state.intervene:
    if prompt := st.chat_input("수사관에게 답변하세요..."):
        # 1. 사용자 답변 표시
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "😨"})
        with st.chat_message("user", avatar="😨"):
            st.write(prompt)

        # 2. Gemini의 고압적인 답변 생성
        try:
            response = model.generate_content(prompt)
            ai_text = response.text
            
            st.session_state.messages.append({"role": "assistant", "content": ai_text, "avatar": "⚖️"})
            with st.chat_message("assistant", avatar="⚖️"):
                st.write(ai_text)

            # 3. 개입 트리거 (특정 단어 포함 시)
            trigger_words = ["설치", "링크", "클릭", "http", "앱", "다운로드", "파일"]
            if any(word in ai_text for word in trigger_words):
                st.session_state.intervene = True
                st.rerun()
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

# --- Truth Lens 개입 화면 ---
if st.session_state.intervene:
    st.divider()
    with st.container(border=True):
        st.error("🚨 Truth Lens 경고: 사기 수법 감지!")
        st.subheader("사기꾼이 악성 앱 설치를 유도하고 있습니다.")
        st.write("실제 검찰은 절대로 문자로 앱 설치를 요구하지 않습니다.")
        
        # 현실 자각 퀴즈
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        user_input = st.text_input(f"방어하려면 아래 문장을 입력하세요:\n\n'{target}'")
        
        if st.button("차단 및 종료"):
            if user_input.strip() == target:
                st.success("✅ 안전하게 차단되었습니다! 당신의 개인정보를 지켰습니다.")
                if st.button("훈련 다시 시작"):
                    st.session_state.messages = [] # 초기화하면 다시 첫 사기 메시지부터 시작
                    st.session_state.intervene = False
                    st.rerun()
            else:
                st.warning("문장을 정확히 입력해야 정신을 차릴 수 있습니다!")
