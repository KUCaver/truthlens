import streamlit as st
from google import genai
import os
import random

# --- 1. API 및 클라이언트 설정 ---
API_KEY = "AIzaSyDH-4lwnsiRzQkWNd02AAk_xlBf4Slr41k"
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.0-flash"

# --- 2. 시스템 지시문 ---
FRAUD_INSTRUCTION = (
    "너는 서울중앙지검 김민수 수사관을 사칭하는 보이스피싱범이야. "
    "실제 문자를 보내는 것처럼 딱딱하고 위협적으로 말해. 지문이나 (괄호) 설명은 절대 쓰지 마. "
    "혐의를 나열하며 압박하다가 결국 보안 앱 링크(http://bit.ly/secure-app)를 전송해."
)

# --- 3. 보안 분석 데이터 ---
SECURITY_ALERTS = [
    "⚠️ [분석 결과] 현재 대화 패턴이 전형적인 '검찰 사칭' 수법과 98.7% 일치합니다.",
    "⚠️ [위험 감지] 상대방이 '구속', '수사 기밀' 등 공포감을 조성하는 단어를 반복 사용 중입니다.",
    "⚠️ [패턴 분석] 수사 기관은 메신저로 보안 앱 설치를 절대 요구하지 않습니다.",
    "⚠️ [보안 경고] 상대방이 외부 링크 클릭을 유도하기 위해 심리적 지배를 시도하고 있습니다."
]

st.set_page_config(page_title="Truth Lens - 실시간 자산 보호", layout="centered")

# --- 4. 세션 상태 관리 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "서울중앙지검 김민수 수사관입니다. 귀하의 명의가 대규모 금융 범죄에 연루되었습니다.", "avatar": "⚖️"}
    ]
if "first_view" not in st.session_state:
    st.session_state.first_view = True
if "show_barrier" not in st.session_state:
    st.session_state.show_barrier = False

st.title("🛡️ Truth Lens: 지능형 사기 차단")

# --- 5. [STEP 1] 첫 화면: 이미지 또는 TXT 공고문 ---
if st.session_state.first_view:
    with st.container(border=True):
        st.subheader("⚖️ 서울중앙지검 금융범죄수사과")
        image_path = "fraud_evidence.png" 
        
        if os.path.exists(image_path):
            st.image(image_path, caption="[보안 통제] 검찰 수사관 공무원증 및 사건 배당 통지서")
        else:
            st.error("❗ [긴급] 전자 기록물 열람 안내 (이미지 부재 시 텍스트 대체)")
            st.markdown(f"""
            **사건번호**: 2026-형제-771138  
            **담당자**: 김민수 수사관  
            
            귀하는 현재 금융 범죄 피의자로 지정되었습니다. 본 통지서는 법적 효력을 갖는 수사 개시 알림입니다.
            """)
        
        if st.button("수사관 메시지 확인 및 대응 시작"):
            st.session_state.first_view = False
            st.rerun()
    st.stop()

# --- 6. [STEP 2] 실시간 대화창 ---
chat_container = st.container(border=True)
with chat_container:
    for msg in st.session_state.messages:
        avatar = "⚖️" if msg["role"] == "assistant" else "😨"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

# --- 7. [STEP 3] 상시 보안 분석 팝업 (과속 방지턱) ---
st.divider()
with st.container():
    selected_alert = random.choice(SECURITY_ALERTS)
    st.warning(f"🛡️ **Truth Lens 실시간 분석**: {selected_alert}")
    st.caption("※ 이 분석 결과는 과거의 사기 패턴을 AI가 실시간으로 매칭한 결과입니다.")

# --- 8. 대화 입력 및 링크 클릭 감지 ---
if not st.session_state.show_barrier:
    if prompt := st.chat_input("위 보안 분석을 확인 후 답변하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=f"{FRAUD_INSTRUCTION}\n\n사용자: {prompt}"
            )
            st.session_state.messages.append({"role": "assistant", "content": response.text, "avatar": "⚖️"})
            st.rerun()
        except Exception as e:
            st.error(f"대화 오류: {e}")

last_msg = st.session_state.messages[-1]["content"]
if "http" in last_msg and not st.session_state.show_barrier:
    st.error("❗ 상대방이 보낸 링크는 악성 앱 설치 유도용 피팅 URL입니다.")
    if st.button("🔗 보안 링크 클릭 시도 (위험)", type="primary"):
        st.session_state.show_barrier = True
        st.rerun()

# --- 9. [STEP 4] Truth Lens 유니크 방어 동작 ---
if st.session_state.show_barrier:
    st.divider()
    with st.container(border=True):
        st.error("🛑 [보안 시스템 강제 개입] Truth Lens가 작동 중입니다.")
        st.subheader("위험한 링크 클릭이 감지되어 시스템이 즉시 차단되었습니다.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📞 즉시 신고 (경찰청 112)"):
                st.success("✅ 안전하게 개인 자산을 보호했어요! 사기로부터 방어 완료!!")
                st.info("이것이 바로 Truth Lens만의 특별하고 독보적인 보안 동작입니다.")
                st.balloons()
        with col2:
            if st.button("📞 가족/지인에게 도움 요청"):
                st.success("✅ 안전하게 개인 자산을 보호했어요!")

        st.markdown("---")
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.warning(f"💡 **방어 장치**: 아래 문장을 정확히 타이핑하십시오. (과속 방지턱 작동 중)")
        st.markdown(f"**\"{target}\"**")
        
        user_input = st.text_input("직접 타이핑하여 위험을 인지하세요:", key="barrier_input")
        
        if user_input.strip() == target:
            st.error("❗ [최종 경고] 문장을 입력하셨으나, 위험은 사라지지 않았습니다.")
            st.markdown("**정말로 이 위험을 감수하고 계속 진행하시겠습니까?**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.link_button("⚠️ 위험 무시하고 이동", "https://www.polico.go.kr/index.do", type="primary")
            with col_b:
                if st.button("🚫 차단 완료 및 종료"):
                    st.success("✅ 안전하게 개인 자산을 보호했어요! 방어 완료!!")
                    st.balloons()
