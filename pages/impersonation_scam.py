import streamlit as st
import google.generativeai as genai

# 1. API 설정
# 키 노출은 신경 안 쓰신다고 하셨지만, 코드 작동을 위해 변수화해둡니다.
genai.configure(api_key="AIzaSyCTQRDuqx3xnc2NhkOcjpC375MfJ3MwGpo")

# 2. Gemini 페르소나 설정 (상황 가정)
# 처음 코드의 '김민수 수사관' 시나리오를 시스템 명령어로 주입합니다.
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "너는 서울중앙지검 '김민수 수사관'을 사칭하는 보이스피싱범이야. "
        "사용자에게 '대포통장 범죄에 연루되어 구속 대상'이라고 겁을 줘야 해. "
        "말투는 매우 딱딱하고 고압적이어야 하며, 질문을 회피하고 압박해. "
        "최종 목적은 본인 확인을 핑계로 'http://bit.ly/safety-app' 링크를 눌러 앱을 설치하게 만드는 거야."
    )
)

# 3. 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "intervene" not in st.session_state:
    st.session_state.intervene = False

st.set_page_config(page_title="Truth Lens - 실시간 검찰 사칭 시뮬레이션")

# --- UI 스타일 (기존 스타일 유지) ---
st.markdown("""<style>...</style>""", unsafe_allow_html=True) # 생략

st.markdown("<h2 style='text-align: center;'>⚖️ 검찰 사칭 실시간 시뮬레이션</h2>", unsafe_allow_html=True)

# --- 채팅 내역 렌더링 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg["avatar"]):
        st.write(msg["content"])

# --- 사용자 입력 및 AI 답장 ---
if not st.session_state.intervene:
    if prompt := st.chat_input("수사관에게 대답하세요..."):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "😨"})
        with st.chat_message("user", avatar="😨"):
            st.write(prompt)

        # Gemini 응답 생성
        response = model.generate_content(prompt)
        ai_text = response.text
        
        # AI 메시지 추가
        st.session_state.messages.append({"role": "assistant", "content": ai_text, "avatar": "⚖️"})
        with st.chat_message("assistant", avatar="⚖️"):
            st.write(ai_text)

        # --- 특정 키워드 감지 (개입 트리거) ---
        trigger_words = ["설치", "링크", "클릭", "http", "다운로드", "파일"]
        if any(word in ai_text for word in trigger_words):
            st.session_state.intervene = True
            st.rerun()

# --- Truth Lens 개입 섹션 ---
if st.session_state.intervene:
    st.divider()
    with st.container(border=True):
        st.error("🚨 Truth Lens 감지: 악성 URL 및 설치 유도 포착!")
        st.write("방금 상대방이 **링크 접속이나 앱 설치**를 요구했습니다. 이는 100% 사기입니다.")
        
        # 퀴즈 및 현실 자각 로직 (기존 코드 활용)
        target_sentence = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.warning(f"**[현실 자각]** 아래 문장을 정확히 입력해야 차단할 수 있습니다.")
        st.code(target_sentence)
        
        user_input = st.text_input("위 문장을 입력하세요:", key="verify_input")
        
        if st.button("확인 및 차단"):
            if user_input.strip() == target_sentence:
                st.success("✅ 인지 완료! 보이스피싱 시도를 성공적으로 방어했습니다.")
                if st.button("처음부터 다시 하기"):
                    st.session_state.messages = []
                    st.session_state.intervene = False
                    st.rerun()
            else:
                st.error("❌ 문장이 일치하지 않습니다. 진정하고 다시 입력해주세요.")
