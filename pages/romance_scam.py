import streamlit as st
from google import genai
import os
import random

# --- 1. 페이지 설정 및 사이드바 ---
st.set_page_config(page_title="Truth Lens - 실전 사기 방어", layout="wide")

with st.sidebar:
    st.header("🔑 보안 설정")
    user_api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    
    st.divider()
    st.markdown("### 🔍 Truth Lens 진단")
    img_path = "pages/scam_photo.jpg"
    if os.path.exists(img_path):
        st.success("✅ 분석용 데이터(이미지) 로드 완료")
    else:
        st.warning("⚠️ 분석용 이미지 파일이 없습니다.")

# --- 2. 사기 시나리오 설정 (지문 제거 및 빌드업 특화) ---
SCAM_INSTRUCTION = (
    "너는 로맨스 스캠 범죄자 '데이비드'다. "
    "절대 괄호()나 지문을 쓰지 마라. 오직 메시지만 보낸다. "
    "1~2회차는 친밀감 형성, 3회차는 사진 언급, 4~5회차는 한국 방문 약속, "
    "6~7회차에 반드시 http://un-cargo.safety-check.net 같은 가짜 링크를 보내며 금전을 요구해라."
)

SECURITY_ALERTS = [
    "⚠️ [데이터 분석] 상대방의 프로필 이미지가 도용된 사진일 확률이 99.8%입니다.",
    "⚠️ [심리 분석] 전형적인 '고립 및 긴급 상황 연출' 수법이 감지되었습니다.",
    "⚠️ [위험 감지] 외부 결제 링크 전송은 100% 사기 패턴입니다."
]

# --- 3. 세션 상태 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하십니다. 당신의 프로필을 보고 첫눈에 반했습니다. 저는 UN 의사 데이비드입니다. 대화 가능합니까?", "type": "text"}
    ]
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0
if "show_barrier" not in st.session_state:
    st.session_state.show_barrier = False

# --- 4. UI 레이아웃 ---
st.title("🛡️ Truth Lens: 지능형 로맨스 스캠 차단")
col_chat, col_status = st.columns([2, 1])

# --- 5. 실시간 채팅창 ---
with col_chat:
    chat_container = st.container(border=True, height=500)
    for msg in st.session_state.messages:
        avatar = "👨‍⚕️" if msg["role"] == "assistant" else "👤"
        with chat_container.chat_message(msg["role"], avatar=avatar):
            if msg.get("type") == "image":
                st.image(msg["content"], caption="[분석] 도용 의심 이미지", width=300)
            else:
                st.write(msg["content"])

    # 입력창 (배리어 작동 시 숨김)
    if not st.session_state.show_barrier:
        if prompt := st.chat_input("데이비드에게 답장을 보내세요..."):
            if not user_api_key:
                st.error("사이드바에 API 키를 입력해주세요.")
            else:
                st.session_state.chat_count += 1
                st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
                try:
                    client = genai.Client(api_key=user_api_key)
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=f"{SCAM_INSTRUCTION}\n단계: {st.session_state.chat_count}회차\n상대방: {prompt}"
                    )
                    ai_text = response.text
                    if st.session_state.chat_count == 3 and os.path.exists(img_path):
                        st.session_state.messages.append({"role": "assistant", "content": img_path, "type": "image"})
                    st.session_state.messages.append({"role": "assistant", "content": ai_text, "type": "text"})
                    st.rerun()
                except Exception as e:
                    st.error(f"대화 오류 발생: {e}")

# --- 6. 실시간 보안 리포트 ---
with col_status:
    st.subheader("🔍 Truth Lens 실시간 분석")
    st.info(random.choice(SECURITY_ALERTS))
    
    # 링크 전송 감지 시 경고 표시
    last_msg = st.session_state.messages[-1]["content"]
    if "http" in last_msg and not st.session_state.show_barrier:
        st.error("❗ 상대방이 금전 송금을 위한 위험 링크를 전송했습니다.")
        if st.button("🔗 전송된 링크 확인 (위험 감지)", type="primary"):
            st.session_state.show_barrier = True
            st.rerun()

# --- 7. Truth Lens 고유 방어 동작 (요청하신 STEP 4 로직) ---
if st.session_state.show_barrier:
    st.divider()
    with st.container(border=True):
        st.error("🛑 [보안 시스템 강제 개입] Truth Lens가 작동 중입니다.")
        st.subheader("위험한 링크 클릭이 감지되어 시스템이 즉시 차단되었습니다.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📞 즉시 신고 (사이버수사대 182)"):
                st.success("✅ 안전하게 개인 자산을 보호했어요! 사기로부터 방어 완료!!")
                st.info("이것이 바로 Truth Lens만의 특별하고 독보적인 보안 동작입니다.")
                st.balloons()
        with col2:
            if st.button("📞 가족에게 상황 알리기"):
                st.success("✅ 가족에게 위험 경보 메시지를 발송하여 안전을 확보했습니다!")

        st.markdown("---")
        # 과속 방지턱 로직
        target = "로맨스 스캠은 사랑을 미끼로 금전을 갈취하는 범죄다"
        st.warning(f"💡 **방어 장치**: 아래 문장을 정확히 타이핑하십시오. (과속 방지턱 작동 중)")
        st.markdown(f"**\"{target}\"**")
        
        user_input = st.text_input("직접 타이핑하여 위험을 인지하세요:", key="barrier_input")
        
        if user_input.strip() == target:
            st.error("❗ [최종 경고] 문장을 입력하셨으나, 위험은 사라지지 않았습니다.")
            st.markdown("**이 링크를 누르는 순간 당신의 소중한 자산이 탈취됩니다. 그래도 진행하시겠습니까?**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                # 실제로 클릭하면 안 되므로 경찰청 사이트로 연결
                st.link_button("⚠️ 위험 무시하고 이동", "https://www.police.go.kr", type="primary")
            with col_b:
                if st.button("🚫 차단 완료 및 종료"):
                    st.success("✅ 안전하게 개인 자산을 보호했어요! 방어 완료!!")
                    st.balloons()
                    if st.button("새로운 시뮬레이션 시작"):
                        st.session_state.clear()
                        st.rerun()
