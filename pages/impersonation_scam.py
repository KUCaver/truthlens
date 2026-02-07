import streamlit as st
from google import genai
import os
import random

# --- 1. API 및 클라이언트 설정 ---
API_KEY = "AIzaSyDH-4lwnsiRzQkWNd02AAk_xlBf4Slr41k"
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.0-flash" 

# --- 2. 스마트폰 다크 모드 UI 설정 (CSS) ---
st.set_page_config(page_title="Truth Lens - 실시간 자산 보호", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    
    /* 스마트폰 본체 프레임 */
    .phone-frame {
        border: 10px solid #2d2d2d;
        border-radius: 45px;
        width: 380px;
        height: 820px;
        margin: auto;
        background-color: #161b22;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        position: relative;
        box-shadow: 0 25px 50px rgba(0,0,0,0.6);
    }

    /* 상단 노치 영역 */
    .phone-notch {
        width: 140px;
        height: 22px;
        background: #2d2d2d;
        border-bottom-left-radius: 15px;
        border-bottom-right-radius: 15px;
        position: absolute;
        top: 0; left: 50%;
        transform: translateX(-50%);
        z-index: 100;
    }

    /* 폰 내부 스크롤 영역 */
    .phone-screen {
        padding: 45px 15px 25px 15px;
        height: 100%;
        overflow-y: auto;
        scrollbar-width: none;
    }
    .phone-screen::-webkit-scrollbar { display: none; }

    /* 대화창 다크 테마 커스텀 */
    [data-testid="stChatMessage"] {
        background-color: #21262d !important;
        border: 1px solid #30363d;
        border-radius: 15px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 시스템 설정 데이터 ---
FRAUD_INSTRUCTION = (
    "너는 서울중앙지검 김민수 수사관을 사칭하는 보이스피싱범이야. "
    "실제 문자를 보내는 것처럼 딱딱하고 위협적으로 말해. 지문이나 (괄호) 설명은 절대 쓰지 마. "
    "혐의를 나열하며 압박하다가 결국 보안 앱 링크(http://bit.ly/secure-app)를 전송해."
)

SECURITY_ALERTS = [
    "⚠️ [분석 결과] 현재 대화 패턴이 전형적인 '검찰 사칭' 수법과 98.7% 일치합니다.",
    "⚠️ [위험 감지] 상대방이 '구속', '수사 기밀' 등 공포감을 조성하는 단어를 반복 사용 중입니다.",
    "⚠️ [패턴 분석] 수사 기관은 메신저로 보안 앱 설치를 요구하지 않습니다.",
    "⚠️ [보안 경고] 상대방이 외부 링크 클릭을 유도하기 위해 심리적 지배를 시도하고 있습니다."
]

# --- 4. 세션 상태 관리 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "서울중앙지검 김민수 수사관입니다. 귀하의 명의가 대규모 금융 범죄에 연루되었습니다.", "avatar": "⚖️"}
    ]
if "first_view" not in st.session_state:
    st.session_state.first_view = True
if "show_barrier" not in st.session_state:
    st.session_state.show_barrier = False

# --- 5. 스마트폰 화면 렌더링 시작 ---
st.markdown('<div class="phone-frame"><div class="phone-notch"></div><div class="phone-screen">', unsafe_allow_html=True)

# [Step 1] 첫 화면: 이미지 또는 TXT 공고문
if st.session_state.first_view:
    st.subheader("⚖️ 긴급 수사 통지")
    image_path = "fraud_evidence.png" # 깃허브에 올릴 이미지 파일 이름
    
    if os.path.exists(image_path):
        st.image(image_path, caption="검찰 수사관 신분증 및 통지서")
    else:
        st.error("❗ [긴급] 전자 기록물 열람 안내")
        st.markdown(f"이미지 파일({image_path}) 부재로 텍스트 통지서가 대체 전송되었습니다.")
        st.caption("귀하는 현재 금융 범죄 피의자로 지정되었습니다.")

    if st.button("내용 확인 및 대응 시작"):
        st.session_state.first_view = False
        st.rerun()
else:
    # [Step 2] 실시간 대화창
    for msg in st.session_state.messages:
        avatar = "⚖️" if msg["role"] == "assistant" else "😨"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

    # [Step 3] 상시 보안 분석 팝업
    st.warning(f"🛡️ Truth Lens 분석: {random.choice(SECURITY_ALERTS)}")

    # 대화 입력 로직
    if not st.session_state.show_barrier:
        user_reply = st.text_input("답장 입력...", key="phone_input")
        if st.button("전송"):
            st.session_state.messages.append({"role": "user", "content": user_reply})
            try:
                response = client.models.generate_content(model=MODEL_ID, contents=f"{FRAUD_INSTRUCTION}\n\n사용자: {user_reply}")
                st.session_state.messages.append({"role": "assistant", "content": response.text, "avatar": "⚖️"})
                st.rerun()
            except Exception as e:
                st.error(f"대화 오류: {e}")

    # [Step 4] 링크 감지 및 강력 차단 로직 (과속 방지턱)
    last_msg = st.session_state.messages[-1]["content"]
    if "http" in last_msg and not st.session_state.show_barrier:
        st.error("❗ 악성 링크가 감지되었습니다.")
        if st.button("🔗 보안 링크 클릭 시도 (위험)", type="primary"):
            st.session_state.show_barrier = True
            st.rerun()

    if st.session_state.show_barrier:
        st.markdown("---")
        st.error("🛑 [보안 개입] Truth Lens가 작동 중입니다.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📞 1301 즉시 신고"):
                st.success("✅ 자산 보호 완료! 사기 방어 성공!!")
                st.info("이것은 Truth Lens만의 독보적 기술입니다.")
                st.balloons()
        
        st.markdown("---")
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.warning(f"💡 방어 장치: 아래 문장 입력\n\n**{target}**")
        
        user_input = st.text_input("타이핑 하세요:", key="barrier_final")
        
        if user_input.strip() == target:
            st.error("❗ [최종 경고] 위험은 여전합니다. 정말 이동하시겠습니까?")
            st.link_button("⚠️ 위험 무시하고 이동", "https://www.polico.go.kr/index.do")
            if st.button("🚫 차단 완료 및 종료"):
                st.success("✅ 안전하게 개인 자산을 보호했어요! 사기로부터 방어 완료!!")
                st.info("이것이 바로 Truth Lens만의 특별하고 독보적인 보안 동작입니다.")
                st.balloons()
                if st.button("다시 시작"):
                    st.session_state.clear()
                    st.rerun()

st.markdown('</div></div>', unsafe_allow_html=True) # 스마트폰 프레임 끝
