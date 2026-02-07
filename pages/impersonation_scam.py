import streamlit as st
from google import genai
import os

# --- 1. API 설정 ---
API_KEY = "AIzaSyDH-4lwnsiRzQkWNd02AAk_xlBf4Slr41k"
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.0-flash" 

# --- 2. UI 스타일 (실제 보안 앱 느낌) ---
st.set_page_config(page_title="Truth Lens - 실시간 자산 보호", layout="centered")
st.markdown("""
<style>
    .stAlert { border-radius: 15px; border: 2px solid #ff4b4b; }
    .stButton > button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .main-text { font-size: 1.2rem; font-weight: 600; color: #31333F; }
</style>
""", unsafe_allow_html=True)

# --- 3. 세션 상태 초기화 ---
if "step" not in st.session_state:
    st.session_state.step = "CHAT" 
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "서울중앙지검 김민수 수사관입니다. 본인 맞습니까?", "avatar": "⚖️"}]

st.title("🛡️ Truth Lens 실시간 탐지")

# --- 4. 대화 단계 (AI 모니터링) ---
if st.session_state.step == "CHAT":
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg.get("avatar", "😨")):
            st.write(msg["content"])

    if prompt := st.chat_input("수사관에게 답변 중..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # AI 사기꾼 답변 생성
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"너는 보이스피싱범이야. 고압적으로 압박하다가 링크 클릭(http://bit.ly/secure-app)을 강요해: {prompt}"
        )
        ai_text = response.text
        st.session_state.messages.append({"role": "assistant", "content": ai_text, "avatar": "⚖️"})
        
        # [과속 방지턱 발동 조건] 위험 키워드 감지
        if any(word in ai_text for word in ["설치", "클릭", "입금", "결제", "링크", "http"]):
            st.session_state.step = "INTERVENTION" # 개입 단계로 강제 전환
        st.rerun()

# --- 5. [과속 방지턱] 실전 개입 팝업 단계 ---
if st.session_state.step == "INTERVENTION":
    st.divider()
    with st.container(border=True):
        st.error("🚨 [위험 감지] 사용자 행동 일시 차단")
        st.markdown("<p class='main-text'>방금 전송된 요청은 사기일 가능성이 99%입니다.</p>", unsafe_allow_html=True)
        
        # [즉시 대응] 버튼 형식으로 바로 연락 가능하게 배치
        col1, col2 = st.columns(2)
        with col1:
            st.button("📞 경찰청(1301) 즉시 연결", on_click=lambda: st.toast("경찰청 연결 시도 중..."))
        with col2:
            st.button("📞 지인에게 도움 요청", on_click=lambda: st.toast("사전에 등록된 지인에게 알림을 보냅니다."))
        
        st.markdown("---")
        
        # [방어장치] 문장 타이핑을 통한 '생각할 시간' 벌기 (과속 방지턱)
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.info(f"💡 **방어 장치 작동**: 아래 문장을 정확히 입력해야 다음 행동이 가능합니다. (인지 능력 회복 단계)")
        st.markdown(f"**\"{target}\"**")
        
        user_input = st.text_input("보안 문장 입력 (직접 타이핑):", key="safety_barrier")

        if st.button("문장 확인"):
            if user_input.strip() == target:
                st.session_state.step = "FINAL_WARNING" # 최종 경고 단계로 이동
                st.rerun()
            else:
                st.error("문장이 일치하지 않습니다. 긴장을 풀고 천천히 다시 입력하세요.")

# --- 6. [최종 경고] 문장 입력 후에도 다시 한 번 확인 ---
if st.session_state.step == "FINAL_WARNING":
    st.warning("🚨 마지막 경고입니다.")
    st.markdown("<p class='main-text'>보안 문장을 입력하셨지만, 시스템은 여전히 이 이동을 권장하지 않습니다.</p>", unsafe_allow_html=True)
    st.write("해당 링크를 클릭하는 순간 모든 보안 책임은 사용자에게 있으며, 자산 유출 위험이 매우 높습니다.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        # 최종 확인 후 이동
        st.link_button("⚠️ 위험 무시하고 이동 (권장하지 않음)", "https://www.polico.go.kr/index.do", type="primary")
    with col_b:
        if st.button("✅ 이제 안전함을 인지함 (종료)"):
            st.success("안전하게 보호되었습니다!")
            if st.button("처음으로 돌아가기"):
                st.session_state.clear()
                st.rerun()
