import streamlit as st
from google import genai
import os
import random

# --- 1. 페이지 설정 및 사이드바 ---
st.set_page_config(page_title="Truth Lens - 로맨스 스캠 방어", layout="wide")

with st.sidebar:
    st.header("🔑 보안 설정")
    user_api_key = st.text_input("Gemini API Key를 입력하세요", type="password", help="Google AI Studio에서 발급받은 키를 넣어주세요.")
    st.info("💡 키가 없으시다면 [Google AI Studio](https://aistudio.google.com/)에서 무료로 발급 가능합니다.")
    
    st.divider()
    st.markdown("### 🔍 Truth Lens 상태")
    if user_api_key:
        st.success("API 연결 준비 완료")
    else:
        st.warning("API 키 대기 중...")

# --- 2. 사기 시나리오 설정 ---
SCAM_INSTRUCTION = (
    "너는 '데이비드'라는 로맨스 스캠범이야. 영국 정형외과 의사이며 예멘 UN 파견 중이라고 속여라. "
    "1. 매우 다정하고 운명적인 사랑을 연기할 것. 2. 번역기 말투 사용. "
    "3. 대화 3회차에 사진 전송 언급. 4. 4회차 이후 송금 링크 전송."
)

SECURITY_ALERTS = [
    "⚠️ [위험] 상대방의 IP 주소가 동남아시아 기반의 사기 콜센터로 추적되었습니다.",
    "⚠️ [경고] 사용 중인 이미지는 해외 소셜 미디어에서 도용된 사진입니다.",
    "⚠️ [분석] 대화 패턴이 전형적인 금전 갈취 알고리즘과 일치합니다."
]

# --- 3. 세션 상태 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "내 소중한 인연... 당신을 찾기 위해 평생을 기다린 것 같습니다. 저는 영국 의사 데이비드입니다. 🌹", "type": "text"}
    ]
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0
if "show_barrier" not in st.session_state:
    st.session_state.show_barrier = False

# --- 4. 메인 화면 레이아웃 ---
st.title("🛡️ Truth Lens: 지능형 로맨스 스캠 차단")
col_chat, col_status = st.columns([2, 1])

# --- 5. 채팅 시스템 및 예외 처리 ---
with col_chat:
    chat_container = st.container(border=True, height=500)
    
    # 메시지 표시 루프
    for msg in st.session_state.messages:
        with chat_container.chat_message(msg["role"]):
            if msg.get("type") == "image":
                st.image(msg["content"], caption="[보안 감지] 도용 의심 이미지", width=250)
            else:
                st.write(msg["content"])

    # 입력창
    if prompt := st.chat_input("메시지를 입력하세요..."):
        if not user_api_key:
            st.error("❗ 왼쪽 사이드바에 API 키를 먼저 입력해주세요!")
        else:
            st.session_state.chat_count += 1
            st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
            
            try:
                # 클라이언트 생성 및 응답 호출
                client = genai.Client(api_key=user_api_key)
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=f"{SCAM_INSTRUCTION}\n단계: {st.session_state.chat_count}회\n유저: {prompt}"
                )
                ai_text = response.text

                # 사진 전송 이벤트
                if st.session_state.chat_count == 3:
                    # 실제 파일이 없을 경우를 대비한 Fallback 문구
                    img_path = "pages/scam_photo.jpg"
                    if os.path.exists(img_path):
                        st.session_state.messages.append({"role": "assistant", "content": img_path, "type": "image"})
                    else:
                        ai_text += "\n\n(방금 제 사진을 보냈는데 확인해 보셨나요?)"

                st.session_state.messages.append({"role": "assistant", "content": ai_text, "type": "text"})
                st.rerun()
                
            except Exception as e:
                # API 키 오류(403 등) 발생 시 사용자에게 친절하게 안내
                error_msg = str(e)
                if "403" in error_msg:
                    st.error("🚫 입력하신 API 키가 유효하지 않거나 유출되어 차단되었습니다. 새로운 키를 입력해주세요.")
                else:
                    st.error(f"⚠️ 통신 중 오류가 발생했습니다: {error_msg}")

# --- 6. 분석 및 차단 시스템 ---
with col_status:
    st.subheader("🔍 실시간 보안 리포트")
    st.info(random.choice(SECURITY_ALERTS))
    
    # 링크 전송 감지 시 차단 화면 가동
    last_msg = st.session_state.messages[-1]["content"]
    if "http" in last_msg or "link" in last_msg.lower():
        st.error("🚨 금전 관련 링크가 감지되었습니다!")
        if st.button("차단 시스템 작동", type="primary"):
            st.session_state.show_barrier = True

if st.session_state.show_barrier:
    st.divider()
    st.error("🛑 [Truth Lens Alert] 사기 범죄의 최종 단계인 '송금 유도'가 확인되었습니다.")
    
    # 인지 강화 퀴즈 (Speed Bump)
    st.markdown("### ⚠️ 자산 보호를 위한 인지 확인")
    target_sentence = "모르는 외국인에게 돈을 보내는 것은 100% 사기다"
    st.write(f"다음 문장을 똑같이 입력하여 이성적 판단을 유지하세요: **\"{target_sentence}\"**")
    
    confirm_input = st.text_input("여기에 입력:")
    if confirm_input == target_sentence:
        st.success("✅ 인지 확인 완료. 대화를 강제 종료하고 상대방을 차단합니다.")
        st.balloons()
        if st.button("시뮬레이션 종료 및 기록 삭제"):
            st.session_state.clear()
            st.rerun()
