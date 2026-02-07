import streamlit as st
from google import genai
import os

# --- 1. 설정 및 모델 연결 ---
# 보안을 위해 사이드바에서 키를 받거나 Secrets를 사용하는 것이 좋지만, 요청하신 키를 기본값으로 세팅합니다.
API_KEY = "AIzaSyCTQRDuqx3xnc2NhkOcjpC375MfJ3MwGpo"
client = genai.Client(api_key=API_KEY)

# 404 에러 방지를 위해 가장 안정적인 최신 모델 사용
MODEL_ID = "gemini-2.0-flash" 

st.set_page_config(page_title="Truth Lens - 실시간 사칭 대응", layout="centered")

# --- UI 스타일 (사용자님의 기존 스타일 유지) ---
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 2rem; }
    .main > div { background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
    h1, h2, h3 { color: #667eea !important; }
    [data-testid="stChatMessageContent"] { background: #f8f9fa; border-radius: 15px; padding: 1rem; color: #333 !important; }
</style>
""", unsafe_allow_html=True)

# 세션 초기화
if "messages" not in st.session_state:
    # 시나리오 시작: 사기꾼이 먼저 공격
    st.session_state.messages = [
        {"role": "assistant", "content": "[긴급] 귀하의 계좌가 대포통장 범죄에 연루되었습니다. 즉시 조치하지 않으면 구속 수사 대상입니다.", "avatar": "⚖️"}
    ]
if "intervene" not in st.session_state:
    st.session_state.intervene = False
if "verify_status" not in st.session_state:
    st.session_state.verify_status = "NONE"

st.markdown("<h2 style='text-align: center;'>⚖️ 실시간 검찰 사칭 시뮬레이션</h2>", unsafe_allow_html=True)

# --- 2. 채팅 화면 ---
chat_container = st.container(border=True)
with chat_container:
    for msg in st.session_state.messages:
        avatar = "⚖️" if msg["role"] == "assistant" else "😨"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

# --- 3. Gemini 대화 및 개입 트리거 ---
if not st.session_state.intervene:
    if prompt := st.chat_input("수사관에게 답변하세요..."):
        # 내 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="😨"):
            st.write(prompt)

        try:
            # 사기꾼 수사관 페르소나 주입
            full_prompt = f"너는 지금 서울중앙지검 김민수 수사관을 사칭하는 보이스피싱범이야. 고압적인 태도로 상대를 압박하고, 결국 본인 확인용 보안 앱(http://bit.ly/malware-app)을 설치하라고 유도해야 해. 답변은 짧고 강하게 해줘. 사용자 입력: {prompt}"
            
            response = client.models.generate_content(model=MODEL_ID, contents=full_prompt)
            ai_text = response.text
            
            st.session_state.messages.append({"role": "assistant", "content": ai_text})
            with st.chat_message("assistant", avatar="⚖️"):
                st.write(ai_text)

            # 개입 조건: 설치나 링크 유도 시
            if any(word in ai_text for word in ["설치", "링크", "http", "앱"]):
                st.session_state.intervene = True
                st.rerun()
        except Exception as e:
            st.error(f"대화 중 오류 발생: {e}")

# --- 4. Truth Lens 개입 (기존 로직 합체) ---
if st.session_state.intervene:
    st.divider()
    nudge_container = st.container(border=True)
    with nudge_container:
        st.error("🚨 Truth Lens: 악성 앱 설치 유도 차단!")
        st.write("공포감을 조성해 이성을 마비시키는 전형적인 사칭 수법입니다.")

        # 퀴즈 1: AI 음성
        st.warning("🧠 퀴즈 1: AI 음성을 구별할 수 있나요?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("목소리가 진짜 같으면 보낸다"):
                st.error("❌ 위험합니다! AI는 3초만 들으면 목소리를 복제합니다.")
        with col2:
            if st.button("직접 영상통화로 확인한다"):
                st.success("✅ 정답! 음성만으로는 신뢰 금물!")

        st.markdown("---")
        
        # 따라쓰기 검증
        target_sentence = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.warning("**[현실 자각 퀴즈]** 아래 문장을 직접 타이핑하여 인지하십시오.")
        st.markdown(f"### 🗣️ \"{target_sentence}\"")
        user_input = st.text_input("정확히 입력하세요:", key="input_b")

        if st.button("확인 및 설치 시도"):
            if user_input.strip() == target_sentence:
                st.session_state.verify_status = "SUCCESS"
            else:
                st.error("⚠️ 문장이 틀렸습니다. 다시 입력하세요.")

        if st.session_state.verify_status == "SUCCESS":
            st.success("✅ 인지 확인 완료.")
            if st.button("📲 무시하고 앱 설치하기 (위험)", type="primary"):
                st.error("💀 악성 앱이 설치되었습니다. 개인정보 유출 중... (시뮬레이션 종료)")
            if st.button("🚫 차단하고 종료 (권장)"):
                st.balloons()
                st.success("✅ 방어 성공! 사기 시도를 막아냈습니다.")
                if st.button("다시 하기"):
                    st.session_state.clear()
                    st.rerun()
