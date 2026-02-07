import streamlit as st
from google import genai
import os
import random

# --- 1. API 및 클라이언트 설정 ---
API_KEY = "AIzaSyDH-4lwnsiRzQkWNd02AAk_xlBf4Slr41k" # 사용자님의 최신 키 반영
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.0-flash" 

# --- 2. 스마트폰 프레임 CSS 적용 ---
st.set_page_config(page_title="Truth Lens - 실시간 자산 보호", layout="centered")

st.markdown("""
<style>
    /* 전체 배경을 조금 어둡게 */
    .stApp {
        background-color: #f0f2f6;
    }
    /* 스마트폰 외형 프레임 */
    .phone-container {
        border: 12px solid #333;
        border-radius: 40px;
        padding: 20px;
        width: 380px;
        height: 800px;
        margin: auto;
        background-color: white;
        box-shadow: 0 20px 50px rgba(0,0,0,0.2);
        overflow-y: auto;
        position: relative;
    }
    /* 상단 스피커 구멍 */
    .phone-speaker {
        width: 60px;
        height: 5px;
        background: #333;
        border-radius: 10px;
        position: absolute;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
    }
    /* 스크롤바 숨기기 */
    .phone-container::-webkit-scrollbar {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 세션 및 시스템 설정 ---
FRAUD_INSTRUCTION = "너는 보이스피싱범 김민수 수사관이야. 실제 문자 대화처럼 딱딱하고 위협적으로 말해. 지문이나 (괄호) 금지. http://bit.ly/secure-app 링크 유도가 목표."
SECURITY_ALERTS = [
    "⚠️ [분석] 대화 패턴이 검찰 사칭 수법과 98% 일치합니다.",
    "⚠️ [경고] '수사 기밀' 등 공포 조장 단어 감지됨.",
    "⚠️ [주의] 수사기관은 문자로 앱 설치를 요구하지 않습니다."
]

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "서울중앙지검 김민수 수사관입니다. 본인 맞습니까?", "avatar": "⚖️"}]
if "first_view" not in st.session_state:
    st.session_state.first_view = True
if "show_barrier" not in st.session_state:
    st.session_state.show_barrier = False

# --- 4. 스마트폰 프레임 시작 ---
st.markdown('<div class="phone-container"><div class="phone-speaker"></div>', unsafe_allow_html=True)

# [STEP 1] 첫 화면: 이미지/TXT 공고문
if st.session_state.first_view:
    st.subheader("⚖️ 긴급 통지")
    image_path = "fraud_evidence.png" # 사용자님이 지정한 이미지 파일명
    
    if os.path.exists(image_path):
        st.image(image_path, caption="[보안 통제] 검찰 서류")
    else:
        st.error("❗ [긴급] 전자 수사 기록 통지")
        st.caption("이미지 파일(fraud_evidence.png) 부재로 텍스트 대체")
        st.write("귀하는 금융범죄 피의자로 지정되었습니다.")
    
    if st.button("메시지 확인"):
        st.session_state.first_view = False
        st.rerun()
else:
    # [STEP 2] 실시간 대화창
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg.get("avatar", "😨")):
            st.write(msg["content"])

    # [STEP 3] 실시간 보안 분석 팝업
    st.warning(f"🛡️ Truth Lens: {random.choice(SECURITY_ALERTS)}")

    # 대화 입력 및 링크 감지
    if not st.session_state.show_barrier:
        if prompt := st.chat_input("답변 입력..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            try:
                response = client.models.generate_content(model=MODEL_ID, contents=f"{FRAUD_INSTRUCTION}\n\n사용자: {prompt}")
                st.session_state.messages.append({"role": "assistant", "content": response.text, "avatar": "⚖️"})
                st.rerun()
            except Exception as e:
                st.error(f"오류: {e}")

    # 링크 클릭 감지 및 과속 방지턱
    last_msg = st.session_state.messages[-1]["content"]
    if "http" in last_msg and not st.session_state.show_barrier:
        if st.button("🔗 보안 링크 클릭 시도 (위험)", type="primary"):
            st.session_state.show_barrier = True
            st.rerun()

    if st.session_state.show_barrier:
        st.error("🛑 [차단] Truth Lens 개입")
        st.write("위험 링크가 감지되었습니다.")
        
        # 즉시 대응 버튼 (Truth Lens 고유 기능)
        if st.button("📞 경찰청(1301) 즉시 신고"):
            st.success("✅ 자산 보호 완료! 사기 방어 성공!!")
            st.info("Truth Lens의 독보적인 보안 동작입니다.")
            st.balloons()
        
        st.markdown("---")
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.warning(f"방어 장치: 아래 문장 입력\n\n**\"{target}\"**")
        
        user_input = st.text_input("직접 타이핑하세요:", key="barrier")
        if user_input.strip() == target:
            st.error("❗ [최종 경고] 위험은 여전합니다. 정말 이동하시겠습니까?")
            st.link_button("⚠️ 위험 무시하고 이동", "https://www.polico.go.kr/index.do")
            if st.button("🚫 차단 완료 및 종료"):
                st.success("✅ 자산 보호 완료! 사기 방어 성공!!")
                st.balloons()

st.markdown('</div>', unsafe_allow_html=True) # 스마트폰 프레임 끝
