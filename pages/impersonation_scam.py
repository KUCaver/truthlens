import streamlit as st
from google import genai
import os
import random

# --- 1. API 및 클라이언트 설정 ---
API_KEY = "AIzaSyDH-4lwnsiRzQkWNd02AAk_xlBf4Slr41k"
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.0-flash" 

# --- 2. 다크 모드 스마트폰 프레임 CSS ---
st.set_page_config(page_title="Truth Lens - 실시간 자산 보호", layout="centered")

st.markdown("""
<style>
    /* 전체 배경: 짙은 다크 그레이 */
    .stApp {
        background-color: #0e1117;
    }
    /* 스마트폰 본체: 매트 블랙 */
    .phone-container {
        border: 12px solid #1f1f1f;
        border-radius: 45px;
        padding: 25px;
        width: 380px;
        height: 800px;
        margin: auto;
        background-color: #161b22; /* 폰 내부 배경 */
        box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        overflow-y: auto;
        color: #e6edf3;
        position: relative;
    }
    /* 상단 스피커 및 노치 영역 */
    .phone-header {
        width: 150px;
        height: 18px;
        background: #1f1f1f;
        border-bottom-left-radius: 15px;
        border-bottom-right-radius: 15px;
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10;
    }
    /* 채팅 메시지 다크 스타일 강제 적용 */
    [data-testid="stChatMessage"] {
        background-color: #21262d !important;
        border-radius: 15px;
    }
    /* 입력창 다크 스타일 */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    /* 스크롤바 숨기기 */
    .phone-container::-webkit-scrollbar { display: none; }
</style>
""", unsafe_allow_html=True)

# --- 3. 시스템 설정 ---
FRAUD_INSTRUCTION = "너는 보이스피싱범 김민수 수사관이야. 실제 문자처럼 딱딱하고 고압적으로 말해. 지문/괄호 금지. http://bit.ly/secure-app 설치 유도."
SECURITY_ALERTS = [
    "⚠️ [분석] 사기 패턴 98.7% 일치",
    "⚠️ [경고] 고압적 압박 수법 감지",
    "⚠️ [주의] 수사기관은 문자로 앱 설치 요구 안 함"
]

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "서울중앙지검 김민수 수사관입니다. 본인 맞습니까?", "avatar": "⚖️"}]
if "first_view" not in st.session_state:
    st.session_state.first_view = True
if "show_barrier" not in st.session_state:
    st.session_state.show_barrier = False

# --- 4. 스마트폰 렌더링 시작 ---
st.markdown('<div class="phone-container"><div class="phone-header"></div>', unsafe_allow_html=True)

# [Step 1] 첫 화면: 이미지/TXT 공고문
if st.session_state.first_view:
    st.subheader("⚖️ 긴급 사건 통지")
    image_path = "fraud_evidence.png"
    
    if os.path.exists(image_path):
        st.image(image_path, caption="검찰 수사 서류")
    else:
        st.error("❗ [긴급] 전자 기록물 통지")
        st.markdown("""
        **사건번호**: 2026-형제-771138  
        귀하는 금융범죄 피의자로 지정되었습니다. 즉시 수사에 협조하십시오.
        """)
    
    if st.button("메시지 확인"):
        st.session_state.first_view = False
        st.rerun()
else:
    # [Step 2] 실시간 대화창
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg.get("avatar", "😨")):
            st.write(msg["content"])

    # [Step 3] 실시간 보안 분석 (과속 방지턱 팝업)
    st.warning(f"🛡️ Truth Lens: {random.choice(SECURITY_ALERTS)}")

    # 입력 및 대화 로직
    if not st.session_state.show_barrier:
        if prompt := st.chat_input("문자 답장 입력..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            try:
                response = client.models.generate_content(model=MODEL_ID, contents=f"{FRAUD_INSTRUCTION}\n\n사용자: {prompt}")
                st.session_state.messages.append({"role": "assistant", "content": response.text, "avatar": "⚖️"})
                st.rerun()
            except Exception as e:
                st.error(f"오류: {e}")

    # [Step 4] URL 클릭 시 Truth Lens 고유 방어 장치
    last_msg = st.session_state.messages[-1]["content"]
    if "http" in last_msg and not st.session_state.show_barrier:
        if st.button("🔗 보안 링크 확인 (클릭)", type="primary"):
            st.session_state.show_barrier = True
            st.rerun()

    if st.session_state.show_barrier:
        st.error("🛑 [차단] Truth Lens 시스템 개입")
        
        if st.button("📞 경찰청(1301) 즉시 신고"):
            st.success("✅ 자산 보호 완료! 사기 방어 성공!!")
            st.balloons()
        
        st.markdown("---")
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.warning(f"방어 장치: 문장 입력\n\n**\"{target}\"**")
        
        user_input = st.text_input("타이핑 하세요:", key="barrier")
        if user_input.strip() == target:
            st.error("❗ [최종 경고] 위험은 여전합니다. 정말 이동하시겠습니까?")
            st.link_button("⚠️ 위험 무시하고 이동", "https://www.polico.go.kr/index.do")
            if st.button("🚫 차단 완료 및 종료"):
                st.success("✅ 자산 보호 완료! 방어 성공!!")
                st.balloons()

st.markdown('</div>', unsafe_allow_html=True) # 스마트폰 프레임 끝
