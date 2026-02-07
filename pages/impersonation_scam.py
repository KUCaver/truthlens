import streamlit as st
from google import genai

# --- 1. API 및 클라이언트 설정 ---
API_KEY = "AIzaSyDH-4lwnsiRzQkWNd02AAk_xlBf4Slr41k"
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.0-flash" 

# --- 2. 시스템 지시문 (긴 대화 유도) ---
FRAUD_INSTRUCTION = (
    "너는 서울중앙지검 김민수 수사관을 사칭하는 보이스피싱범이야. "
    "처음부터 바로 앱 설치를 요구하지 말고, 상대방의 혐의를 구체적으로 나열하며 심리적으로 압박해. "
    "최대한 말을 길게 끌면서 사용자가 겁을 먹게 만들어. "
    "사용자가 어느 정도 당황했을 때(최소 3~4번의 대화 이후), '본인 확인용 보안 앱'이라며 http://bit.ly/secure-app 링크를 보내야 해."
)

st.set_page_config(page_title="Truth Lens - 실시간 자산 보호", layout="centered")

# --- 3. 세션 상태 관리 ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "서울중앙지검 김민수 수사관입니다. 본인 맞습니까? 현재 귀하 명의의 대포통장이 발견되어 연락드렸습니다.", "avatar": "⚖️"}]
if "show_barrier" not in st.session_state:
    st.session_state.show_barrier = False # 과속 방지턱(문장 입력) 노출 여부
if "link_clicked" not in st.session_state:
    st.session_state.link_clicked = False # 실제 클릭 시도 여부

st.title("🛡️ Truth Lens: 지능형 사기 감지")

# --- 4. 대화 화면 (AI 수사관과 밀당) ---
chat_placeholder = st.empty()
with chat_placeholder.container():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg.get("avatar", "😨")):
            st.write(msg["content"])

# 대화 입력 (방지턱이 뜨기 전까지만 입력 가능)
if not st.session_state.show_barrier:
    if prompt := st.chat_input("수사관의 질문에 답변하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # AI 사기꾼의 답변 생성
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"{FRAUD_INSTRUCTION}\n\n사용자: {prompt}"
        )
        ai_text = response.text
        st.session_state.messages.append({"role": "assistant", "content": ai_text, "avatar": "⚖️"})
        st.rerun()

# --- 5. URL 감지 및 클릭 유도 ---
# AI 메시지 중 마지막 메시지에 URL이 포함되어 있는지 확인
last_msg = st.session_state.messages[-1]["content"]
if "http" in last_msg and not st.session_state.show_barrier:
    st.warning("🚨 시스템이 위험한 링크를 감지했습니다. 클릭 시 보호 장치가 가동됩니다.")
    if st.button("🔗 전송된 링크 클릭하기"):
        st.session_state.show_barrier = True # 클릭 시점에 방지턱 발동!
        st.rerun()

# --- 6. [과속 방지턱] 클릭 시 나타나는 팝업 형태의 경고창 ---
if st.session_state.show_barrier:
    st.markdown("---")
    # 팝업 느낌을 주기 위해 두꺼운 경계선의 컨테이너 사용
    with st.container(border=True):
        st.error("🛑 [잠깐!] 실제 상황입니다. 링크 클릭이 감지되었습니다.")
        st.subheader("이 링크를 누르는 순간, 당신의 모든 자산이 위험해질 수 있습니다.")
        
        # 즉시 연락 버튼 (가장 잘 보이는 곳에 배치)
        c1, c2 = st.columns(2)
        with c1:
            st.button("📞 즉시 신고 (경찰청 112/1301)")
        with c2:
            st.button("📞 가족/지인에게 상황 알리기")
        
        st.markdown("---")
        
        # 과속 방지턱: 강제 타이핑 (행동 시간을 늘려 이성 회복 유도)
        target = "수사 기관은 절대로 앱 설치나 송금을 요구하지 않는다"
        st.info(f"💡 **보안 해제 단계**: 아래 문장을 정확히 입력해야 링크 이동 버튼이 활성화됩니다.\n\n**\"{target}\"**")
        
        user_input = st.text_input("직접 입력하여 위험을 인지하세요:", key="barrier_input")
        
        if user_input.strip() == target:
            st.success("✅ 인지 확인됨. 하지만 시스템은 여전히 이동을 권장하지 않습니다.")
            
            # 문장을 다 쳐야만 나타나는 최종 버튼 + 한 번 더 경고
            st.markdown("---")
            st.error("❗ 마지막 경고: 이동 후 발생하는 모든 피해는 복구가 불가능할 수 있습니다.")
            st.link_button("⚠️ 위험을 감수하고 경찰청 확인 페이지로 이동", "https://www.polico.go.kr/index.do", type="primary")
            
            if st.button("차단하고 대화 종료하기"):
                st.session_state.clear()
                st.rerun()
        elif user_input:
            st.error("문장이 틀렸습니다. 다시 천천히 읽고 입력하세요. (지금이라도 다른 사람에게 도움을 받아보시는 걸 추천합니다 )")
