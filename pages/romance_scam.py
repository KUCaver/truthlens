import streamlit as st
from google import genai
import os
import random
import time

# --- 1. API 및 클라이언트 설정 ---
# 사용자가 제공한 키 반영
API_KEY = "AIzaSyCTQRDuqx3xnc2NhkOcjpC375MfJ3MwGpo"
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.0-flash"

# --- 2. [프롬프트] 로맨스 스캠 빌드업 전략 ---
SCAM_INSTRUCTION = (
    "너는 '데이비드'라는 이름의 38세 영국인 정형외과 의사야. "
    "현재 예멘 UN 의료본부에 파견 중이며, 한국 여성(사용자)에게 의도적으로 접근한 로맨스 스캠범이야. "
    "전략: "
    "1. 초기(1~2회): '우연한 인연'을 강조하며 과도한 칭찬과 애정 공세를 펼쳐라. 말투는 번역기 느낌이 나야 함. "
    "2. 중기(3~4회): 신뢰를 위해 본인의 사진(파일경로 언급)을 보냈다고 말하며, 한국행 비행기표를 예약하겠다고 설득해라. "
    "3. 위기 및 링크: 갑자기 'UN 보안 계좌가 동결되어 비행기 관세가 필요하다'며 http://un-safety-check.com/pay 링크를 보내라. "
    "지문이나 설명 없이 실제 메시지만 보낼 것."
)

SECURITY_ALERTS = [
    "⚠️ [데이터 분석] 상대방의 프로필 이미지가 구글 이미지 검색 결과 42개의 가짜 계정에서 발견되었습니다.",
    "⚠️ [패턴 경고] 전형적인 '해외 파견 의사' 사칭 스크립트와 대화 내용이 95% 일치합니다.",
    "⚠️ [심리 분석] 상대방이 '긴급한 금전 필요' 상황을 설정하여 사용자의 판단력을 흐리고 있습니다.",
    "⚠️ [보안 차단] 수사기관 및 UN은 메신저를 통해 개인에게 관세를 요구하지 않습니다."
]

st.set_page_config(page_title="Truth Lens - 로맨스 스캠 방어", layout="centered")

# --- 3. 세션 상태 관리 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요, 아름다운 영혼을 가진 당신. 당신의 프로필이 내 마음을 두드렸습니다. 대화 가능할까요?", "type": "text"}
    ]
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0
if "show_barrier" not in st.session_state:
    st.session_state.show_barrier = False

st.title("🛡️ Truth Lens: 지능형 로맨스 스캠 차단")

# --- 4. 실시간 대화창 ---
chat_container = st.container(border=True, height=500)
with chat_container:
    for msg in st.session_state.messages:
        avatar = "👨‍⚕️" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            if msg.get("type") == "image":
                st.image(msg["content"], caption="[보안 통제] 데이비드가 보낸 사진", width=300)
            else:
                st.write(msg["content"])

# --- 5. 실시간 보안 분석 팝업 (첫 번째 코드 로직) ---
st.divider()
selected_alert = random.choice(SECURITY_ALERTS)
st.warning(f"🛡️ **Truth Lens 실시간 분석**: {selected_alert}")

# --- 6. 대화 입력 및 AI 응답 로직 ---
if not st.session_state.show_barrier:
    if prompt := st.chat_input("데이비드에게 답장하기..."):
        st.session_state.chat_count += 1
        st.session_state.messages.append({"role": "user", "content": prompt, "type": "text"})
        
        try:
            # AI 응답 생성
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=f"{SCAM_INSTRUCTION}\n단계: {st.session_state.chat_count}회\n사용자: {prompt}"
            )
            ai_text = response.text

            # 대화 3회차에 이미지 강제 삽입 (두 번째 코드 로직 반영)
            if st.session_state.chat_count == 3:
                img_path = "pages/scam_photo.jpg"
                if os.path.exists(img_path):
                    st.session_state.messages.append({"role": "assistant", "content": img_path, "type": "image"})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "[이미지 전송: 데이비드의 의사 가운 입은 사진]", "type": "text"})

            st.session_state.messages.append({"role": "assistant", "content": ai_text, "type": "text"})
            st.rerun()
            
        except Exception as e:
            st.error(f"대화 오류: {e}")

# --- 7. [핵심] 링크 감지 및 방어 동작 (빌드업의 정점) ---
last_msg = st.session_state.messages[-1]["content"]
if "http" in last_msg and not st.session_state.show_barrier:
    st.error("❗ 상대방이 금전 결제를 유도하는 외부 링크를 전송했습니다.")
    if st.button("🔗 링크 확인 및 안전 검사", type="primary"):
        st.session_state.show_barrier = True
        st.rerun()

if st.session_state.show_barrier:
    st.divider()
    with st.container(border=True):
        st.error("🛑 [위험 차단] Truth Lens가 피싱 사이트 접속을 중단시켰습니다.")
        st.subheader("로맨스 스캠의 전형적인 '금전 갈취' 단계입니다.")
        
        # 교육적 방어 기제: 타이핑 확인
        target = "온라인에서 만난 외국인은 어떤 이유로든 금전을 요구하지 않는다"
        st.warning(f"💡 **인지 기능 확인**: 아래 문장을 입력하여 사고력을 회복하십시오.")
        st.markdown(f"**\"{target}\"**")
        
        user_input = st.text_input("직접 입력하십시오:", key="barrier_input")
        
        if user_input.strip() == target:
            st.success("✅ 안전 의식이 확인되었습니다. 자산 보호 성공!")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📞 112 사이버 수사대 신고"):
                    st.balloons()
                    st.success("사기꾼의 IP와 대화 내역이 경찰청에 전달되었습니다.")
            with col_b:
                if st.button("🚫 이 사용자 차단하기"):
                    st.info("차단 완료. 더 이상 이 범죄자와 대화할 수 없습니다.")
